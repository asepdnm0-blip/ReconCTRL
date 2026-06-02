import uuid
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


# --- Requests ---

class ScanCreate(BaseModel):
    target: str = Field(..., min_length=1, max_length=500, description="Target host, domain, IP, or CIDR")
    scan_type: str = Field(default="full", description="Scan type: full, port, whois, subdomain")
    modules: List[str] = Field(
        default=["port_scan", "header", "osint"],
        description=(
            "Modules: port_scan (nmap), subdomain, header, dir_enum, "
            "owasp, osint (whois), ai_summary. Aliases: nmap, whois"
        ),
    )


# --- Responses ---

class ScanModuleResponse(BaseModel):
    id: uuid.UUID
    module_name: str
    status: str
    progress: int
    result_data: Optional[dict] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ScanResponse(BaseModel):
    id: uuid.UUID
    target: str
    scan_type: str
    status: str
    progress: int
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    owner_id: uuid.UUID

    class Config:
        from_attributes = True


class ScanDetailResponse(ScanResponse):
    modules: List[ScanModuleResponse] = []
    results_summary: Optional[dict] = None


class ScanListResponse(BaseModel):
    items: List[ScanResponse]
    total: int
