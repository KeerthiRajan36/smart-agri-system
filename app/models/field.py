from sqlalchemy import Column, Integer, String, Float, ForeignKey, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import TimestampMixin
from app.models.enums import FieldStatus


class Field(Base, TimestampMixin):
    __tablename__ = "fields"
    __table_args__ = (UniqueConstraint("farm_id", "field_name", name="uq_farm_field_name"),)

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
    field_name = Column(String(150), nullable=False)
    area = Column(Float, nullable=False)
    soil_type = Column(String(100), nullable=False)
    irrigation_type = Column(String(100), nullable=False)
    status = Column(SAEnum(FieldStatus), nullable=False, default=FieldStatus.ACTIVE)

    farm = relationship("Farm", back_populates="fields")
    crops = relationship("Crop", back_populates="field", cascade="all, delete-orphan")
    irrigations = relationship("Irrigation", back_populates="field", cascade="all, delete-orphan")
