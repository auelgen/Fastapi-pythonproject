from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt

SECRET_KEY = "your-secret-key"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Şifre hashleme için Passlib ayarı
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """Kullanıcının verdiği şifreyi hash ile karşılaştırır."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Şifreyi hashler."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """JWT tokeni oluşturur."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
