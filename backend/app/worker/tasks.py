"""
Celery tasks: scan orchestrator and per-module workers.

Database access is synchronous (see app.worker.db). Async I/O for httpx
runs in isolated asyncio.run() per module to avoid event-loop conflicts.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from app.models.scan import ModuleStatus, ScanStatus
from app.worker import db as worker_db
from app.worker import events
from app.worker.celery_app import celery_app
from app.worker.module_runners import (
    run_ai_summary,
    run_dir_enum,
    run_header,
    run_osint,
    run_owasp,
    run_port_scan,
    run_subdomain,
    run_ai_summary_async,
    run_dir_enum_async,
    run_header_async,
    run_osint_async,
    run_owasp_async,
    run_port_scan_async,
    run_subdomain_async,
)
from app.worker.utils import extract_domain, normalize_url, resolve_module_alias

logger = logging.getLogger(__name__)

ASYNC_RUNNERS = {
    "port_scan": run_port_scan_async,
    "subdomain": run_subdomain_async,
    "header": run_header_async,
    "dir_enum": run_dir_enum_async,
    "owasp": run_owasp_async,
    "osint": run_osint_async,
    "ai_summary": run_ai_summary_async,
}


def _run_module_async(coro):
    """Fresh event loop per module — safe with sync SQLAlchemy in worker."""
    return asyncio.run(coro)


def _invoke_module(
    canonical: str,
    scan_id: str,
    module_name: str,
    target_url: str,
    accumulated: dict[str, Any],
) -> dict[str, Any] | None:
    domain = extract_domain(target_url)
    url = normalize_url(target_url)
    runner = ASYNC_RUNNERS.get(canonical)
    if runner is None:
        return None

    if canonical == "port_scan":
        return _run_module_async(runner(scan_id, target_url, module_name=module_name))
    if canonical == "subdomain":
        return _run_module_async(runner(scan_id, domain, module_name=module_name))
    if canonical == "header":
        return _run_module_async(runner(scan_id, url, module_name=module_name))
    if canonical == "dir_enum":
        return _run_module_async(runner(scan_id, url, module_name=module_name))
    if canonical == "owasp":
        header_result = accumulated.get("header") or accumulated.get("headers")
        for key, val in accumulated.items():
            if resolve_module_alias(key) == "header" and isinstance(val, dict):
                header_result = val
                break
        return _run_module_async(runner(scan_id, header_result, module_name=module_name))
    if canonical == "osint":
        return _run_module_async(runner(scan_id, domain, module_name=module_name))
    if canonical == "ai_summary":
        return _run_module_async(runner(scan_id, accumulated, module_name=module_name))
    return None


def _orchestrate(scan_id: str, target_url: str, modules_list: list[str]) -> dict[str, Any]:
    scan = worker_db.get_scan(scan_id)
    if scan is None:
        logger.error("Scan %s not found", scan_id)
        return {"error": "scan_not_found"}

    if not target_url:
        target_url = scan.target
    if not modules_list:
        modules_list = [m.module_name for m in scan.modules] or ["port_scan", "osint"]

    worker_db.set_scan_status(scan_id, ScanStatus.RUNNING, progress=0)
    events.publish_event(scan_id, "module_start", {
        "module": "orchestrator",
        "message": f"Scan started for {target_url}",
        "modules": modules_list,
    })

    accumulated: dict[str, Any] = {}
    total = len(modules_list)
    failed_modules: list[str] = []

    for index, module_name in enumerate(modules_list):
        canonical = resolve_module_alias(module_name)

        if canonical not in ASYNC_RUNNERS:
            msg = f"Unknown module: {module_name}"
            logger.warning(msg)
            events.publish_module_error(scan_id, module_name, msg)
            worker_db.set_module_status(
                scan_id, module_name, ModuleStatus.FAILED, error_message=msg,
            )
            failed_modules.append(module_name)
            continue

        try:
            result = _invoke_module(
                canonical, scan_id, module_name, target_url, accumulated,
            )
            if result is not None:
                accumulated[module_name] = result
                accumulated[canonical] = result
        except Exception as exc:
            logger.exception("Module %s failed for scan %s", module_name, scan_id)
            events.publish_module_error(scan_id, module_name, str(exc))
            worker_db.set_module_status(
                scan_id, module_name, ModuleStatus.FAILED, error_message=str(exc),
            )
            failed_modules.append(module_name)

        progress = int(((index + 1) / total) * 100)
        worker_db.set_scan_status(scan_id, ScanStatus.RUNNING, progress=progress)

    worker_db.set_scan_status(
        scan_id,
        ScanStatus.COMPLETED,
        progress=100,
        results_summary=accumulated,
    )
    events.publish_event(scan_id, "scan_complete", {
        "message": "All modules finished",
        "progress": 100,
        "failed_modules": failed_modules,
        "modules_completed": list(accumulated.keys()),
    })

    return {
        "scan_id": scan_id,
        "status": ScanStatus.COMPLETED.value,
        "results": accumulated,
        "failed_modules": failed_modules,
    }


# ---------------------------------------------------------------------------
# Module Celery tasks (standalone)
# ---------------------------------------------------------------------------

@celery_app.task(name="worker.tasks.port_scan_task", bind=True)
def port_scan_task(self, scan_id: str, target: str, module_name: str = "port_scan") -> dict[str, Any]:
    return run_port_scan(scan_id, target, module_name=module_name)


@celery_app.task(name="worker.tasks.subdomain_task", bind=True)
def subdomain_task(self, scan_id: str, domain: str, module_name: str = "subdomain") -> dict[str, Any]:
    return run_subdomain(scan_id, domain, module_name=module_name)


@celery_app.task(name="worker.tasks.header_task", bind=True)
def header_task(self, scan_id: str, url: str, module_name: str = "header") -> dict[str, Any]:
    return run_header(scan_id, url, module_name=module_name)


@celery_app.task(name="worker.tasks.dir_enum_task", bind=True)
def dir_enum_task(self, scan_id: str, url: str, module_name: str = "dir_enum") -> dict[str, Any]:
    return run_dir_enum(scan_id, url, module_name=module_name)


@celery_app.task(name="worker.tasks.owasp_task", bind=True)
def owasp_task(
    self,
    scan_id: str,
    headers_data: dict[str, Any] | None,
    module_name: str = "owasp",
) -> dict[str, Any]:
    return run_owasp(scan_id, headers_data, module_name=module_name)


@celery_app.task(name="worker.tasks.osint_task", bind=True)
def osint_task(self, scan_id: str, domain: str, module_name: str = "osint") -> dict[str, Any]:
    return run_osint(scan_id, domain, module_name=module_name)


@celery_app.task(name="worker.tasks.ai_summary_task", bind=True)
def ai_summary_task(
    self,
    scan_id: str,
    all_results: dict[str, Any],
    module_name: str = "ai_summary",
) -> dict[str, Any]:
    return run_ai_summary(scan_id, all_results, module_name=module_name)


@celery_app.task(name="worker.tasks.scan_task", bind=True)
def scan_task(
    self,
    scan_id: str,
    target_url: str | None = None,
    modules_list: list[str] | None = None,
) -> dict[str, Any]:
    """Orchestrate scan modules (sync DB + isolated asyncio per module)."""
    logger.info(
        "scan_task scan_id=%s target=%s modules=%s",
        scan_id, target_url, modules_list,
    )

    if target_url is None or modules_list is None:
        scan = worker_db.get_scan(scan_id)
        if scan is None:
            return {"error": "scan_not_found"}
        if target_url is None:
            target_url = scan.target
        if modules_list is None:
            modules_list = [m.module_name for m in scan.modules]

    return _orchestrate(scan_id, target_url, modules_list)
