from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.enums import FieldStatus


class FieldBase(BaseModel):
    field_name: str = Field(..., min_length=2, max_length=150)
    area: float = Field(..., gt=0)
    soil_type: str = Field(..., min_length=2, max_length=100)
    irrigation_type: str = Field(..., min_length=2, max_length=100)
    status: FieldStatus = FieldStatus.ACTIVE


class FieldCreate(FieldBase):
    pass


class FieldUpdate(BaseModel):
    field_name: Optional[str] = Field(None, min_length=2, max_length=150)
    area: Optional[float] = Field(None, gt=0)
    soil_type: Optional[str] = None
    irrigation_type: Optional[str] = None
    status: Optional[FieldStatus] = None


class FieldOut(FieldBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    farm_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
