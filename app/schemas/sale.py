from datetime import date, datetime
from pydantic import BaseModel, Field, ConfigDict

from app.models.enums import PaymentStatus


class SaleBase(BaseModel):
    harvest_id: int
    buyer_name: str = Field(..., min_length=2, max_length=150)
    quantity: float = Field(..., gt=0)
    price_per_unit: float = Field(..., gt=0)
    sale_date: date
    payment_status: PaymentStatus = PaymentStatus.PENDING


class SaleCreate(SaleBase):
    pass


class SaleOut(SaleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    total_amount: float
    created_at: datetime
