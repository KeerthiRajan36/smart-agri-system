from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.sale import SaleCreate, SaleOut
from app.schemas.common import PaginatedResponse
from app.models.enums import UserRole, PaymentStatus
from app.models.user import User
from app.services import sale_service
from app.utils.deps import get_current_user, require_roles

router = APIRouter(prefix="/sales", tags=["Sales"])


@router.post("", response_model=SaleOut, status_code=status.HTTP_201_CREATED)
def create_sale(
    sale_in: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.FARM_MANAGER, UserRole.FARMER)),
):
    return sale_service.create_sale(db, sale_in)


@router.get("", response_model=PaginatedResponse[SaleOut])
def list_sales(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sort_by: Optional[str] = None,
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    payment_status: Optional[PaymentStatus] = Query(None, description="Filter by payment status"),
    buyer_name: Optional[str] = Query(None, description="Filter by buyer"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total, total_pages = sale_service.list_sales(db, page, limit, sort_by, sort_order, payment_status, buyer_name)
    return PaginatedResponse(total=total, page=page, limit=limit, total_pages=total_pages, items=items)


@router.get("/{sale_id}", response_model=SaleOut)
def get_sale(sale_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return sale_service.get_sale_or_404(db, sale_id)
