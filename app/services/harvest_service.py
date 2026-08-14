from typing import Optional
from datetime import date
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.harvest import Harvest
from app.models.enums import CropStatus
from app.schemas.harvest import HarvestCreate
from app.services.crop_service import get_crop_or_404
from app.utils.pagination import paginate


def create_harvest(db: Session, harvest_in: HarvestCreate) -> Harvest:
    crop = get_crop_or_404(db, harvest_in.crop_id)

    if crop.status != CropStatus.READY_FOR_HARVEST:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Harvest can be created only when the crop status is 'Ready for Harvest'",
        )

    harvest = Harvest(**harvest_in.model_dump())
    db.add(harvest)

    # Business rule: crop status automatically moves to Harvested.
    crop.status = CropStatus.HARVESTED
    db.add(crop)

    db.commit()
    db.refresh(harvest)
    return harvest


def get_harvest_or_404(db: Session, harvest_id: int) -> Harvest:
    harvest = db.query(Harvest).filter(Harvest.id == harvest_id).first()
    if not harvest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Harvest not found")
    return harvest


def list_harvests(
    db: Session,
    page: int,
    limit: int,
    sort_by: Optional[str],
    sort_order: str,
    quality_grade: Optional[str] = None,
    harvest_date: Optional[date] = None,
    crop_id: Optional[int] = None,
):
    query = db.query(Harvest)
    if quality_grade:
        query = query.filter(Harvest.quality_grade == quality_grade)
    if harvest_date:
        query = query.filter(Harvest.harvest_date == harvest_date)
    if crop_id:
        query = query.filter(Harvest.crop_id == crop_id)
    return paginate(query, Harvest, page, limit, sort_by, sort_order)
