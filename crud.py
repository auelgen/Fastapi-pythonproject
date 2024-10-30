from sqlalchemy.orm import Session
from models import User

def get_user_by_email(db: Session, email: str):
    """Email ile kullanıcıyı veritabanından getirir."""
    return db.query(User).filter(User.email == email).first()