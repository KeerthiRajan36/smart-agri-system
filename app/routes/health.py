from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.health import HealthCreate, HealthOut
from app.schemas.common import PaginatedResponse
from app.models.enums import UserRole
from app.models.user import User
from app.services import health_service
from app.utils.deps import get_current_user, require_roles

router = APIRouter(tags=["Crop Health"])


@router.post("/crop-health", response_model=HealthOut, status_code=status.HTTP_201_CREATED)
def create_health_record(
    health_in: HealthCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.FARM_MANAGER, UserRole.FARMER, UserRole.FIELD_WORKER)
    ),
):
    return health_service.create_health_record(db, health_in)


@router.get("/crop-health", response_model=PaginatedResponse[HealthOut])
def list_health_records(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sort_by: Optional[str] = None,
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total, total_pages = health_service.list_health_records(db, page, limit, sort_by, sort_order)
    return PaginatedResponse(total=total, page=page, limit=limit, total_pages=total_pages, items=items)


@router.get("/crops/{crop_id}/health-history", response_model=PaginatedResponse[HealthOut])
def list_health_history(
    crop_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sort_by: Optional[str] = None,
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total, total_pages = health_service.list_health_records(db, page, limit, sort_by, sort_order, crop_id=crop_id)
    return PaginatedResponse(total=total, page=page, limit=limit, total_pages=total_pages, items=items)
