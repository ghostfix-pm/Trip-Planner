from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.db.models import UserRole

class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="Email hợp lệ của người dùng")
    password: str = Field(..., min_length=6, description="Mật khẩu ít nhất 6 ký tự")
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True  

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"