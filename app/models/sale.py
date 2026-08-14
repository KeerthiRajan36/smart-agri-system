from sqlalchemy import Column, Integer, Float, Date, ForeignKey, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import TimestampMixin
from app.models.enums import PaymentStatus


class Sale(Base, TimestampMixin):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    harvest_id = Column(Integer, ForeignKey("harvests.id"), nullable=False)
    buyer_name = Column(String(150), nullable=False)
    quantity = Column(Float, nullable=False)
    price_per_unit = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    sale_date = Column(Date, nullable=False)
    payment_status = Column(SAEnum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)

    harvest = relationship("Harvest", back_populates="sales")
