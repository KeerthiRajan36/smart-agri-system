from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.harvest import HarvestCreate, HarvestOut
from app.schemas.common import PaginatedResponse
from app.models.enums import UserRole
from app.models.user import User
from app.services import harvest_service
from app.utils.deps import get_current_user, require_roles

router = APIRouter(tags=["Harvest"])


@router.post("/harvests", response_model=HarvestOut, status_code=status.HTTP_201_CREATED)
def create_harvest(
    harvest_in: HarvestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.FARM_MANAGER, UserRole.FARMER)),
):
    return harvest_service.create_harvest(db, harvest_in)


@router.get("/harvests", response_model=PaginatedResponse[HarvestOut])
def list_harvests(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sort_by: Optional[str] = None,
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    quality_grade: Optional[str] = Query(None, description="Filter by quality grade"),
    harvest_date: Optional[date] = Query(None, description="Filter by harvest date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total, total_pages = harvest_service.list_harvests(
        db, page, limit, sort_by, sort_order, quality_grade, harvest_date
    )
    return PaginatedResponse(total=total, page=page, limit=limit, total_pages=total_pages, items=items)


@router.get("/crops/{crop_id}/harvest", response_model=PaginatedResponse[HarvestOut])
def list_harvest_for_crop(
    crop_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sort_by: Optional[str] = None,
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total, total_pages = harvest_service.list_harvests(
        db, page, limit, sort_by, sort_order, crop_id=crop_id
    )
    return PaginatedResponse(total=total, page=page, limit=limit, total_pages=total_pages, items=items)
