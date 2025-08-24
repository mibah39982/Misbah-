from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import datetime

from .. import models
from ..db import SessionLocal

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/daily")
def daily_sales_report(db: Session = Depends(get_db)):
    today = datetime.date.today()
    total = db.query(func.sum(models.Sale.total_amount)).filter(func.date(models.Sale.timestamp) == today).scalar()
    return {"date": today, "total_sales": total or 0}

@router.get("/weekly")
def weekly_sales_report(db: Session = Depends(get_db)):
    today = datetime.date.today()
    start_of_week = today - datetime.timedelta(days=today.weekday())
    end_of_week = start_of_week + datetime.timedelta(days=6)
    total = db.query(func.sum(models.Sale.total_amount)).filter(func.date(models.Sale.timestamp).between(start_of_week, end_of_week)).scalar()
    return {"start_of_week": start_of_week, "end_of_week": end_of_week, "total_sales": total or 0}

@router.get("/monthly")
def monthly_sales_report(db: Session = Depends(get_db)):
    today = datetime.date.today()
    total = db.query(func.sum(models.Sale.total_amount)).filter(func.extract('month', models.Sale.timestamp) == today.month, func.extract('year', models.Sale.timestamp) == today.year).scalar()
    return {"month": today.strftime("%B"), "year": today.year, "total_sales": total or 0}

@router.get("/best-selling")
def best_selling_products(db: Session = Depends(get_db)):
    results = db.query(
        models.Product.name,
        func.sum(models.SaleItem.quantity).label('total_quantity')
    ).join(models.SaleItem).group_by(models.Product.name).order_by(func.sum(models.SaleItem.quantity).desc()).limit(10).all()

    return [{"product_name": name, "total_quantity": quantity} for name, quantity in results]
