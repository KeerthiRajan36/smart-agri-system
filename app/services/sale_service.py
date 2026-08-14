from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status

from app.models.sale import Sale
from app.models.enums import PaymentStatus
from app.schemas.sale import SaleCreate
from app.services.harvest_service import get_harvest_or_404
from app.utils.pagination import paginate


def create_sale(db: Session, sale_in: SaleCreate) -> Sale:
    harvest = get_harvest_or_404(db, sale_in.harvest_id)

    already_sold = (
        db.query(func.sum(Sale.quantity)).filter(Sale.harvest_id == harvest.id).scalar() or 0
    )
    remaining = harvest.quantity - already_sold
    if sale_in.quantity > remaining:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot sell {sale_in.quantity} {harvest.unit}; only {remaining} {harvest.unit} of harvested produce remain",
        )

    total_amount = round(sale_in.quantity * sale_in.price_per_unit, 2)
    sale = Sale(**sale_in.model_dump(), total_amount=total_amount)
    db.add(sale)
    db.commit()
    db.refresh(sale)
    return sale


def get_sale_or_404(db: Session, sale_id: int) -> Sale:
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")
    return sale


def list_sales(
    db: Session,
    page: int,
    limit: int,
    sort_by: Optional[str],
    sort_order: str,
    payment_status: Optional[PaymentStatus] = None,
    buyer_name: Optional[str] = None,
):
    query = db.query(Sale)
    if payment_status:
        query = query.filter(Sale.payment_status == payment_status)
    if buyer_name:
        query = query.filter(Sale.buyer_name.ilike(f"%{buyer_name}%"))
    return paginate(query, Sale, page, limit, sort_by, sort_order)
