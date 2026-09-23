from typing import Optional
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    database: str
    details: Optional[str] = None


class ErrorResponse(BaseModel):
    detail: str
