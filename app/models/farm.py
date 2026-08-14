from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import TimestampMixin
from app.models.enums import FarmStatus


class Farm(Base, TimestampMixin):
    __tablename__ = "farms"

    id = Column(Integer, primary_key=True, index=True)
    farm_name = Column(String(150), unique=True, nullable=False, index=True)
    location = Column(String(200), nullable=False, index=True)
    total_area = Column(Float, nullable=False)
    owner_name = Column(String(150), nullable=False)
    status = Column(SAEnum(FarmStatus), nullable=False, default=FarmStatus.ACTIVE)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    fields = relationship("Field", back_populates="farm", cascade="all, delete-orphan")
