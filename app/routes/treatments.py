from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.treatment import TreatmentCreate, TreatmentOut
from app.schemas.common import PaginatedResponse
from app.models.enums import UserRole
from app.models.user import User
from app.services import treatment_service
from app.utils.deps import get_current_user, require_roles

router = APIRouter(tags=["Crop Treatments"])


@router.post("/crop-treatments", response_model=TreatmentOut, status_code=status.HTTP_201_CREATED)
def create_treatment(
    treatment_in: TreatmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.FARM_MANAGER, UserRole.FARMER, UserRole.FIELD_WORKER)
    ),
):
    return treatment_service.create_treatment(db, treatment_in)


@router.get("/crop-treatments", response_model=PaginatedResponse[TreatmentOut])
def list_treatments(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sort_by: Optional[str] = None,
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total, total_pages = treatment_service.list_treatments(db, page, limit, sort_by, sort_order)
    return PaginatedResponse(total=total, page=page, limit=limit, total_pages=total_pages, items=items)


@router.get("/crops/{crop_id}/treatments", response_model=PaginatedResponse[TreatmentOut])
def list_treatments_for_crop(
    crop_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sort_by: Optional[str] = None,
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total, total_pages = treatment_service.list_treatments(db, page, limit, sort_by, sort_order, crop_id=crop_id)
    return PaginatedResponse(total=total, page=page, limit=limit, total_pages=total_pages, items=items)
