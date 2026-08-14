from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.farm import Farm
from app.models.field import Field
from app.models.enums import FarmStatus
from app.schemas.farm import FarmCreate, FarmUpdate
from app.utils.pagination import paginate


def create_farm(db: Session, farm_in: FarmCreate, created_by_id: int) -> Farm:
    existing = db.query(Farm).filter(Farm.farm_name == farm_in.farm_name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A farm with this name already exists")

    farm = Farm(**farm_in.model_dump(), created_by_id=created_by_id)
    db.add(farm)
    db.commit()
    db.refresh(farm)
    return farm


def get_farm_or_404(db: Session, farm_id: int) -> Farm:
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found")
    return farm


def list_farms(
    db: Session,
    page: int,
    limit: int,
    sort_by: Optional[str],
    sort_order: str,
    location: Optional[str] = None,
    status_filter: Optional[FarmStatus] = None,
):
    query = db.query(Farm)
    if location:
        query = query.filter(Farm.location.ilike(f"%{location}%"))
    if status_filter:
        query = query.filter(Farm.status == status_filter)
    return paginate(query, Farm, page, limit, sort_by, sort_order)


def update_farm(db: Session, farm_id: int, farm_in: FarmUpdate) -> Farm:
    farm = get_farm_or_404(db, farm_id)
    update_data = farm_in.model_dump(exclude_unset=True)

    if "farm_name" in update_data:
        existing = (
            db.query(Farm)
            .filter(Farm.farm_name == update_data["farm_name"], Farm.id != farm_id)
            .first()
        )
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A farm with this name already exists")

    for field_name, value in update_data.items():
        setattr(farm, field_name, value)

    db.commit()
    db.refresh(farm)
    return farm


def get_available_area(db: Session, farm: Farm) -> float:
    """Farm's total area minus the area already allocated to its fields."""
    allocated_rows = db.query(Field.area).filter(Field.farm_id == farm.id).all()
    allocated_total = sum(row[0] for row in allocated_rows) if allocated_rows else 0
    return farm.total_area - allocated_total
