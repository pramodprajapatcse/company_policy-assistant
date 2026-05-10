import json
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import logging
from app.models.user import (
    User, UserCreate, UserLogin, UserUpdate, UserSession,
    hash_password, verify_password, generate_token, UserResponse, UserRole
)
from app.config import config

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self):
        self.users_file = config.DATA_DIR / "users.json"
        self.sessions_file = config.DATA_DIR / "sessions.json"
        self._ensure_files_exist()
        self._load_data()
    
    def _ensure_files_exist(self):
        """Ensure user data files exist"""
        if not self.users_file.exists():
            self._save_users({})
        if not self.sessions_file.exists():
            self._save_sessions({})
    
    def _load_data(self):
        """Load user and session data"""
        try:
            with open(self.users_file, 'r') as f:
                self.users = json.load(f)
        except:
            self.users = {}
        
        try:
            with open(self.sessions_file, 'r') as f:
                self.sessions = json.load(f)
        except:
            self.sessions = {}
    
    def _save_users(self, users: dict):
        """Save users to file"""
        with open(self.users_file, 'w') as f:
            json.dump(users, f, default=str, indent=2)
        self.users = users
    
    def _save_sessions(self, sessions: dict):
        """Save sessions to file"""
        with open(self.sessions_file, 'w') as f:
            json.dump(sessions, f, default=str, indent=2)
        self.sessions = sessions
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        # Check if user exists
        if user_data.email in self.users:
            raise ValueError("User already exists")
        
        # Check if employee ID is unique
        for existing_user in self.users.values():
            if existing_user.get('employee_id') == user_data.employee_id:
                raise ValueError("Employee ID already exists")
        
        user_id = f"user_{len(self.users) + 1}"
        
        user = User(
            user_id=user_id,
            email=user_data.email,
            full_name=user_data.full_name,
            employee_id=user_data.employee_id,
            department=user_data.department,
            phone_number=user_data.phone_number,
            location=user_data.location,
            role=UserRole.EMPLOYEE,
            created_at=datetime.now(),
            join_date=datetime.now()
        )
        
        # Store user with hashed password
        self.users[user_data.email] = {
            **user.dict(),
            "password_hash": hash_password(user_data.password)
        }
        
        self._save_users(self.users)
        logger.info(f"User created: {user_data.email}")
        
        return user
    
    def authenticate(self, login_data: UserLogin) -> Optional[User]:
        """Authenticate user"""
        user_data = self.users.get(login_data.email)
        
        if not user_data:
            return None
        
        if not verify_password(login_data.password, user_data.get('password_hash', '')):
            return None
        
        # Check if user is active
        if user_data.get('status') != 'active':
            return None
        
        # Update last login
        user_data['last_login'] = datetime.now().isoformat()
        self._save_users(self.users)
        
        return User(**{k: v for k, v in user_data.items() if k != 'password_hash'})
    
    def create_session(self, user: User, ip_address: str = None, user_agent: str = None) -> UserSession:
        """Create a new session for user"""
        session_id = generate_token()
        token = generate_token()
        
        session = UserSession(
            session_id=session_id,
            user_id=user.user_id,
            token=token,
            expires_at=datetime.now() + timedelta(days=7),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.sessions[session_id] = session.dict()
        self._save_sessions(self.sessions)
        
        return session
    
    def validate_session(self, token: str) -> Optional[User]:
        """Validate session token and return user"""
        for session_id, session_data in self.sessions.items():
            if session_data.get('token') == token:
                expires_at = datetime.fromisoformat(session_data['expires_at'])
                if expires_at > datetime.now():
                    # Get user
                    user_data = self.users.get(session_data.get('user_email'))
                    if user_data:
                        return User(**{k: v for k, v in user_data.items() if k != 'password_hash'})
        
        return None
    
    def logout(self, token: str):
        """Invalidate session"""
        for session_id, session_data in list(self.sessions.items()):
            if session_data.get('token') == token:
                del self.sessions[session_id]
                self._save_sessions(self.sessions)
                break
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        user_data = self.users.get(email)
        if user_data:
            return User(**{k: v for k, v in user_data.items() if k != 'password_hash'})
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        for user_data in self.users.values():
            if user_data.get('user_id') == user_id:
                return User(**{k: v for k, v in user_data.items() if k != 'password_hash'})
        return None
    
    def update_user(self, email: str, updates: UserUpdate) -> Optional[User]:
        """Update user information"""
        user_data = self.users.get(email)
        if not user_data:
            return None
        
        update_dict = updates.dict(exclude_unset=True)
        user_data.update(update_dict)
        
        self._save_users(self.users)
        
        return User(**{k: v for k, v in user_data.items() if k != 'password_hash'})
    
    def change_password(self, email: str, old_password: str, new_password: str) -> bool:
        """Change user password"""
        user_data = self.users.get(email)
        if not user_data:
            return False
        
        if not verify_password(old_password, user_data.get('password_hash', '')):
            return False
        
        user_data['password_hash'] = hash_password(new_password)
        self._save_users(self.users)
        
        return True
    
    def get_all_users(self) -> List[UserResponse]:
        """Get all users (admin only)"""
        users = []
        for user_data in self.users.values():
            if user_data.get('role') != 'admin':
                users.append(UserResponse(
                    **{k: v for k, v in user_data.items() if k != 'password_hash'}
                ))
        return users