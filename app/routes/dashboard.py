from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.dashboard import DashboardSummary, DashboardReports, FarmRevenue, CropProduction
from app.models.enums import UserRole
from app.models.user import User
from app.services import dashboard_service
from app.utils.deps import require_roles

router = APIRouter(prefix="/dashboard", tags=["Dashboard & Reports"])


@router.get("/summary", response_model=DashboardSummary)
def summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.FARM_MANAGER)),
):
    return dashboard_service.get_summary(db)


@router.get("/reports", response_model=DashboardReports)
def reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.FARM_MANAGER)),
):
    farm_revenue = dashboard_service.get_farm_wise_revenue(db)
    crop_production = dashboard_service.get_crop_wise_production(db)
    return DashboardReports(
        farm_wise_revenue=[FarmRevenue(**r) for r in farm_revenue],
        crop_wise_production=[CropProduction(**r) for r in crop_production],
    )
