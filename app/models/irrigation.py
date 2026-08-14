from sqlalchemy import Column, Integer, Float, Date, String, ForeignKey
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import TimestampMixin
from app.models.enums import IrrigationStatus


class Irrigation(Base, TimestampMixin):
    __tablename__ = "irrigations"

    id = Column(Integer, primary_key=True, index=True)
    field_id = Column(Integer, ForeignKey("fields.id"), nullable=False)
    irrigation_date = Column(Date, nullable=False)
    water_quantity = Column(Float, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    irrigation_status = Column(SAEnum(IrrigationStatus), nullable=False, default=IrrigationStatus.COMPLETED)
    remarks = Column(String(500), nullable=True)

    field = relationship("Field", back_populates="irrigations")
