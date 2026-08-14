from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.treatment import CropTreatment
from app.schemas.treatment import TreatmentCreate
from app.services.crop_service import get_crop_or_404
from app.utils.pagination import paginate


def create_treatment(db: Session, treatment_in: TreatmentCreate) -> CropTreatment:
    get_crop_or_404(db, treatment_in.crop_id)
    treatment = CropTreatment(**treatment_in.model_dump())
    db.add(treatment)
    db.commit()
    db.refresh(treatment)
    return treatment


def list_treatments(
    db: Session,
    page: int,
    limit: int,
    sort_by: Optional[str],
    sort_order: str,
    crop_id: Optional[int] = None,
):
    query = db.query(CropTreatment)
    if crop_id:
        query = query.filter(CropTreatment.crop_id == crop_id)
    return paginate(query, CropTreatment, page, limit, sort_by, sort_order)


def get_total_treatment_cost(db: Session, crop_id: int) -> float:
    total = db.query(func.sum(CropTreatment.cost)).filter(CropTreatment.crop_id == crop_id).scalar()
    return float(total or 0.0)
