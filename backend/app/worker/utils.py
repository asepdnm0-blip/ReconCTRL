"""URL / domain helpers for scan modules."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

_WORDLIST_PATH = Path(__file__).parent / "data" / "dir_wordlist.txt"


def normalize_url(target: str) -> str:
    target = target.strip()
    if not target.startswith(("http://", "https://")):
        return f"https://{target}"
    return target


def extract_domain(target: str) -> str:
    url = normalize_url(target)
    host = urlparse(url).hostname or target
    return host.lower().removeprefix("www.")


def extract_host_for_nmap(target: str) -> str:
    domain = extract_domain(target)
    return domain.split("/")[0]


def load_dir_wordlist() -> list[str]:
    if _WORDLIST_PATH.is_file():
        lines = _WORDLIST_PATH.read_text(encoding="utf-8").splitlines()
        return [ln.strip() for ln in lines if ln.strip() and not ln.startswith("#")]
    return [
        "admin", "api", "backup", "config", "dashboard", "dev",
        "login", "robots.txt", "sitemap.xml", "static", "test", "uploads",
    ]


def resolve_module_alias(name: str) -> str:
    """Map API aliases to canonical module keys."""
    aliases = {
        "nmap": "port_scan",
        "whois": "osint",
        "headers": "header",
        "directory": "dir_enum",
        "ai": "ai_summary",
    }
    return aliases.get(name, name)
