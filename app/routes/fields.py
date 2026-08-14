from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.field import FieldCreate, FieldOut
from app.schemas.common import PaginatedResponse
from app.models.enums import UserRole
from app.models.user import User
from app.services import field_service
from app.utils.deps import get_current_user, require_roles

# Nested under /farms/{farm_id}/fields per the assignment's API spec.
router = APIRouter(prefix="/farms", tags=["Fields"])


@router.post("/{farm_id}/fields", response_model=FieldOut, status_code=status.HTTP_201_CREATED)
def create_field(
    farm_id: int,
    field_in: FieldCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.FARM_MANAGER)),
):
    return field_service.create_field(db, farm_id, field_in)


@router.get("/{farm_id}/fields", response_model=PaginatedResponse[FieldOut])
def list_fields(
    farm_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sort_by: Optional[str] = None,
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total, total_pages = field_service.list_fields_for_farm(db, farm_id, page, limit, sort_by, sort_order)
    return PaginatedResponse(total=total, page=page, limit=limit, total_pages=total_pages, items=items)
