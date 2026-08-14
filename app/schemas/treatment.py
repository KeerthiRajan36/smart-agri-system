from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.enums import ProductType


class TreatmentBase(BaseModel):
    crop_id: int
    product_name: str = Field(..., min_length=2, max_length=150)
    product_type: ProductType
    quantity: float = Field(..., gt=0)
    applied_date: date
    cost: float = Field(..., gt=0)
    remarks: Optional[str] = Field(None, max_length=500)


class TreatmentCreate(TreatmentBase):
    pass


class TreatmentOut(TreatmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
