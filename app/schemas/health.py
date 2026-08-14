from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.enums import HealthStatus, SeverityLevel


class HealthBase(BaseModel):
    crop_id: int
    inspection_date: date
    health_status: HealthStatus
    disease_name: Optional[str] = Field(None, max_length=150)
    severity: Optional[SeverityLevel] = None
    remarks: Optional[str] = Field(None, max_length=500)


class HealthCreate(HealthBase):
    pass


class HealthOut(HealthBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
