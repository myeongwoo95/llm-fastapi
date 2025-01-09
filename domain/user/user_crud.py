from passlib.context import CryptContext
from models import User
from sqlalchemy.orm import Session
from domain.user.user_schema import UserCreate, UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_list(db: Session):
    user_list = db.query(User).order_by(User.created_at.desc()).all()
    return user_list

def create_user(db: Session, user_create: UserCreate):
    db_user = User(
        name=user_create.name,
        email=user_create.email,
        password=pwd_context.hash(user_create.password),
    )
    db.add(db_user)
    db.commit()

def get_existing_user(db: Session, user_create: UserCreate):
    return db.query(User).filter(User.email == user_create.email).first()

def get_user(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()