from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.farm import FarmCreate, FarmUpdate, FarmOut
from app.schemas.common import PaginatedResponse
from app.models.enums import UserRole, FarmStatus
from app.models.user import User
from app.services import farm_service
from app.utils.deps import get_current_user, require_roles

router = APIRouter(prefix="/farms", tags=["Farms"])


@router.post("", response_model=FarmOut, status_code=status.HTTP_201_CREATED)
def create_farm(
    farm_in: FarmCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.FARM_MANAGER)),
):
    return farm_service.create_farm(db, farm_in, created_by_id=current_user.id)


@router.get("", response_model=PaginatedResponse[FarmOut])
def list_farms(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sort_by: Optional[str] = None,
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    location: Optional[str] = Query(None, description="Search by location"),
    status: Optional[FarmStatus] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total, total_pages = farm_service.list_farms(db, page, limit, sort_by, sort_order, location, status)
    return PaginatedResponse(total=total, page=page, limit=limit, total_pages=total_pages, items=items)


@router.get("/{farm_id}", response_model=FarmOut)
def get_farm(farm_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return farm_service.get_farm_or_404(db, farm_id)


@router.put("/{farm_id}", response_model=FarmOut)
def update_farm(
    farm_id: int,
    farm_in: FarmUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.FARM_MANAGER)),
):
    return farm_service.update_farm(db, farm_id, farm_in)
