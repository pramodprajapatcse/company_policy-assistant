from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
import hashlib
import secrets
from enum import Enum

class UserRole(str, Enum):
    EMPLOYEE = "employee"
    MANAGER = "manager"
    HR = "hr"
    ADMIN = "admin"

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class User(BaseModel):
    user_id: str
    email: EmailStr
    full_name: str
    employee_id: str
    department: str
    role: UserRole = UserRole.EMPLOYEE
    status: UserStatus = UserStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    profile_picture: Optional[str] = None
    phone_number: Optional[str] = None
    location: Optional[str] = None
    manager_email: Optional[EmailStr] = None
    join_date: Optional[datetime] = None
    preferences: dict = Field(default_factory=dict)

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str
    employee_id: str
    department: str
    phone_number: Optional[str] = None
    location: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    department: Optional[str] = None
    phone_number: Optional[str] = None
    location: Optional[str] = None
    profile_picture: Optional[str] = None
    preferences: Optional[dict] = None

class PasswordReset(BaseModel):
    email: EmailStr
    reset_token: str
    new_password: str

class UserSession(BaseModel):
    session_id: str
    user_id: str
    token: str
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class UserResponse(BaseModel):
    user_id: str
    email: EmailStr
    full_name: str
    employee_id: str
    department: str
    role: UserRole
    created_at: datetime
    last_login: Optional[datetime]
    profile_picture: Optional[str]
    phone_number: Optional[str]
    location: Optional[str]
    preferences: dict

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == hashed

def generate_token() -> str:
    """Generate secure session token"""
    return secrets.token_urlsafe(32)