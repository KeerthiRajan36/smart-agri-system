from sqlalchemy import Column, Integer, Float, Date, String, ForeignKey
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import TimestampMixin
from app.models.enums import ProductType


class CropTreatment(Base, TimestampMixin):
    __tablename__ = "crop_treatments"

    id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=False)
    product_name = Column(String(150), nullable=False)
    product_type = Column(SAEnum(ProductType), nullable=False)
    quantity = Column(Float, nullable=False)
    applied_date = Column(Date, nullable=False)
    cost = Column(Float, nullable=False)
    remarks = Column(String(500), nullable=True)

    crop = relationship("Crop", back_populates="treatments")
