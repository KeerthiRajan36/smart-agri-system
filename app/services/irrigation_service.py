from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.irrigation import Irrigation
from app.models.crop import Crop
from app.models.enums import CropStatus
from app.schemas.irrigation import IrrigationCreate
from app.services.field_service import get_field_or_404
from app.utils.pagination import paginate

ACTIVE_CROP_STATUSES = [CropStatus.PLANNED, CropStatus.GROWING, CropStatus.READY_FOR_HARVEST]


def create_irrigation(db: Session, irrigation_in: IrrigationCreate) -> Irrigation:
    field = get_field_or_404(db, irrigation_in.field_id)

    active_crop = (
        db.query(Crop)
        .filter(Crop.field_id == field.id, Crop.status.in_(ACTIVE_CROP_STATUSES))
        .first()
    )
    if not active_crop:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Irrigation can be recorded only for fields with an active crop",
        )

    irrigation = Irrigation(**irrigation_in.model_dump())
    db.add(irrigation)
    db.commit()
    db.refresh(irrigation)
    return irrigation


def list_irrigations(
    db: Session,
    page: int,
    limit: int,
    sort_by: Optional[str],
    sort_order: str,
    field_id: Optional[int] = None,
):
    query = db.query(Irrigation)
    if field_id:
        query = query.filter(Irrigation.field_id == field_id)
    return paginate(query, Irrigation, page, limit, sort_by, sort_order)
