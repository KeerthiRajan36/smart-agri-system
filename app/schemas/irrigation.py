from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.enums import IrrigationStatus


class IrrigationBase(BaseModel):
    field_id: int
    irrigation_date: date
    water_quantity: float = Field(..., gt=0)
    duration_minutes: int = Field(..., gt=0)
    irrigation_status: IrrigationStatus = IrrigationStatus.COMPLETED
    remarks: Optional[str] = Field(None, max_length=500)


class IrrigationCreate(IrrigationBase):
    pass


class IrrigationOut(IrrigationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
