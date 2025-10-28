from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from auth import get_current_user
from models.user import User
from models.sale import Sale
from models.product import Product
from utils import get_local_now

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    today_date = get_local_now().date()
    
    # Ventas de hoy
    today_sales = db.query(Sale).filter(
        Sale.created_at >= datetime.combine(today_date, datetime.min.time()).replace(tzinfo=get_local_now().tzinfo)
    ).all()
    
    today_revenue = sum(sale.total for sale in today_sales)
    today_count = len(today_sales)
    
    # Total de productos
    total_products = db.query(Product).filter(Product.is_active == True).count()
    
    # Productos con stock bajo
    low_stock = db.query(Product).filter(
        Product.is_active == True,
        Product.stock < 10
    ).count()
    
    return {
        "today_revenue": today_revenue,
        "today_sales_count": today_count,
        "total_products": total_products,
        "low_stock_products": low_stock
    }