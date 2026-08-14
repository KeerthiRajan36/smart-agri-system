from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.farm import Farm
from app.models.field import Field
from app.models.crop import Crop
from app.models.harvest import Harvest
from app.models.sale import Sale
from app.models.treatment import CropTreatment
from app.models.alert import Alert
from app.models.enums import CropStatus


def get_summary(db: Session) -> dict:
    total_farms = db.query(func.count(Farm.id)).scalar() or 0
    total_fields = db.query(func.count(Field.id)).scalar() or 0

    active_crops = (
        db.query(func.count(Crop.id))
        .filter(Crop.status.in_([CropStatus.PLANNED, CropStatus.GROWING, CropStatus.READY_FOR_HARVEST]))
        .scalar()
        or 0
    )
    crops_ready = (
        db.query(func.count(Crop.id)).filter(Crop.status == CropStatus.READY_FOR_HARVEST).scalar() or 0
    )
    critical_alerts = db.query(func.count(Alert.id)).filter(Alert.is_resolved == False).scalar() or 0  # noqa: E712

    total_harvest_qty = db.query(func.sum(Harvest.quantity)).scalar() or 0
    total_sales = db.query(func.count(Sale.id)).scalar() or 0
    total_revenue = db.query(func.sum(Sale.total_amount)).scalar() or 0
    total_treatment_cost = db.query(func.sum(CropTreatment.cost)).scalar() or 0

    return {
        "total_farms": total_farms,
        "total_fields": total_fields,
        "active_crops": active_crops,
        "crops_ready_for_harvest": crops_ready,
        "critical_crop_alerts": critical_alerts,
        "total_harvest_quantity": float(total_harvest_qty),
        "total_sales": total_sales,
        "total_revenue": float(total_revenue),
        "total_treatment_cost": float(total_treatment_cost),
    }


def get_farm_wise_revenue(db: Session):
    rows = (
        db.query(Farm.id, Farm.farm_name, func.coalesce(func.sum(Sale.total_amount), 0))
        .outerjoin(Field, Field.farm_id == Farm.id)
        .outerjoin(Crop, Crop.field_id == Field.id)
        .outerjoin(Harvest, Harvest.crop_id == Crop.id)
        .outerjoin(Sale, Sale.harvest_id == Harvest.id)
        .group_by(Farm.id, Farm.farm_name)
        .all()
    )
    return [{"farm_id": r[0], "farm_name": r[1], "total_revenue": float(r[2])} for r in rows]


def get_crop_wise_production(db: Session):
    rows = (
        db.query(Crop.crop_name, func.coalesce(func.sum(Harvest.quantity), 0))
        .outerjoin(Harvest, Harvest.crop_id == Crop.id)
        .group_by(Crop.crop_name)
        .all()
    )
    return [{"crop_name": r[0], "total_quantity": float(r[1])} for r in rows]
