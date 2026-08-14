from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, model_validator

from app.models.enums import CropStatus


class CropBase(BaseModel):
    crop_name: str = Field(..., min_length=2, max_length=150)
    crop_type: str = Field(..., min_length=2, max_length=100)
    planting_date: date
    expected_harvest_date: date
    seed_quantity: float = Field(..., gt=0)
    status: CropStatus = CropStatus.PLANNED

    @model_validator(mode="after")
    def validate_dates(self):
        if self.planting_date > self.expected_harvest_date:
            raise ValueError("planting_date cannot be after expected_harvest_date")
        return self


class CropCreate(CropBase):
    field_id: int


class CropUpdate(BaseModel):
    crop_name: Optional[str] = Field(None, min_length=2, max_length=150)
    crop_type: Optional[str] = Field(None, min_length=2, max_length=100)
    planting_date: Optional[date] = None
    expected_harvest_date: Optional[date] = None
    seed_quantity: Optional[float] = Field(None, gt=0)
    status: Optional[CropStatus] = None


class CropOut(CropBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    field_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
