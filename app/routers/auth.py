from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
 
from app.database import get_db
from app.models.models import User
 
from app.schemas.schemas import (
    RegisterRequest,
    LoginRequest,
    UserResponse,
    TokenResponse
)
 
from app.auth.security import (
    hash_password,
    verify_password,
    create_access_token
)
 
from app.auth.security import get_current_user
 
 
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)
 
 
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    user_data: RegisterRequest,
    db: Session = Depends(get_db)
):
 
    existing_email = db.query(User).filter(
        User.email == user_data.email
    ).first()
 
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
 
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(
            user_data.password
        ),
        role=user_data.role,
        is_active=True
    )
 
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
 
    return {
        "message": "User registered successfully",
        "id": new_user.id,
        "name": new_user.name,
        "email": new_user.email,
        "role": new_user.role
    }
 
 
@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    user_data: LoginRequest,
    db: Session = Depends(get_db)
):
 
    user = db.query(User).filter(
        User.email == user_data.email
    ).first()
 
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
 
    if not verify_password(
        user_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
 
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user cannot login"
        )
 
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role
        }
    )
 
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
 
 
@router.get(
    "/me",
    response_model=UserResponse
)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user