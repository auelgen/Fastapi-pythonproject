from fastapi import FastAPI,HTTPException,Depends,status
from pydantic import BaseModel
from typing import List, Annotated
from auth import blacklist_token , verify_password, create_access_token
import models
from databases import engine,SessionLocal
from crud import get_user_by_email
from sqlalchemy.orm import Session

app=FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()    

class LoginRequest(BaseModel):
    email: str
    password: str       

def logout_token(token: str):
    BLACKLIST.add(token)

@app.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, request.email)
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/logout", status_code=status.HTTP_200_OK)
async def logout(access_token: str = Depends(oauth2_scheme)):
    if access_token in TOKEN_BLACKLIST:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Gecersiz token."
        )
    
    invalidate_token(access_token)  
    TOKEN_BLACKLIST.add(access_token)  
    return {"message": "Basariyla cikis yaptiniz.."}

@app.post("/users/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, db: Session = Depends(SessionLocal)):
    new_user = create_new_user(db, user_data)  # Delegate to repository function
    return new_user

@app.patch("/users/{user_id}/email", response_model=UserOut)
async def update_user_email(user_id: int, new_email: str, db: Session = Depends(SessionLocal)):
    user = fetch_user_by_id(db, user_id) 
    if not user:
        raise HTTPException(status_code=404, detail="Kullanici bulunamadi.")
    
    user.email = new_email
    db.commit()
    db.refresh(user)  
    return user


@app.get("/users/", response_model=List[UserOut])
async def get_users(
    skip: int = 0, 
    limit: Optional[int] = Query(10, ge=1, le=100), 
    db: Session = Depends(SessionLocal)
):
    users = db.query(User).offset(skip).limit(limit).all()
    if not users:
        raise HTTPException(status_code=404, detail="Kullanici bulunamadi.")
    return users

# 5. Soft Delete User
@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Session = Depends(SessionLocal)):
    user = fetch_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    user.is_active = False  
    db.commit()
    return {"message": "Devredisi."}