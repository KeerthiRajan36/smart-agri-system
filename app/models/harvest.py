from sqlalchemy import Column, Integer, Float, Date, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import TimestampMixin


class Harvest(Base, TimestampMixin):
    __tablename__ = "harvests"

    id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=False)
    harvest_date = Column(Date, nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String(30), nullable=False, default="kg")
    quality_grade = Column(String(20), nullable=False)
    storage_location = Column(String(150), nullable=True)

    crop = relationship("Crop", back_populates="harvests")
    sales = relationship("Sale", back_populates="harvest", cascade="all, delete-orphan")
