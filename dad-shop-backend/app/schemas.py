from pydantic import BaseModel, ConfigDict
from typing import List, Optional
import datetime

# Schemas for SaleItem
class SaleItemBase(BaseModel):
    product_id: int
    quantity: int

class SaleItemCreate(SaleItemBase):
    pass

class SaleItem(SaleItemBase):
    id: int
    price_at_time_of_sale: float

    model_config = ConfigDict(from_attributes=True)

# Schemas for Product
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    quantity_in_stock: int
    category: Optional[str] = None
    supplier: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# Schemas for Sale
class SaleBase(BaseModel):
    pass

class SaleCreate(SaleBase):
    items: List[SaleItemCreate]

class Sale(SaleBase):
    id: int
    timestamp: datetime.datetime
    total_amount: float
    items: List[SaleItem] = []

    model_config = ConfigDict(from_attributes=True)
