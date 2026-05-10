from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.models.user import (
    UserCreate, UserLogin, UserUpdate, UserResponse,
    PasswordReset
)
from app.services.user_service import UserService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

# Initialize user service
user_service = UserService()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserResponse:
    """Get current user from token"""
    token = credentials.credentials
    user = user_service.validate_session(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return UserResponse(**user.dict())

def get_current_active_user(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    """Get current active user"""
    if current_user.status != 'active':
        raise HTTPException(status_code=403, detail="Inactive user")
    return current_user

@router.post("/signup", response_model=UserResponse)
async def signup(user_data: UserCreate):
    """Register a new user"""
    try:
        user = user_service.create_user(user_data)
        return UserResponse(**user.dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/login")
async def login(login_data: UserLogin, request: Request):
    """Login user and create session"""
    user = user_service.authenticate(login_data)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create session
    session = user_service.create_session(
        user,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return {
        "access_token": session.token,
        "token_type": "bearer",
        "user": UserResponse(**user.dict())
    }

@router.post("/logout")
async def logout(current_user: UserResponse = Depends(get_current_user), credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout user"""
    user_service.logout(credentials.credentials)
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    updates: UserUpdate,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Update current user information"""
    updated_user = user_service.update_user(current_user.email, updates)
    
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(**updated_user.dict())

@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Change user password"""
    success = user_service.change_password(current_user.email, old_password, new_password)
    
    if not success:
        raise HTTPException(status_code=400, detail="Invalid old password")
    
    return {"message": "Password changed successfully"}

@router.get("/users", response_model=list[UserResponse])
async def get_all_users(current_user: UserResponse = Depends(get_current_active_user)):
    """Get all users (admin only)"""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return user_service.get_all_users()