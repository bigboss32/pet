from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
import jwt
from passlib.context import CryptContext
import enum
import os
from zoneinfo import ZoneInfo  # ✅ Importar para manejo de zonas horarias

# ✅ Configurar zona horaria de Colombia
TIMEZONE = ZoneInfo("America/Bogota")

def get_local_now():
    """Obtiene la fecha y hora actual en la zona horaria de Colombia"""
    return datetime.now(TIMEZONE)

# Configuración
SECRET_KEY = os.getenv("SECRET_KEY", "tu-clave-secreta-muy-segura-cambiala-en-produccion")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./paws_pos.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Enums
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    CASHIER = "cashier"
    MANAGER = "manager"

class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    CARD = "card"
    NEQUI = "nequi"
    DAVIPLATA = "daviplata"
    TRANSFER = "transfer"

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(SQLEnum(UserRole), default=UserRole.CASHIER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=get_local_now)  # ✅ Usar zona horaria local

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    price = Column(Float)
    cost = Column(Float, default=0)
    stock = Column(Integer, default=0)
    barcode = Column(String, unique=True, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    image_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=get_local_now)  # ✅ Usar zona horaria local
    category = relationship("Category", back_populates="products")

class Sale(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total = Column(Float)
    subtotal = Column(Float)
    tax = Column(Float, default=0)
    discount = Column(Float, default=0)
    payment_method = Column(SQLEnum(PaymentMethod))
    customer_name = Column(String, nullable=True)
    customer_email = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=get_local_now)  # ✅ Usar zona horaria local
    items = relationship("SaleItem", back_populates="sale")
    user = relationship("User")

class SaleItem(Base):
    __tablename__ = "sale_items"
    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    price = Column(Float)
    subtotal = Column(Float)
    sale = relationship("Sale", back_populates="items")
    product = relationship("Product")

class UserSimple(BaseModel):
    id: int
    username: str
    full_name: Optional[str]

    class Config:
        from_attributes = True

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str
    role: UserRole = UserRole.CASHIER

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = Field(gt=0)
    cost: float = Field(ge=0, default=0)
    stock: int = Field(ge=0, default=0)
    barcode: Optional[str] = None
    category_id: int
    image_url: Optional[str] = None

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

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    cost: float
    stock: int
    barcode: Optional[str]
    category_id: int
    image_url: Optional[str]
    is_active: bool
    created_at: datetime
    category: CategoryResponse

    class Config:
        from_attributes = True

class SaleItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    price: float = Field(gt=0)

class SaleCreate(BaseModel):
    items: List[SaleItemCreate]
    payment_method: PaymentMethod
    customer_name: Optional[str] = None
    customer_email: Optional[EmailStr] = None
    discount: float = Field(ge=0, default=0)
    notes: Optional[str] = None

class SaleItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float
    subtotal: float
    product: ProductResponse

    class Config:
        from_attributes = True

class SaleResponse(BaseModel):
    id: int
    total: float
    subtotal: float
    tax: float
    discount: float
    payment_method: PaymentMethod
    customer_name: Optional[str]
    customer_email: Optional[str]
    notes: Optional[str]
    created_at: datetime
    user: Optional[UserSimple]
    items: List[SaleItemResponse]

    class Config:
        from_attributes = True

# FastAPI app
app = FastAPI(title="Paws POS Pro API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Auth functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    password = password[:72]
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = get_local_now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # ✅ Usar zona horaria local
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

# Routes
@app.get("/")
def read_root():
    return {"message": "Paws POS Pro API", "version": "1.0.0"}

@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email or username already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        full_name=user.full_name,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/auth/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_credentials.username).first()
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# Categories
@app.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category: CategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_category = db.query(Category).filter(Category.name == category.name).first()
    if db_category:
        raise HTTPException(status_code=400, detail="Category already exists")
    
    new_category = Category(**category.dict())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

@app.get("/categories", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Category).all()

# Products
@app.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    category = db.query(Category).filter(Category.id == product.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    if product.barcode:
        existing = db.query(Product).filter(Product.barcode == product.barcode).first()
        if existing:
            raise HTTPException(status_code=400, detail="Barcode already exists")
    
    new_product = Product(**product.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@app.get("/products", response_model=List[ProductResponse])
def get_products(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    is_active: Optional[bool] = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Product)
    
    if is_active is not None:
        query = query.filter(Product.is_active == is_active)
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if search:
        query = query.filter(Product.name.contains(search))
    
    return query.offset(skip).limit(limit).all()

@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = product_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    return product

@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product.is_active = False
    db.commit()
    return None

# Sales
@app.post("/sales", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
def create_sale(sale: SaleCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Validate products and stock
    subtotal = 0
    for item in sale.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {product.name}")
        subtotal += item.price * item.quantity
    
    # Calculate totals
    tax = subtotal * 0.19  # 19% IVA
    total = subtotal + tax - sale.discount
    
    # Create sale
    new_sale = Sale(
        user_id=current_user.id,
        subtotal=subtotal,
        tax=tax,
        discount=sale.discount,
        total=total,
        payment_method=sale.payment_method,
        customer_name=sale.customer_name,
        customer_email=sale.customer_email,
        notes=sale.notes
    )
    db.add(new_sale)
    db.flush()
    
    # Create sale items and update stock
    for item in sale.items:
        sale_item = SaleItem(
            sale_id=new_sale.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.price,
            subtotal=item.price * item.quantity
        )
        db.add(sale_item)
        
        # Update product stock
        product = db.query(Product).filter(Product.id == item.product_id).first()
        product.stock -= item.quantity
    
    db.commit()
    db.refresh(new_sale)
    return new_sale

from sqlalchemy.orm import joinedload

@app.get("/sales", response_model=List[SaleResponse])
def get_sales(
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    today: bool = False,
    summary: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Sale).options(
        joinedload(Sale.user),
        joinedload(Sale.items).joinedload(SaleItem.product).joinedload(Product.category)
    )

    # ✅ Filtrar por fecha si el frontend manda start_date o end_date
    if start_date:
        query = query.filter(Sale.created_at >= start_date)
    if end_date:
        query = query.filter(Sale.created_at <= end_date)

    # ✅ Si el frontend pide las ventas del día actual
    if today:
        today_date = get_local_now().date()
        start_of_day = datetime.combine(today_date, datetime.min.time()).replace(tzinfo=TIMEZONE)
        end_of_day = datetime.combine(today_date, datetime.max.time()).replace(tzinfo=TIMEZONE)
        query = query.filter(Sale.created_at >= start_of_day, Sale.created_at <= end_of_day)

    # ✅ Si el frontend solo quiere el resumen del día
    if summary:
        today_date = get_local_now().date()
        start_of_day = datetime.combine(today_date, datetime.min.time()).replace(tzinfo=TIMEZONE)
        end_of_day = datetime.combine(today_date, datetime.max.time()).replace(tzinfo=TIMEZONE)

        sales = query.filter(Sale.created_at >= start_of_day, Sale.created_at <= end_of_day).all()
        total = sum(s.total for s in sales)
        count = len(sales)
        return {"total": total, "count": count}

    # ✅ Devolver la lista de ventas normal
    return query.order_by(Sale.created_at.desc()).offset(skip).limit(limit).all()

@app.get("/sales/{sale_id}", response_model=SaleResponse)
def get_sale(sale_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale

from datetime import date

# Dashboard stats
@app.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    today_date = get_local_now().date()  # ✅ Usar zona horaria local
    
    # Today's sales
    today_sales = db.query(Sale).filter(
        Sale.created_at >= datetime.combine(today_date, datetime.min.time()).replace(tzinfo=TIMEZONE)
    ).all()
    
    today_revenue = sum(sale.total for sale in today_sales)
    today_count = len(today_sales)
    
    # Total products
    total_products = db.query(Product).filter(Product.is_active == True).count()
    
    # Low stock products
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)