from typing import Optional
from sqlalchemy.orm import Session

from app.models.health import CropHealth
from app.models.alert import Alert
from app.models.enums import HealthStatus
from app.schemas.health import HealthCreate
from app.services.crop_service import get_crop_or_404
from app.utils.pagination import paginate


def create_health_record(db: Session, health_in: HealthCreate) -> CropHealth:
    get_crop_or_404(db, health_in.crop_id)

    record = CropHealth(**health_in.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)

    # Business rule: a Critical inspection raises an alert for the Farm Manager.
    if record.health_status == HealthStatus.CRITICAL:
        message = f"Crop #{record.crop_id} was inspected as CRITICAL on {record.inspection_date}"
        if record.disease_name:
            message += f" (suspected: {record.disease_name})"
        alert = Alert(crop_id=record.crop_id, message=message, target_role="farm_manager")
        db.add(alert)
        db.commit()

    return record


def list_health_records(
    db: Session,
    page: int,
    limit: int,
    sort_by: Optional[str],
    sort_order: str,
    crop_id: Optional[int] = None,
):
    query = db.query(CropHealth)
    if crop_id:
        query = query.filter(CropHealth.crop_id == crop_id)
    return paginate(query, CropHealth, page, limit, sort_by, sort_order)
