"""Port scan via python-nmap with NVD CVE enrichment."""

from __future__ import annotations

import logging
import time
from typing import Any

import httpx
import nmap

from app.worker.utils import extract_host_for_nmap

logger = logging.getLogger(__name__)

NVD_CVE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
SCAN_TIMEOUT_S = 120
NVD_REQUEST_DELAY_S = 0.65  # NVD unauthenticated rate limit ~5 req / 30s


def _fetch_cves_for_cpe(cpe: str, client: httpx.Client) -> list[dict[str, Any]]:
    if not cpe or not cpe.strip():
        return []
    try:
        time.sleep(NVD_REQUEST_DELAY_S)
        resp = client.get(NVD_CVE_URL, params={"keywordSearch": cpe.strip()})
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        logger.warning("NVD lookup failed for %s: %s", cpe, exc)
        return []

    cves: list[dict[str, Any]] = []
    for item in data.get("vulnerabilities", []):
        cve = item.get("cve", {})
        cve_id = cve.get("id")
        if not cve_id:
            continue

        descriptions = cve.get("descriptions", [])
        desc_en = next(
            (d.get("value") for d in descriptions if d.get("lang") == "en"),
            descriptions[0].get("value") if descriptions else "",
        )

        cvss_score = None
        severity = None
        metrics = cve.get("metrics", {})
        for metric_key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
            metric_list = metrics.get(metric_key, [])
            if metric_list:
                cvss_data = metric_list[0].get("cvssData", {})
                cvss_score = cvss_data.get("baseScore")
                severity = cvss_data.get("baseSeverity") or metric_list[0].get("baseSeverity")
                break

        cves.append({
            "id": cve_id,
            "description": desc_en,
            "cvss_score": cvss_score,
            "severity": severity,
        })
    return cves


def _parse_os_guess(scanner: nmap.PortScanner, host: str) -> str | None:
    if host not in scanner.all_hosts():
        return None
    host_data = scanner[host]
    osmatch = host_data.get("osmatch", [])
    if osmatch:
        return osmatch[0].get("name")
    osclass = host_data.get("osclass", [])
    if osclass:
        return osclass[0].get("osfamily") or osclass[0].get("vendor")
    return None


def _extract_ports(scanner: nmap.PortScanner, host: str) -> list[dict[str, Any]]:
    ports: list[dict[str, Any]] = []
    if host not in scanner.all_hosts():
        return ports

    for proto in scanner[host].all_protocols():
        port_dict = scanner[host][proto]
        for port_num in port_dict:
            info = port_dict[port_num]
            if info.get("state") != "open":
                continue
            cpe = info.get("cpe") or ""
            if isinstance(cpe, list):
                cpe = cpe[0] if cpe else ""
            service = info.get("name", "")
            version = info.get("version", "")
            if info.get("product"):
                product = info["product"]
                version = f"{product} {version}".strip() if version else product

            ports.append({
                "port": int(port_num),
                "state": info.get("state", "unknown"),
                "service": service,
                "version": version or None,
                "cpe": cpe or None,
                "cves": [],
            })
    return ports


def execute_port_scan(target: str) -> dict[str, Any]:
    """
    Run nmap -sV -sC on target (max ~120s), enrich open ports with NVD CVE data.

    Returns:
        ports: list of {port, state, service, version, cpe, cves}
        os_guess: str | None
        duration_s: float
        host: str
    """
    host = extract_host_for_nmap(target)
    start = time.monotonic()
    scanner = nmap.PortScanner()

    try:
        scanner.scan(
            hosts=host,
            arguments="-sV -sC -T4 --open --host-timeout 120s",
        )
    except nmap.PortScannerError as exc:
        elapsed = round(time.monotonic() - start, 2)
        if elapsed >= SCAN_TIMEOUT_S:
            raise TimeoutError(f"Port scan exceeded {SCAN_TIMEOUT_S}s") from exc
        raise

    elapsed = time.monotonic() - start
    if elapsed > SCAN_TIMEOUT_S:
        raise TimeoutError(f"Port scan exceeded {SCAN_TIMEOUT_S}s")

    ports = _extract_ports(scanner, host)
    os_guess = _parse_os_guess(scanner, host)

    nvd_deadline = start + SCAN_TIMEOUT_S
    with httpx.Client(timeout=30.0) as http_client:
        for entry in ports:
            if time.monotonic() >= nvd_deadline:
                logger.warning("Stopping NVD lookups due to scan time budget")
                break
            cpe = entry.get("cpe")
            if cpe:
                entry["cves"] = _fetch_cves_for_cpe(cpe, http_client)

    duration_s = round(time.monotonic() - start, 2)
    return {
        "host": host,
        "ports": ports,
        "os_guess": os_guess,
        "duration_s": duration_s,
    }
