from models import User
from sqlalchemy.orm import Session

def get_user_list(db: Session):
    user_list = db.query(User).order_by(User.created_at.desc()).all()
    return user_list