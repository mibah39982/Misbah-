from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..db import SessionLocal

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.Sale)
def create_sale(sale: schemas.SaleCreate, db: Session = Depends(get_db)):
    total_amount = 0
    sale_items = []

    for item_data in sale.items:
        product = db.query(models.Product).filter(models.Product.id == item_data.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with id {item_data.product_id} not found")
        if product.quantity_in_stock < item_data.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough stock for product {product.name}")

        price_at_time_of_sale = product.price
        total_amount += price_at_time_of_sale * item_data.quantity

        product.quantity_in_stock -= item_data.quantity

        sale_item = models.SaleItem(
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            price_at_time_of_sale=price_at_time_of_sale
        )
        sale_items.append(sale_item)

    db_sale = models.Sale(total_amount=total_amount, items=sale_items)
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return db_sale

@router.get("/", response_model=List[schemas.Sale])
def read_sales(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sales = db.query(models.Sale).offset(skip).limit(limit).all()
    return sales
