from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.crop import CropCreate, CropUpdate, CropOut
from app.schemas.common import PaginatedResponse
from app.models.enums import UserRole, CropStatus
from app.models.user import User
from app.services import crop_service
from app.utils.deps import get_current_user, require_roles

router = APIRouter(prefix="/crops", tags=["Crops"])


@router.post("", response_model=CropOut, status_code=status.HTTP_201_CREATED)
def create_crop(
    crop_in: CropCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.FARM_MANAGER, UserRole.FARMER)),
):
    return crop_service.create_crop(db, crop_in)


@router.get("", response_model=PaginatedResponse[CropOut])
def list_crops(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sort_by: Optional[str] = None,
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    crop_name: Optional[str] = Query(None, description="Search by crop name"),
    status: Optional[CropStatus] = Query(None, description="Filter by crop status"),
    start_date: Optional[date] = Query(None, description="Planting date range start"),
    end_date: Optional[date] = Query(None, description="Planting date range end"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total, total_pages = crop_service.list_crops(
        db, page, limit, sort_by, sort_order, crop_name, status, start_date, end_date
    )
    return PaginatedResponse(total=total, page=page, limit=limit, total_pages=total_pages, items=items)


@router.get("/{crop_id}", response_model=CropOut)
def get_crop(crop_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return crop_service.get_crop_or_404(db, crop_id)


@router.put("/{crop_id}", response_model=CropOut)
def update_crop(
    crop_id: int,
    crop_in: CropUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.FARM_MANAGER, UserRole.FARMER)),
):
    return crop_service.update_crop(db, crop_id, crop_in)
