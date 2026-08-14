from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.irrigation import IrrigationCreate, IrrigationOut
from app.schemas.common import PaginatedResponse
from app.models.enums import UserRole
from app.models.user import User
from app.services import irrigation_service
from app.utils.deps import get_current_user, require_roles

router = APIRouter(tags=["Irrigation"])


@router.post("/irrigation", response_model=IrrigationOut, status_code=status.HTTP_201_CREATED)
def create_irrigation(
    irrigation_in: IrrigationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.FARM_MANAGER, UserRole.FARMER, UserRole.FIELD_WORKER)
    ),
):
    return irrigation_service.create_irrigation(db, irrigation_in)


@router.get("/irrigation", response_model=PaginatedResponse[IrrigationOut])
def list_irrigation(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sort_by: Optional[str] = None,
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total, total_pages = irrigation_service.list_irrigations(db, page, limit, sort_by, sort_order)
    return PaginatedResponse(total=total, page=page, limit=limit, total_pages=total_pages, items=items)


@router.get("/fields/{field_id}/irrigation", response_model=PaginatedResponse[IrrigationOut])
def list_irrigation_for_field(
    field_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sort_by: Optional[str] = None,
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total, total_pages = irrigation_service.list_irrigations(
        db, page, limit, sort_by, sort_order, field_id=field_id
    )
    return PaginatedResponse(total=total, page=page, limit=limit, total_pages=total_pages, items=items)
