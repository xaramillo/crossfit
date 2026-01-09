"""
Authentication module for CrossFit PR Tracker
Handles user authentication, password hashing, and session management
"""
import bcrypt
import streamlit as st
from typing import Optional, Dict
import db


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False


def login_user(username: str, password: str) -> Optional[Dict]:
    """
    Authenticate user and return user data if successful
    Returns None if authentication fails
    """
    user = db.get_user_by_username(username)
    
    if user and verify_password(password, user['password_hash']):
        return user
    
    return None


def register_user(username: str, password: str, full_name: Optional[str] = None) -> bool:
    """
    Register a new user with 'user' role
    Returns True if successful, False if username already exists
    """
    password_hash = hash_password(password)
    user_id = db.create_user(username, password_hash, role='user', full_name=full_name)
    
    return user_id is not None


def change_password(user_id: int, old_password: str, new_password: str) -> bool:
    """
    Change user password
    Returns True if successful, False if old password is incorrect
    """
    user = db.get_user_by_id(user_id)
    
    if not user or not verify_password(old_password, user['password_hash']):
        return False
    
    new_password_hash = hash_password(new_password)
    return db.update_user_password(user_id, new_password_hash)


def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None


def set_authenticated_user(user: Dict):
    """Set the authenticated user in session state"""
    st.session_state.authenticated = True
    st.session_state.user = user


def logout():
    """Logout the current user"""
    st.session_state.authenticated = False
    st.session_state.user = None


def is_authenticated() -> bool:
    """Check if user is authenticated"""
    return st.session_state.get('authenticated', False)


def get_current_user() -> Optional[Dict]:
    """Get the currently authenticated user"""
    return st.session_state.get('user', None)


def get_current_user_id() -> Optional[int]:
    """Get the currently authenticated user's ID"""
    user = get_current_user()
    return user['id'] if user else None


def get_current_user_role() -> Optional[str]:
    """Get the currently authenticated user's role"""
    user = get_current_user()
    return user['role'] if user else None


def is_admin() -> bool:
    """Check if current user is admin"""
    return get_current_user_role() == 'admin'


def is_coach() -> bool:
    """Check if current user is coach"""
    return get_current_user_role() == 'coach'


def is_user() -> bool:
    """Check if current user is regular user"""
    return get_current_user_role() == 'user'


def can_view_all_data() -> bool:
    """Check if current user can view all users' data (coach or admin)"""
    role = get_current_user_role()
    return role in ['coach', 'admin']


def can_modify_all_data() -> bool:
    """Check if current user can modify all users' data (admin only)"""
    return is_admin()


def ensure_default_admin():
    """
    Ensure default admin account exists
    Creates admin/admin account if no users exist
    """
    # Check if any users exist
    if not db.has_users():
        # Create default admin account
        password_hash = hash_password('admin')
        db.create_user('admin', password_hash, role='admin', full_name='Administrator')
        return True
    
    return False
