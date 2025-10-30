from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey,Text
from sqlalchemy.orm import relationship
from database import Base
from utils import get_local_now

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    cost = Column(Float, default=0.0)
    stock = Column(Integer, default=0)
    barcode = Column(String, unique=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    image_base64 = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=get_local_now)
    category = relationship("Category", back_populates="products")