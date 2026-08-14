from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import TimestampMixin
from app.models.enums import CropStatus


class Crop(Base, TimestampMixin):
    __tablename__ = "crops"

    id = Column(Integer, primary_key=True, index=True)
    field_id = Column(Integer, ForeignKey("fields.id"), nullable=False)
    crop_name = Column(String(150), nullable=False, index=True)
    crop_type = Column(String(100), nullable=False)
    planting_date = Column(Date, nullable=False)
    expected_harvest_date = Column(Date, nullable=False)
    seed_quantity = Column(Float, nullable=False)
    status = Column(SAEnum(CropStatus), nullable=False, default=CropStatus.PLANNED)

    field = relationship("Field", back_populates="crops")
    treatments = relationship("CropTreatment", back_populates="crop", cascade="all, delete-orphan")
    health_records = relationship("CropHealth", back_populates="crop", cascade="all, delete-orphan")
    harvests = relationship("Harvest", back_populates="crop", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="crop", cascade="all, delete-orphan")
