from sqlalchemy import Column, Integer, Date, String, ForeignKey
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import TimestampMixin
from app.models.enums import HealthStatus, SeverityLevel


class CropHealth(Base, TimestampMixin):
    __tablename__ = "crop_health_records"

    id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=False)
    inspection_date = Column(Date, nullable=False)
    health_status = Column(SAEnum(HealthStatus), nullable=False)
    disease_name = Column(String(150), nullable=True)
    severity = Column(SAEnum(SeverityLevel), nullable=True)
    remarks = Column(String(500), nullable=True)

    crop = relationship("Crop", back_populates="health_records")
