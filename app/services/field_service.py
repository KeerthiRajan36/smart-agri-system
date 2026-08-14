from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.field import Field
from app.schemas.field import FieldCreate
from app.services.farm_service import get_farm_or_404, get_available_area
from app.utils.pagination import paginate


def create_field(db: Session, farm_id: int, field_in: FieldCreate) -> Field:
    farm = get_farm_or_404(db, farm_id)

    existing = (
        db.query(Field)
        .filter(Field.farm_id == farm_id, Field.field_name == field_in.field_name)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A field with this name already exists on this farm",
        )

    available_area = get_available_area(db, farm)
    if field_in.area > available_area:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Field area ({field_in.area}) exceeds the farm's available area ({available_area})",
        )

    field = Field(farm_id=farm_id, **field_in.model_dump())
    db.add(field)
    db.commit()
    db.refresh(field)
    return field


def get_field_or_404(db: Session, field_id: int) -> Field:
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Field not found")
    return field


def list_fields_for_farm(db: Session, farm_id: int, page: int, limit: int, sort_by: Optional[str], sort_order: str):
    get_farm_or_404(db, farm_id)
    query = db.query(Field).filter(Field.farm_id == farm_id)
    return paginate(query, Field, page, limit, sort_by, sort_order)
