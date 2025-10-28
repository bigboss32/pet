from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from .user import UserSimple

class SaleItemBase(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    price: float = Field(gt=0)

class SaleBase(BaseModel):
    payment_method: str
    customer_name: Optional[str] = None
    customer_email: Optional[EmailStr] = None
    discount: float = Field(ge=0, default=0)
    notes: Optional[str] = None

class SaleCreate(SaleBase):
    items: List[SaleItemBase]

class SaleItemResponse(SaleItemBase):
    id: int
    subtotal: float
    product_name: Optional[str] = None  # Para mostrar el nombre del producto
    
    class Config:
        from_attributes = True

class SaleResponse(SaleBase):
    id: int
    total: float
    subtotal: float
    tax: float
    created_at: datetime
    user: Optional[UserSimple] = None  # ✅ Ahora usa UserSimple
    items: List[SaleItemResponse]
    
    class Config:
        from_attributes = True

# Esquema para respuestas con joins
class SaleWithUserResponse(SaleResponse):
    user: Optional[UserSimple] = None
    
    class Config:
        from_attributes = True