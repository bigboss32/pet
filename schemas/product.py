from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = Field(gt=0)
    cost: float = Field(ge=0, default=0)
    stock: int = Field(ge=0, default=0)
    barcode: Optional[str] = None
    unidad_medida: Optional[str] = None
    category_id: int
    image_url: Optional[str] = None

class ProductCreate(ProductBase):
    image_base64: Optional[str] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    cost: Optional[float] = Field(None, ge=0)
    stock: Optional[int] = Field(None, ge=0)
    barcode: Optional[str] = None
    category_id: Optional[int] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None

class ProductResponse(ProductBase):
    id: int
    is_active: bool
    image_base64: Optional[str] = None
    
    class Config:
        from_attributes = True