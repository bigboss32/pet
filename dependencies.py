from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
from models.user import User

# Dependencias comunes
def get_current_active_user(current_user: User = Depends(get_current_user)):
    return current_user

def get_db_session(db: Session = Depends(get_db)):
    return db