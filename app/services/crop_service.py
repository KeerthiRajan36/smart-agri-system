from typing import Optional
from datetime import date
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.crop import Crop
from app.models.enums import CropStatus, FieldStatus
from app.schemas.crop import CropCreate, CropUpdate
from app.services.field_service import get_field_or_404
from app.utils.pagination import paginate

# Statuses that count as an "active" crop cycle occupying a field.
ACTIVE_CROP_STATUSES = [CropStatus.PLANNED, CropStatus.GROWING, CropStatus.READY_FOR_HARVEST]


def create_crop(db: Session, crop_in: CropCreate) -> Crop:
    field = get_field_or_404(db, crop_in.field_id)

    if field.status != FieldStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive fields cannot be used for new crop cultivation",
        )

    overlapping = (
        db.query(Crop)
        .filter(Crop.field_id == crop_in.field_id, Crop.status.in_(ACTIVE_CROP_STATUSES))
        .first()
    )
    if overlapping:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This field already has an active crop cycle; a field cannot have overlapping active crops",
        )

    crop = Crop(**crop_in.model_dump())
    db.add(crop)
    db.commit()
    db.refresh(crop)
    return crop


def get_crop_or_404(db: Session, crop_id: int) -> Crop:
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crop not found")
    return crop


def list_crops(
    db: Session,
    page: int,
    limit: int,
    sort_by: Optional[str],
    sort_order: str,
    crop_name: Optional[str] = None,
    status_filter: Optional[CropStatus] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
):
    query = db.query(Crop)
    if crop_name:
        query = query.filter(Crop.crop_name.ilike(f"%{crop_name}%"))
    if status_filter:
        query = query.filter(Crop.status == status_filter)
    if start_date:
        query = query.filter(Crop.planting_date >= start_date)
    if end_date:
        query = query.filter(Crop.planting_date <= end_date)
    return paginate(query, Crop, page, limit, sort_by, sort_order)


def update_crop(db: Session, crop_id: int, crop_in: CropUpdate) -> Crop:
    crop = get_crop_or_404(db, crop_id)

    if crop.status == CropStatus.HARVESTED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Harvested crops cannot be modified")

    update_data = crop_in.model_dump(exclude_unset=True)
    planting_date = update_data.get("planting_date", crop.planting_date)
    expected_harvest_date = update_data.get("expected_harvest_date", crop.expected_harvest_date)
    if planting_date > expected_harvest_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="planting_date cannot be after expected_harvest_date",
        )

    for field_name, value in update_data.items():
        setattr(crop, field_name, value)

    db.commit()
    db.refresh(crop)
    return crop
