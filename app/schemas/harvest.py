from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class HarvestBase(BaseModel):
    crop_id: int
    harvest_date: date
    quantity: float = Field(..., gt=0)
    unit: str = Field("kg", max_length=30)
    quality_grade: str = Field(..., max_length=20)
    storage_location: Optional[str] = Field(None, max_length=150)


class HarvestCreate(HarvestBase):
    pass


class HarvestOut(HarvestBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
