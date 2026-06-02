"""Subdomain discovery via crt.sh and DNS resolution."""

from __future__ import annotations

import logging
from typing import Any

import dns.resolver
import httpx

from app.worker.utils import extract_domain

logger = logging.getLogger(__name__)

CRT_SH_URL = "https://crt.sh/?q=%.{domain}&output=json"
DNS_TIMEOUT_S = 5.0


def _fetch_crt_sh_subdomains(domain: str) -> set[str]:
    url = CRT_SH_URL.format(domain=domain)
    with httpx.Client(timeout=90.0) as client:
        resp = client.get(url)
        resp.raise_for_status()
        entries = resp.json()
        if not isinstance(entries, list):
            logger.warning("crt.sh returned unexpected payload for %s", domain)
            return set()

    fqdns: set[str] = set()
    for entry in entries:
        name_value = entry.get("name_value", "")
        for raw in name_value.split("\n"):
            fqdn = raw.strip().lower().removeprefix("*.")
            if not fqdn or "*" in fqdn:
                continue
            if fqdn == domain or fqdn.endswith(f".{domain}"):
                fqdns.add(fqdn)
    return fqdns


def _resolve_subdomain(fqdn: str, resolver: dns.resolver.Resolver) -> tuple[str | None, bool]:
    try:
        answers = resolver.resolve(fqdn, "A")
        ips = [str(r) for r in answers]
        if ips:
            return ips[0], True
        return None, False
    except (
        dns.resolver.NXDOMAIN,
        dns.resolver.NoAnswer,
        dns.resolver.NoNameservers,
        dns.resolver.Timeout,
        dns.exception.DNSException,
    ):
        return None, False


def execute_subdomain_scan(domain: str) -> dict[str, Any]:
    """
    Discover subdomains from crt.sh, deduplicate, DNS-resolve each.

    Returns:
        subdomains: [{fqdn, ip, live}, ...]
        total_found: int
        total_live: int
    """
    domain = extract_domain(domain)
    fqdns = sorted(_fetch_crt_sh_subdomains(domain))

    resolver = dns.resolver.Resolver()
    resolver.lifetime = DNS_TIMEOUT_S

    subdomains: list[dict[str, Any]] = []
    live_count = 0

    for i, fqdn in enumerate(fqdns):
        ip, live = _resolve_subdomain(fqdn, resolver)
        if live:
            live_count += 1
        subdomains.append({
            "fqdn": fqdn,
            "ip": ip,
            "live": live,
        })
        if (i + 1) % 25 == 0:
            logger.info("Resolved %d/%d subdomains for %s", i + 1, len(fqdns), domain)

    return {
        "domain": domain,
        "subdomains": subdomains,
        "total_found": len(subdomains),
        "total_live": live_count,
    }
