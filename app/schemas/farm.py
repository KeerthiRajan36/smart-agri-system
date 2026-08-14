from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.enums import FarmStatus


class FarmBase(BaseModel):
    farm_name: str = Field(..., min_length=2, max_length=150)
    location: str = Field(..., min_length=2, max_length=200)
    total_area: float = Field(..., gt=0)
    owner_name: str = Field(..., min_length=2, max_length=150)
    status: FarmStatus = FarmStatus.ACTIVE


class FarmCreate(FarmBase):
    pass


class FarmUpdate(BaseModel):
    farm_name: Optional[str] = Field(None, min_length=2, max_length=150)
    location: Optional[str] = Field(None, min_length=2, max_length=200)
    total_area: Optional[float] = Field(None, gt=0)
    owner_name: Optional[str] = Field(None, min_length=2, max_length=150)
    status: Optional[FarmStatus] = None


class FarmOut(FarmBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
