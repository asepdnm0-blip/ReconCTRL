"""Module execution logic (called from Celery tasks and orchestrator)."""

from __future__ import annotations

import asyncio
import logging
import socket
from typing import Any
from urllib.parse import urljoin

import httpx
import whois

from app.config import settings
from app.models.scan import ModuleStatus
from app.worker import db as worker_db
from app.worker import events
from app.worker.modules.ai_summary import execute_ai_summary
from app.worker.modules.port_scan import execute_port_scan
from app.worker.modules.subdomain import execute_subdomain_scan
from app.worker.utils import (
    extract_domain,
    extract_host_for_nmap,
    load_dir_wordlist,
    normalize_url,
)

logger = logging.getLogger(__name__)

SECURITY_HEADERS = [
    "strict-transport-security",
    "content-security-policy",
    "x-frame-options",
    "x-content-type-options",
    "referrer-policy",
    "permissions-policy",
]


def _run_sync(coro):
    """Run async module from standalone Celery task (no outer event loop)."""
    return asyncio.run(coro)


# ---------------------------------------------------------------------------
# Port scan (nmap + NVD) — blocking, run in thread pool
# ---------------------------------------------------------------------------

async def run_port_scan_async(
    scan_id: str, target: str, module_name: str = "port_scan"
) -> dict[str, Any]:
    module = module_name
    host = extract_host_for_nmap(target)
    events.publish_module_start(scan_id, module, f"nmap -sV -sC on {host} (timeout 120s)")
    worker_db.set_module_status(scan_id, module, ModuleStatus.RUNNING, progress=10)

    try:
        events.publish_module_progress(scan_id, module, 25)
        result = await asyncio.to_thread(execute_port_scan, target)
        events.publish_module_progress(scan_id, module, 90, ports_open=len(result["ports"]))
        events.publish_module_complete(
            scan_id, module,
            {"ports_open": len(result["ports"]), "duration_s": result["duration_s"]},
        )
        worker_db.set_module_status(
            scan_id, module, ModuleStatus.COMPLETED,
            progress=100, result_data=result,
        )
        return result
    except Exception as exc:
        logger.exception("%s failed for %s", module, scan_id)
        events.publish_module_error(scan_id, module, str(exc))
        worker_db.set_module_status(
            scan_id, module, ModuleStatus.FAILED, error_message=str(exc),
        )
        raise


def run_port_scan(scan_id: str, target: str, module_name: str = "port_scan") -> dict[str, Any]:
    return _run_sync(run_port_scan_async(scan_id, target, module_name))


# ---------------------------------------------------------------------------
# Subdomain (crt.sh + DNS)
# ---------------------------------------------------------------------------

async def run_subdomain_async(
    scan_id: str, domain: str, module_name: str = "subdomain"
) -> dict[str, Any]:
    module = module_name
    events.publish_module_start(scan_id, module, f"crt.sh subdomain scan for {domain}")
    worker_db.set_module_status(scan_id, module, ModuleStatus.RUNNING, progress=10)

    try:
        events.publish_module_progress(scan_id, module, 30)
        result = await asyncio.to_thread(execute_subdomain_scan, domain)
        events.publish_module_progress(
            scan_id, module, 90,
            total_found=result["total_found"],
            total_live=result["total_live"],
        )
        events.publish_module_complete(
            scan_id, module,
            {"total_found": result["total_found"], "total_live": result["total_live"]},
        )
        worker_db.set_module_status(
            scan_id, module, ModuleStatus.COMPLETED,
            progress=100, result_data=result,
        )
        return result
    except Exception as exc:
        events.publish_module_error(scan_id, module_name, str(exc))
        worker_db.set_module_status(
            scan_id, module_name, ModuleStatus.FAILED, error_message=str(exc),
        )
        raise


def run_subdomain(scan_id: str, domain: str, module_name: str = "subdomain") -> dict[str, Any]:
    return _run_sync(run_subdomain_async(scan_id, domain, module_name))


# ---------------------------------------------------------------------------
# HTTP headers (httpx async)
# ---------------------------------------------------------------------------

async def run_header_async(
    scan_id: str, url: str, module_name: str = "header"
) -> dict[str, Any]:
    module = module_name
    url = normalize_url(url)
    events.publish_module_start(scan_id, module, f"Fetching headers for {url}")
    worker_db.set_module_status(scan_id, module, ModuleStatus.RUNNING, progress=10)

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        events.publish_module_progress(scan_id, module, 40)
        response = await client.get(url)
        headers = {k.lower(): v for k, v in response.headers.items()}

    result = {
        "url": str(response.url),
        "status_code": response.status_code,
        "headers": headers,
    }
    events.publish_module_progress(scan_id, module, 100)
    events.publish_module_complete(scan_id, module, {"status_code": response.status_code})
    worker_db.set_module_status(
        scan_id, module, ModuleStatus.COMPLETED,
        progress=100, result_data=result,
    )
    return result


def run_header(scan_id: str, url: str, module_name: str = "header") -> dict[str, Any]:
    return _run_sync(run_header_async(scan_id, url, module_name))


# ---------------------------------------------------------------------------
# Directory enumeration (httpx async)
# ---------------------------------------------------------------------------

async def run_dir_enum_async(
    scan_id: str, url: str, module_name: str = "dir_enum"
) -> dict[str, Any]:
    module = module_name
    base_url = normalize_url(url)
    paths = load_dir_wordlist()
    events.publish_module_start(scan_id, module, f"Directory enum on {base_url}")
    worker_db.set_module_status(scan_id, module, ModuleStatus.RUNNING, progress=5)

    found: list[dict[str, Any]] = []
    sem = asyncio.Semaphore(10)

    async def probe(path: str, client: httpx.AsyncClient) -> None:
        target = urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
        async with sem:
            try:
                resp = await client.get(target, follow_redirects=False)
                if resp.status_code < 400:
                    found.append({
                        "path": path,
                        "url": target,
                        "status_code": resp.status_code,
                        "content_length": resp.headers.get("content-length"),
                    })
            except httpx.HTTPError:
                pass

    async with httpx.AsyncClient(timeout=15.0) as client:
        tasks = []
        for i, path in enumerate(paths):
            tasks.append(probe(path, client))
            if len(tasks) >= 20:
                await asyncio.gather(*tasks)
                tasks.clear()
                pct = 5 + int((i / len(paths)) * 85)
                events.publish_module_progress(scan_id, module, pct, checked=i + 1)
        if tasks:
            await asyncio.gather(*tasks)

    result = {"base_url": base_url, "paths_checked": len(paths), "found": found}
    events.publish_module_progress(scan_id, module, 100)
    events.publish_module_complete(scan_id, module, {"found_count": len(found)})
    worker_db.set_module_status(
        scan_id, module, ModuleStatus.COMPLETED,
        progress=100, result_data=result,
    )
    return result


def run_dir_enum(scan_id: str, url: str, module_name: str = "dir_enum") -> dict[str, Any]:
    return _run_sync(run_dir_enum_async(scan_id, url, module_name))


# ---------------------------------------------------------------------------
# OWASP header checks (sync)
# ---------------------------------------------------------------------------

async def run_owasp_async(
    scan_id: str,
    headers_data: dict[str, Any] | None,
    module_name: str = "owasp",
) -> dict[str, Any]:
    module = module_name
    events.publish_module_start(scan_id, module, "OWASP security header analysis")
    worker_db.set_module_status(scan_id, module, ModuleStatus.RUNNING, progress=20)

    headers = (headers_data or {}).get("headers", {})
    if isinstance(headers_data, dict) and "headers" not in headers_data and headers_data:
        headers = {k.lower(): v for k, v in headers_data.items() if isinstance(k, str)}

    findings: list[dict[str, str]] = []
    for header in SECURITY_HEADERS:
        if header not in headers:
            findings.append({
                "severity": "medium",
                "check": f"missing_{header}",
                "message": f"Missing recommended header: {header}",
            })

    server = headers.get("server", "")
    if server and any(c.isdigit() for c in server):
        findings.append({
            "severity": "low",
            "check": "server_version_disclosure",
            "message": f"Server header may disclose version: {server}",
        })

    if "x-powered-by" in headers:
        findings.append({
            "severity": "low",
            "check": "x_powered_by",
            "message": f"X-Powered-By present: {headers['x-powered-by']}",
        })

    cookie = headers.get("set-cookie", "")
    if cookie and "secure" not in cookie.lower():
        findings.append({
            "severity": "medium",
            "check": "cookie_secure",
            "message": "Set-Cookie may be missing Secure flag",
        })

    score = max(0, 100 - len(findings) * 12)
    result = {
        "score": score,
        "findings": findings,
        "headers_analyzed": list(headers.keys()),
    }
    events.publish_module_progress(scan_id, module, 100, score=score)
    events.publish_module_complete(scan_id, module, {"findings_count": len(findings), "score": score})
    worker_db.set_module_status(
        scan_id, module, ModuleStatus.COMPLETED,
        progress=100, result_data=result,
    )
    return result


def run_owasp(
    scan_id: str,
    headers_data: dict[str, Any] | None,
    module_name: str = "owasp",
) -> dict[str, Any]:
    return _run_sync(run_owasp_async(scan_id, headers_data, module_name))


# ---------------------------------------------------------------------------
# OSINT (whois + ip-api)
# ---------------------------------------------------------------------------

async def run_osint_async(
    scan_id: str, domain: str, module_name: str = "osint"
) -> dict[str, Any]:
    module = module_name
    domain = extract_domain(domain)
    events.publish_module_start(scan_id, module, f"OSINT for {domain}")
    worker_db.set_module_status(scan_id, module, ModuleStatus.RUNNING, progress=10)

    whois_data: dict[str, Any] = {}
    try:
        w = await asyncio.to_thread(whois.whois, domain)
        whois_data = {
            "domain_name": w.domain_name,
            "registrar": w.registrar,
            "creation_date": str(w.creation_date),
            "expiration_date": str(w.expiration_date),
            "name_servers": w.name_servers,
            "emails": w.emails,
        }
    except Exception as exc:
        whois_data = {"error": str(exc)}

    events.publish_module_progress(scan_id, module, 50)

    ip_info: dict[str, Any] = {}
    try:
        ip = await asyncio.to_thread(socket.gethostbyname, domain)
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                f"http://ip-api.com/json/{ip}?fields=status,message,country,isp,org,as,query"
            )
            if resp.status_code == 200:
                ip_info = resp.json()
    except Exception as exc:
        ip_info = {"error": str(exc)}

    result = {"domain": domain, "whois": whois_data, "ip_info": ip_info}
    events.publish_module_progress(scan_id, module, 100)
    events.publish_module_complete(scan_id, module, {"has_whois": "error" not in whois_data})
    worker_db.set_module_status(
        scan_id, module, ModuleStatus.COMPLETED,
        progress=100, result_data=result,
    )
    return result


def run_osint(scan_id: str, domain: str, module_name: str = "osint") -> dict[str, Any]:
    return _run_sync(run_osint_async(scan_id, domain, module_name))


# ---------------------------------------------------------------------------
# AI summary (Anthropic SDK)
# ---------------------------------------------------------------------------

async def run_ai_summary_async(
    scan_id: str,
    all_results: dict[str, Any],
    module_name: str = "ai_summary",
) -> dict[str, Any]:
    module = module_name
    events.publish_module_start(scan_id, module, "Generating AI pentest summary")
    worker_db.set_module_status(scan_id, module, ModuleStatus.RUNNING, progress=15)

    if not settings.CLAUDE_API_KEY:
        result = {
            "summary": "Claude API key not configured (set CLAUDE_API_KEY).",
            "skipped": True,
        }
        events.publish_module_complete(scan_id, module, {"skipped": True})
        worker_db.set_module_status(
            scan_id, module, ModuleStatus.COMPLETED,
            progress=100, result_data=result,
        )
        return result

    events.publish_module_progress(scan_id, module, 40)
    summary_text = await asyncio.to_thread(execute_ai_summary, all_results)
    result = {"summary": summary_text, "model": settings.CLAUDE_MODEL}
    events.publish_module_progress(scan_id, module, 100)
    events.publish_module_complete(scan_id, module, {"chars": len(summary_text)})
    worker_db.set_module_status(
        scan_id, module, ModuleStatus.COMPLETED,
        progress=100, result_data=result,
    )
    return result


def run_ai_summary(
    scan_id: str,
    all_results: dict[str, Any],
    module_name: str = "ai_summary",
) -> dict[str, Any]:
    return _run_sync(run_ai_summary_async(scan_id, all_results, module_name))
