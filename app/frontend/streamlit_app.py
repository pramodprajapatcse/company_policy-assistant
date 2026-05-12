import streamlit as st
import requests
import time
from datetime import datetime
import plotly.graph_objects as go
import pandas as pd
from PIL import Image
import io
import base64
import os
import hashlib
import json
import random
import re
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import pyotp
import phonenumbers
from twilio.rest import Client
import os

# ===============================
# MAHINDRA BRAND COLORS
# ===============================
MAHINDRA_RED = "#D71920"
MAHINDRA_DARK_RED = "#A5151C"
MAHINDRA_GRAY = "#4A4A4A"
MAHINDRA_LIGHT_GRAY = "#F5F5F5"
MAHINDRA_DARK_GRAY = "#2C2C2C"
MAHINDRA_GOLD = "#C5A028"

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="Mahindra Rise - AI Policy Assistant",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===============================
# EMAIL AND SMS CONFIGURATION
# ===============================
class EmailService:
    def __init__(self):
        # Configure your email settings here
        self.smtp_server = "smtp.gmail.com"  # or your company's SMTP server
        self.smtp_port = 587
        self.sender_email = "your-email@gmail.com"  # Replace with your email
        self.sender_password = "your-app-password"  # Replace with your app password
    
    def send_otp_email(self, recipient_email, otp):
        """Send OTP via email"""
        try:
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = recipient_email
            message["Subject"] = "Mahindra Policy Assistant - Password Reset OTP"
            
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                    <div style="text-align: center;">
                        <div style="width: 80px; height: 80px; background: #D71920; border-radius: 20px; margin: 0 auto; display: flex; align-items: center; justify-content: center;">
                            <span style="font-size: 2rem; color: white;">M</span>
                        </div>
                        <h2 style="color: #2C2C2C;">Mahindra Rise</h2>
                        <h3>Password Reset Request</h3>
                    </div>
                    <div style="padding: 20px;">
                        <p>Hello,</p>
                        <p>You requested to reset your password for your Mahindra Policy Assistant account.</p>
                        <div style="text-align: center; margin: 30px 0;">
                            <div style="font-size: 32px; font-weight: bold; color: #D71920; letter-spacing: 5px;">{otp}</div>
                            <p style="color: #666;">This OTP is valid for 5 minutes</p>
                        </div>
                        <p>If you didn't request this, please ignore this email.</p>
                        <hr style="border: none; border-top: 1px solid #ddd;">
                        <p style="font-size: 12px; color: #999;">This is an automated message, please do not reply.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            message.attach(MIMEText(html_content, "html"))
            
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            return True
        except Exception as e:
            print(f"Email error: {e}")
            return False

class SMSService:
    def __init__(self):
        # Configure Twilio SMS settings
        self.account_sid = os.environ.get("TWILIO_ACCOUNT_SID", "")
        self.auth_token = os.environ.get("TWILIO_AUTH_TOKEN", "")
        self.twilio_phone = os.environ.get("TWILIO_PHONE_NUMBER", "")
        self.client = Client(self.account_sid, self.auth_token) if self.account_sid else None
    
    def send_otp_sms(self, phone_number, otp):
        """Send OTP via SMS"""
        try:
            if not self.client:
                # Demo mode if Twilio not configured
                st.warning("SMS service not configured. Using demo mode.")
                return True
            
            message = self.client.messages.create(
                body=f"Mahindra Policy Assistant: Your OTP for password reset is {otp}. Valid for 5 minutes.",
                from_=self.twilio_phone,
                to=phone_number
            )
            return True
        except Exception as e:
            print(f"SMS error: {e}")
            return False

# ===============================
# OTP MANAGEMENT
# ===============================
class OTPManager:
    def __init__(self):
        self.otp_storage = {}
        self.email_service = EmailService()
        self.sms_service = SMSService()
    
    def generate_otp(self, email):
        otp = str(random.randint(100000, 999999))
        self.otp_storage[email] = {
            "otp": otp,
            "expires_at": time.time() + 300,
            "attempts": 0
        }
        return otp
    
    def send_otp_email(self, email, otp):
        """Send real OTP via email"""
        return self.email_service.send_otp_email(email, otp)
    
    def send_otp_sms(self, phone, otp):
        """Send real OTP via SMS"""
        return self.sms_service.send_otp_sms(phone, otp)
    
    def verify_otp(self, email, otp):
        if email not in self.otp_storage:
            return False
        
        stored_data = self.otp_storage[email]
        
        if time.time() > stored_data["expires_at"]:
            del self.otp_storage[email]
            return False
        
        if stored_data["attempts"] >= 3:
            del self.otp_storage[email]
            return False
        
        stored_data["attempts"] += 1
        
        if stored_data["otp"] == otp:
            del self.otp_storage[email]
            return True
        
        return False

otp_manager = OTPManager()

# ===============================
# USER DATA MANAGEMENT
# ===============================
def get_users_file():
    users_dir = Path("data/users")
    users_dir.mkdir(parents=True, exist_ok=True)
    return users_dir / "users.json"

def load_users():
    users_file = get_users_file()
    if users_file.exists():
        with open(users_file, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    users_file = get_users_file()
    with open(users_file, 'w') as f:
        json.dump(users, f, indent=2)

def save_profile_image(user_email, image_file):
    if image_file:
        profile_dir = Path("data/profile_images")
        profile_dir.mkdir(parents=True, exist_ok=True)
        
        image_path = profile_dir / f"{user_email.replace('@', '_').replace('.', '_')}.jpg"
        
        try:
            img = Image.open(image_file)
            img = img.resize((200, 200))
            img.save(image_path, 'JPEG', quality=85)
            return str(image_path)
        except Exception as e:
            print(f"Error saving image: {e}")
            return None
    return None

def get_profile_image(user_email):
    profile_dir = Path("data/profile_images")
    image_path = profile_dir / f"{user_email.replace('@', '_').replace('.', '_')}.jpg"
    
    if image_path.exists():
        return image_path
    return None

# ===============================
# AUTHENTICATION FUNCTIONS
# ===============================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

def login_user(email, password):
    users = load_users()
    
    if email in users:
        if verify_password(password, users[email]["password"]):
            st.session_state.authenticated = True
            st.session_state.user_email = email
            st.session_state.user_full_name = users[email]["full_name"]
            st.session_state.user_employee_id = users[email]["employee_id"]
            st.session_state.user_department = users[email]["department"]
            st.session_state.user_phone = users[email].get("phone", "")
            st.session_state.user_location = users[email].get("location", "")
            st.session_state.user_bio = users[email].get("bio", "")
            st.session_state.user_join_date = users[email].get("join_date", datetime.now().strftime("%B %Y"))
            
            profile_img_path = get_profile_image(email)
            if profile_img_path and profile_img_path.exists():
                st.session_state.profile_image = str(profile_img_path)
            else:
                st.session_state.profile_image = None
            
            return True
    
    return False

def signup_user(user_data):
    users = load_users()
    
    if user_data["email"] in users:
        return False, "Email already registered"
    
    for existing_user in users.values():
        if existing_user.get("employee_id") == user_data["employee_id"]:
            return False, "Employee ID already registered"
    
    users[user_data["email"]] = {
        "full_name": user_data["full_name"],
        "email": user_data["email"],
        "employee_id": user_data["employee_id"],
        "department": user_data["department"],
        "phone": user_data.get("phone", ""),
        "location": user_data.get("location", ""),
        "bio": user_data.get("bio", ""),
        "password": hash_password(user_data["password"]),
        "join_date": datetime.now().strftime("%B %Y"),
        "created_at": datetime.now().isoformat()
    }
    
    save_users(users)
    
    if user_data.get("profile_image"):
        save_profile_image(user_data["email"], user_data["profile_image"])
    
    return True, "Account created successfully"

def reset_password(email, new_password):
    users = load_users()
    
    if email in users:
        users[email]["password"] = hash_password(new_password)
        save_users(users)
        return True
    return False

def update_user_profile(email, updates):
    users = load_users()
    
    if email in users:
        for key, value in updates.items():
            if value:
                users[email][key] = value
        
        save_users(users)
        
        if "full_name" in updates:
            st.session_state.user_full_name = updates["full_name"]
        if "phone" in updates:
            st.session_state.user_phone = updates["phone"]
        if "location" in updates:
            st.session_state.user_location = updates["location"]
        if "bio" in updates:
            st.session_state.user_bio = updates["bio"]
        
        return True
    return False

def logout_user():
    st.session_state.authenticated = False
    st.session_state.user_email = ""
    st.session_state.user_full_name = ""
    st.session_state.user_employee_id = ""
    st.session_state.user_department = ""
    st.session_state.user_phone = ""
    st.session_state.user_location = ""
    st.session_state.user_bio = ""
    st.session_state.profile_image = None
    st.session_state.chat_history = []
    st.session_state.query_count = 0
    st.session_state.total_response_time = 0
    st.rerun()

# ===============================
# SESSION STATE INITIALIZATION
# ===============================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "user_full_name" not in st.session_state:
    st.session_state.user_full_name = ""
if "user_employee_id" not in st.session_state:
    st.session_state.user_employee_id = ""
if "user_department" not in st.session_state:
    st.session_state.user_department = ""
if "user_phone" not in st.session_state:
    st.session_state.user_phone = ""
if "user_location" not in st.session_state:
    st.session_state.user_location = ""
if "user_bio" not in st.session_state:
    st.session_state.user_bio = ""
if "user_join_date" not in st.session_state:
    st.session_state.user_join_date = ""
if "profile_image" not in st.session_state:
    st.session_state.profile_image = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "query_count" not in st.session_state:
    st.session_state.query_count = 0
if "total_response_time" not in st.session_state:
    st.session_state.total_response_time = 0
if "reset_email" not in st.session_state:
    st.session_state.reset_email = ""
if "reset_verified" not in st.session_state:
    st.session_state.reset_verified = False
if "show_forgot_password" not in st.session_state:
    st.session_state.show_forgot_password = False

# ===============================
# CUSTOM CSS FOR MAHINDRA BRANDING
# ===============================
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}
    
    .stApp {{
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #ffffff 0%, {MAHINDRA_LIGHT_GRAY} 100%);
    }}
    
    /* Main container */
    .main-container {{
        display: flex;
        min-height: 100vh;
        width: 100%;
    }}
    
    /* Left Section */
    .left-section {{
        width: 50%;
        background: linear-gradient(135deg, {MAHINDRA_DARK_GRAY} 0%, {MAHINDRA_GRAY} 100%);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        padding: 3rem;
        position: fixed;
        left: 0;
        top: 0;
        bottom: 0;
        overflow-y: auto;
    }}
    
    /* Right Section */
    .right-section {{
        width: 50%;
        margin-left: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        padding: 2rem;
        background: white;
    }}
    
    .auth-card {{
        width: 100%;
        max-width: 480px;
        background: white;
        border-radius: 24px;
        padding: 2rem;
    }}
    
    .auth-header {{
        text-align: center;
        margin-bottom: 2rem;
    }}
    
    .auth-header h2 {{
        color: {MAHINDRA_DARK_GRAY};
        font-size: 1.8rem;
        margin-bottom: 0.5rem;
    }}
    
    .auth-header p {{
        color: {MAHINDRA_GRAY};
        font-size: 0.9rem;
    }}
    
    /* Form Styles */
    .stTextInput > div > div > input {{
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 0.75rem;
        font-size: 0.95rem;
    }}
    
    .stTextInput > div > div > input:focus {{
        border-color: {MAHINDRA_RED};
        box-shadow: 0 0 0 2px rgba(215,25,32,0.1);
    }}
    
    .stSelectbox > div > div {{
        border-radius: 10px;
        border: 2px solid #e0e0e0;
    }}
    
    .stTextArea > div > div > textarea {{
        border-radius: 10px;
        border: 2px solid #e0e0e0;
    }}
    
    /* Button Styles */
    .stButton > button {{
        background: linear-gradient(135deg, {MAHINDRA_RED} 0%, {MAHINDRA_DARK_RED} 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(215,25,32,0.3);
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 1rem;
        background-color: transparent;
        border-bottom: 2px solid #e0e0e0;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        font-size: 1rem;
        font-weight: 500;
        padding: 0.75rem 1rem;
    }}
    
    .stTabs [aria-selected="true"] {{
        color: {MAHINDRA_RED};
        border-bottom-color: {MAHINDRA_RED};
    }}
    
    /* Badge */
    .badge {{
        display: inline-block;
        padding: 0.25rem 0.75rem;
        background: {MAHINDRA_RED};
        color: white;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
    }}
    
    /* Feature items */
    .feature-item {{
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.5rem;
        color: white;
    }}
    
    .feature-icon {{
        width: 45px;
        height: 45px;
        background: rgba(215,25,32,0.2);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
    }}
    
    .feature-text {{
        flex: 1;
    }}
    
    .feature-text strong {{
        display: block;
        margin-bottom: 0.25rem;
        font-size: 1rem;
    }}
    
    .feature-text small {{
        font-size: 0.85rem;
        opacity: 0.8;
    }}
    
    @keyframes shimmer {{
        0% {{ transform: translate(0,0); }}
        100% {{ transform: translate(50px,50px); }}
    }}
    
    .animated-bg {{
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(215,25,32,0.1) 1%, transparent 1%);
        background-size: 50px 50px;
        animation: shimmer 20s linear infinite;
    }}
</style>
""", unsafe_allow_html=True)
# ===============================
# AUTH PAGE WITH SPLIT LAYOUT
# ===============================
def show_auth_page():
    # Load company logo from local file
    try:
        # Update this path to your actual logo file location
        logo_path = "images/company_logo.png"  # Change this to your logo path
        if os.path.exists(logo_path):
            company_logo = Image.open(logo_path)
        else:
            company_logo = None
            st.warning(f"Logo not found at {logo_path}. Using default logo.")
    except Exception as e:
        company_logo = None
        st.warning(f"Error loading logo: {e}")
    
    # Initialize session state for tab tracking
    if 'auth_tab' not in st.session_state:
        st.session_state.auth_tab = "Login"
    
    # Add custom CSS for full-width footer and professional icons
    st.markdown("""
    <style>
    /* CRITICAL FIX: Remove all white space */
    html, body, .stApp {
        height: 100%;
        margin: 0;
        padding: 0;
    }
    
    .stApp {
        display: flex;
        flex-direction: column;
    }
    
    .main {
        flex: 1;
        display: flex;
        flex-direction: column;
    }
    
    /* Remove all default Streamlit padding */
    .main .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
    }
    
    /* Hide Streamlit's default footer */
    footer {
        display: none !important;
    }
    
    /* Remove any extra spacing from headers */
    header {
        display: none !important;
    }
    
    /* Professional Feature Icons */
    .feature-icon-pro {
        width: 50px;
        height: 50px;
        background: linear-gradient(135deg, #e03a3e, #b82b2f);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
        flex-shrink: 0;
    }
    
    .feature-icon-pro:hover {
        transform: translateY(-2px);
    }
    
    .feature-icon-pro svg {
        width: 28px;
        height: 28px;
        fill: white;
    }
    
    .feature-text-pro {
        flex: 1;
    }
    
    .feature-text-pro strong {
        font-size: 1rem;
        color: #333;
        display: block;
        margin-bottom: 0.25rem;
    }
    
    .feature-text-pro small {
        font-size: 0.85rem;
        color: #666;
        line-height: 1.4;
    }
    
    .feature-row {
        display: flex;
        align-items: center;
        margin-bottom: 1.5rem;
        padding: 0.75rem;
        border-radius: 12px;
        transition: background 0.3s ease;
    }
    
    .feature-row:hover {
        background: rgba(224, 58, 62, 0.05);
    }
    
    /* Full Width Footer Styles */
    .footer-full {
        width: 100vw;
        position: relative;
        left: 50%;
        right: 50%;
        margin-left: -50vw;
        margin-right: -50vw;
        margin-top: auto;
        background: linear-gradient(135deg, #1a1a1a 0%, #2c2c2c 100%);
        color: #ffffff;
        border-top: 3px solid #e03a3e;
    }
    
    .footer-content {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem 2rem 1.5rem 2rem;
    }
    
    .footer-main {
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 2rem;
        margin-bottom: 2rem;
    }
    
    .footer-section {
        flex: 1;
        min-width: 200px;
        text-align: left;
    }
    
    .footer-section h4 {
        color: #e03a3e;
        margin-bottom: 1rem;
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    .footer-section p {
        color: rgba(255,255,255,0.8);
        font-size: 0.85rem;
        line-height: 1.5;
        margin: 0.5rem 0;
    }
    
    .footer-links {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .footer-links a {
        color: rgba(255,255,255,0.8);
        text-decoration: none;
        font-size: 0.85rem;
        transition: color 0.3s ease;
    }
    
    .footer-links a:hover {
        color: #e03a3e;
    }
    
    .footer-social {
        display: flex;
        gap: 1.5rem;
        margin-top: 1rem;
        flex-wrap: wrap;
    }
    
    .footer-social a {
        color: rgba(255,255,255,0.8);
        text-decoration: none;
        transition: all 0.3s ease;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.9rem;
    }
    
    .footer-social a:hover {
        color: #e03a3e;
        transform: translateY(-2px);
    }
    
    .footer-social img {
        width: 20px;
        height: 20px;
        filter: brightness(0) invert(1);
        transition: filter 0.3s ease;
    }
    
    .footer-social a:hover img {
        filter: brightness(0) saturate(100%) invert(32%) sepia(89%) saturate(1832%) hue-rotate(334deg) brightness(92%) contrast(91%);
    }
    
    .footer-bottom {
        border-top: 1px solid rgba(255,255,255,0.1);
        padding-top: 1.5rem;
        text-align: center;
        font-size: 0.8rem;
        color: rgba(255,255,255,0.6);
    }
    
    /* Ensure content container has proper spacing */
    .content-container {
        flex: 1;
        padding: 2rem;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .footer-content {
            padding: 2rem 1rem 1.5rem 1rem;
        }
        .footer-main {
            flex-direction: column;
            text-align: center;
        }
        .footer-section {
            text-align: center;
        }
        .footer-social {
            justify-content: center;
        }
        .content-container {
            padding: 1rem;
        }
        .feature-row {
            padding: 0.5rem;
        }
        .feature-icon-pro {
            width: 40px;
            height: 40px;
        }
        .feature-icon-pro svg {
            width: 22px;
            height: 22px;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Wrap main content in a container with proper spacing
    st.markdown('<div class="content-container">', unsafe_allow_html=True)
    
    # Create two columns
    col_left, col_right = st.columns([1, 1], gap="large")
    
    # LEFT SECTION - Mahindra Branding
    with col_left:
        # Logo and title
        if company_logo:
            # Display actual company logo
            col_logo, col_logo_center, col_logo2 = st.columns([1, 2, 1])
            with col_logo_center:
                st.image(company_logo, width=150)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                f"""
                <div style="text-align: center;">
                    <h1 style="color: {MAHINDRA_DARK_GRAY}; margin-bottom: 1rem;">Mahindra Rise</h1>
                    <p style="color: {MAHINDRA_GRAY}; font-size: 1.1rem;">AI-Powered Policy Assistant</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            # Default logo (colored box with M)
            st.markdown(
                f"""
                <div style="text-align: center; padding: 2rem;">
                    <div style="width: 120px; height: 120px; background: linear-gradient(135deg, {MAHINDRA_RED}, {MAHINDRA_DARK_RED}); 
                                border-radius: 30px; display: flex; align-items: center; justify-content: center; 
                                margin: 0 auto 2rem;">
                        <span style="font-size: 4rem; font-weight: bold; color: white;">M</span>
                    </div>
                    <h1 style="color: {MAHINDRA_DARK_GRAY}; margin-bottom: 1rem;">Mahindra Rise</h1>
                    <p style="color: {MAHINDRA_GRAY}; font-size: 1.1rem;">AI-Powered Policy Assistant</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Feature items - Show only when auth_tab is "Sign Up"
        if st.session_state.auth_tab == "Sign Up":
            st.markdown("""
            <div class="feature-row">
                <div class="feature-icon-pro">
                    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
                    </svg>
                </div>
                <div class="feature-text-pro">
                    <strong>Instant Policy Access</strong>
                    <small>Get answers in seconds from official documents</small>
                </div>
            </div>
            <div class="feature-row">
                <div class="feature-icon-pro">
                    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path d="M4 6h16v2H4V6zm2-4h12v2H6V2zm16 8H2v12h20V10zm-4 6h-4v-2h4v2z"/>
                    </svg>
                </div>
                <div class="feature-text-pro">
                    <strong>7 Policy Categories</strong>
                    <small>HR, Travel, IT Security, Safety & more</small>
                </div>
            </div>
            <div class="feature-row">
                <div class="feature-icon-pro">
                    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z"/>
                    </svg>
                </div>
                <div class="feature-text-pro">
                    <strong>Secure & Compliant</strong>
                    <small>Enterprise-grade security with data protection</small>
                </div>
            </div>
            <div class="feature-row">
                <div class="feature-icon-pro">
                    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13h-1v6l5.25 3.15.75-1.23-4.5-2.67z"/>
                    </svg>
                </div>
                <div class="feature-text-pro">
                    <strong>24/7 Availability</strong>
                    <small>Always here to help with your policy queries</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # RIGHT SECTION - Login/Signup Forms
    with col_right:
        if st.session_state.show_forgot_password:
            show_forgot_password_flow()
        else:
            # Welcome header
            st.markdown(
                """
                <div style="text-align: center; margin-bottom: 2rem;">
                    <h2>Welcome Back</h2>
                    <p style="color: #666;">Sign in to access Mahindra Policy Assistant</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Create tabs with custom buttons to track active tab
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(" Login", use_container_width=True, 
                           type="primary" if st.session_state.auth_tab == "Login" else "secondary"):
                    st.session_state.auth_tab = "Login"
                    st.rerun()
            
            with col2:
                if st.button(" Sign Up", use_container_width=True,
                           type="primary" if st.session_state.auth_tab == "Sign Up" else "secondary"):
                    st.session_state.auth_tab = "Sign Up"
                    st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            
            # Show Login or Sign Up form based on active tab
            if st.session_state.auth_tab == "Login":
                with st.form("login_form"):
                    email = st.text_input("Email Address", placeholder="john.doe@mahindra.com")
                    password = st.text_input("Password", type="password", placeholder="Enter your password")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        submit = st.form_submit_button("Login", use_container_width=True)
                    with col2:
                        if st.form_submit_button("Forgot Password?", use_container_width=True):
                            st.session_state.show_forgot_password = True
                            st.rerun()
                    
                    if submit:
                        if email and password:
                            if login_user(email, password):
                                st.success("Login successful! Redirecting...")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Invalid email or password")
                        else:
                            st.warning("Please enter both email and password")
            
            else:  # Sign Up tab
                with st.form("signup_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        full_name = st.text_input("Full Name *", placeholder="John Doe")
                        email = st.text_input("Email Address *", placeholder="john.doe@mahindra.com")
                        employee_id = st.text_input("Employee ID *", placeholder="EMP12345")
                        phone = st.text_input("Phone Number", placeholder="+91 12345 67890")
                    
                    with col2:
                        department = st.selectbox("Department *", [
                            "Select Department",
                            "Engineering", "HR", "IT", "Finance", 
                            "Operations", "Sales", "Marketing", "Legal"
                        ])
                        location = st.text_input("Location", placeholder="Mumbai, India")
                        bio = st.text_area("Bio", placeholder="Tell us about yourself...", height=80)
                    
                    password = st.text_input("Password *", type="password", placeholder="Minimum 8 characters")
                    confirm_password = st.text_input("Confirm Password *", type="password", placeholder="Re-enter password")
                    
                    st.markdown("#### Profile Picture")
                    profile_image = st.file_uploader("Upload profile picture (optional)", type=['jpg', 'jpeg', 'png'])
                    
                    if profile_image:
                        try:
                            img = Image.open(profile_image)
                            st.image(img, width=100, caption="Preview")
                        except:
                            st.error("Invalid image file")
                    
                    st.caption("* Required fields")
                    
                    submit = st.form_submit_button("Create Account", use_container_width=True)
                    
                    if submit:
                        if not all([full_name, email, employee_id, department != "Select Department", password]):
                            st.error("Please fill all required fields")
                        elif password != confirm_password:
                            st.error("Passwords do not match")
                        elif len(password) < 8:
                            st.error("Password must be at least 8 characters")
                        else:
                            user_data = {
                                "full_name": full_name,
                                "email": email,
                                "employee_id": employee_id,
                                "department": department,
                                "phone": phone,
                                "location": location,
                                "bio": bio,
                                "password": password,
                                "profile_image": profile_image
                            }
                            
                            success, message = signup_user(user_data)
                            if success:
                                st.success("Account created successfully! Please login.")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(f"{message}")
    
    # Close content container
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Add full-width professional footer
    st.markdown("""
    <div class="footer-full">
        <div class="footer-content">
            <div class="footer-main">
                <div class="footer-section">
                    <h4>About Mahindra Rise</h4>
                    <p>AI-Powered Policy Assistant helping employees access company policies quickly and efficiently, ensuring compliance and knowledge accessibility across the organization.</p>
                </div>
                <div class="footer-section">
                    <h4>Quick Links</h4>
                    <div class="footer-links">
                        <a href="#">Privacy Policy</a>
                        <a href="#">Terms of Service</a>
                        <a href="#">Security & Compliance</a>
                        <a href="#">Support Center</a>
                        <a href="#">FAQs</a>
                    </div>
                </div>
                <div class="footer-section">
                    <h4>Contact Us</h4>
                    <p>📧 support@mahindra.com</p>
                    <p>📞 +91 22 1234 5678</p>
                    <p>📍 Mahindra Towers, Mumbai, India</p>
                    <p>⏰ Mon-Fri: 9:00 AM - 6:00 PM</p>
                </div>
                <div class="footer-section">
                    <h4>Connect With Us</h4>
                    <div class="footer-social">
                        <a href="https://www.linkedin.com/company/mahindra" target="_blank">
                            <img src="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/linkedin.svg">
                            LinkedIn
                        </a>
                        <a href="https://twitter.com/MahindraRise" target="_blank">
                            <img src="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/twitter.svg">
                            Twitter
                        </a>
                        <a href="https://www.facebook.com/MahindraRise" target="_blank">
                            <img src="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/facebook.svg">
                            Facebook
                        </a>
                        <a href="https://www.instagram.com/mahindrarise" target="_blank">
                            <img src="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg">
                            Instagram
                        </a>
                        <a href="https://www.youtube.com/c/MahindraRise" target="_blank">
                            <img src="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/youtube.svg">
                            YouTube
                        </a>
                    </div>
                </div>
            </div>
            <div class="footer-bottom">
                © 2024 Mahindra Group. All rights reserved. | Empowering People to Rise | Version 1.0
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_forgot_password_flow():
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 2rem;">
            <h2>Reset Password</h2>
            <p style="color: #666;">Enter your email to receive OTP</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    if not st.session_state.reset_verified:
        with st.form("forgot_password_form"):
            email = st.text_input("Email Address", placeholder="john.doe@mahindra.com")
            contact_method = st.radio("Receive OTP via", ["Email", "SMS"], horizontal=True)
            
            phone = ""
            if contact_method == "SMS":
                phone = st.text_input("Phone Number", placeholder="+91 12345 67890")
            
            col1, col2 = st.columns(2)
            with col1:
                send_otp = st.form_submit_button("Send OTP", use_container_width=True)
            with col2:
                if st.form_submit_button("Back to Login", use_container_width=True):
                    st.session_state.show_forgot_password = False
                    st.session_state.reset_verified = False
                    st.rerun()
            
            if send_otp:
                users = load_users()
                if email in users:
                    st.session_state.reset_email = email
                    otp = otp_manager.generate_otp(email)
                    
                    if contact_method == "Email":
                        success = otp_manager.send_otp_email(email, otp)
                        if success:
                            st.success(f"OTP sent to {email}")
                            st.session_state.show_otp_input = True
                        else:
                            st.error("Failed to send email. Please check email configuration.")
                    else:
                        if phone:
                            try:
                                parsed_number = phonenumbers.parse(phone, "IN")
                                formatted_phone = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
                                success = otp_manager.send_otp_sms(formatted_phone, otp)
                                if success:
                                    st.success(f"OTP sent to {phone}")
                                    st.session_state.show_otp_input = True
                                else:
                                    st.error("Failed to send SMS. Please check SMS configuration.")
                            except:
                                st.error("Invalid phone number format. Please use format: +91 12345 67890")
                        else:
                            st.error("Please enter phone number")
                else:
                    st.error("Email not registered")
        
        if st.session_state.get("show_otp_input", False):
            st.markdown("---")
            with st.form("verify_otp_form"):
                otp = st.text_input("Enter OTP", placeholder="6-digit code", max_chars=6)
                
                col1, col2 = st.columns(2)
                with col1:
                    verify = st.form_submit_button("Verify OTP", use_container_width=True)
                with col2:
                    resend = st.form_submit_button("Resend OTP", use_container_width=True)
                
                if verify:
                    if otp and otp_manager.verify_otp(st.session_state.reset_email, otp):
                        st.success("OTP verified!")
                        st.session_state.reset_verified = True
                        st.session_state.show_otp_input = False
                        st.rerun()
                    else:
                        st.error("Invalid or expired OTP")
                
                if resend:
                    otp = otp_manager.generate_otp(st.session_state.reset_email)
                    otp_manager.send_otp_email(st.session_state.reset_email, otp)
                    st.success("New OTP sent!")
    
    else:
        with st.form("reset_password_form"):
            new_password = st.text_input("New Password", type="password", placeholder="Minimum 8 characters")
            confirm_password = st.text_input("Confirm New Password", type="password", placeholder="Re-enter new password")
            
            col1, col2 = st.columns(2)
            with col1:
                reset = st.form_submit_button("Reset Password", use_container_width=True)
            with col2:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state.show_forgot_password = False
                    st.session_state.reset_verified = False
                    st.session_state.reset_email = ""
                    st.rerun()
            
            if reset:
                if new_password and confirm_password:
                    if new_password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(new_password) < 8:
                        st.error("Password must be at least 8 characters")
                    else:
                        if reset_password(st.session_state.reset_email, new_password):
                            st.success("Password reset successfully! Please login.")
                            time.sleep(2)
                            st.session_state.show_forgot_password = False
                            st.session_state.reset_verified = False
                            st.session_state.reset_email = ""
                            st.rerun()
                        else:
                            st.error("Failed to reset password")
                else:
                    st.warning("Please enter new password")
# ===============================
# QUERY FUNCTION
# ===============================
API_URL = os.environ.get("API_URL", "http://localhost:8000/api/v1")

def query_policy(question):
    try:
        start = time.time()
        
        headers = {}
        if st.session_state.user_email:
            headers["X-User-Email"] = st.session_state.user_email
        
        res = requests.post(
            f"{API_URL}/query",
            json={"question": question},
            headers=headers,
            timeout=30
        )
        
        response_time = (time.time() - start) * 1000
        
        if res.status_code == 200:
            data = res.json()
            data["response_time"] = response_time
            return data
        else:
            st.error(f"Server error: {res.status_code}")
            return None
    
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None

# ===============================
# MAIN APP UI
# ===============================
def main_app():
    # Get profile image
    profile_img_base64 = ""
    profile_image_exists = False
    
    if st.session_state.profile_image and Path(st.session_state.profile_image).exists():
        try:
            with open(st.session_state.profile_image, "rb") as img_file:
                profile_img_base64 = base64.b64encode(img_file.read()).decode()
                profile_image_exists = True
        except:
            pass
    
    # Header with profile image - using st.image() approach
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #2C2C2C, #4A4A4A); padding: 1rem 2rem; border-radius: 0px 0px 20px 20px; margin-bottom: 2rem;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="width: 50px; height: 50px; background: linear-gradient(135deg, #D71920, #A5151C); border-radius: 12px; display: flex; align-items: center; justify-content: center;">
                    <span style="font-size: 1.5rem; font-weight: bold; color: white;">M</span>
                </div>
                <div>
                    <h1 style="color: white; margin: 0;">Mahindra Rise</h1>
                    <p style="color: rgba(255,255,255,0.8); margin: 0;">AI-Powered Policy Assistant</p>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 1rem; background: rgba(255,255,255,0.1); padding: 0.5rem 1rem; border-radius: 50px;">
                <div id="profile-avatar" style="width: 40px; height: 40px; border-radius: 50%;">
                </div>
                <div style="color: white;">
                    <strong>{st.session_state.user_full_name}</strong><br>
                    <small>{st.session_state.user_department}</small>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Use st.image to display the profile picture in the header
    if profile_image_exists:
        # Create columns to position the image in the header
        # This uses the placeholder div we created above
        st.markdown(f"""
        <style>
            #profile-avatar {{
                background-image: url(data:image/jpeg;base64,{profile_img_base64});
                background-size: cover;
                background-position: center;
            }}
        </style>
        """, unsafe_allow_html=True)
    else:
        # Show initials
        initial = st.session_state.user_full_name[0].upper() if st.session_state.user_full_name else "U"
        st.markdown(f"""
        <style>
            #profile-avatar {{
                background: {MAHINDRA_RED};
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                font-size: 1rem;
            }}
        </style>
        <script>
            // This is a workaround - better to use the HTML approach for initials
        </script>
        """, unsafe_allow_html=True)
        
        # For initials, we need to add the text content
        st.markdown(f"""
        <div style="display: none;" id="initial-content">{initial}</div>
        <script>
            var avatarDiv = document.getElementById('profile-avatar');
            if (avatarDiv && !avatarDiv.style.backgroundImage) {{
                avatarDiv.innerHTML = '{initial}';
                avatarDiv.style.display = 'flex';
                avatarDiv.style.alignItems = 'center';
                avatarDiv.style.justifyContent = 'center';
                avatarDiv.style.color = 'white';
                avatarDiv.style.fontWeight = 'bold';
                avatarDiv.style.fontSize = '1rem';
            }}
        </script>
        """, unsafe_allow_html=True)
    
    # Welcome Banner
    current_hour = datetime.now().hour
    greeting = "Good morning" if current_hour < 12 else "Good afternoon" if current_hour < 17 else "Good evening"
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {MAHINDRA_RED}, {MAHINDRA_DARK_RED}); padding: 1rem 1.5rem; border-radius: 12px; margin-bottom: 1.5rem; color: white;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h3 style="margin: 0;">{greeting}, {st.session_state.user_full_name.split()[0]}! 👋</h3>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">How can I assist you with Mahindra policies today?</p>
            </div>
            <div style="display: flex; gap: 0.5rem;">
                <span class="badge">7 Policies</span>
                <span class="badge">24/7 Support</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation Menu
    tab1, tab2, tab3 = st.tabs(["Ask Question", "Chat History", "My Profile"])
    
    # ASK QUESTION PAGE
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### Ask Your Question")
            
            question = st.text_area(
                "",
                height=120,
                placeholder="Example: What is the paternity leave policy? How many days are employees entitled to?",
                key="question_input"
            )
            
            
           
            
            
            
            if st.button("Get Answer", type="primary", use_container_width=True):
                if question:
                    with st.spinner("🔍 Searching policy documents..."):
                        result = query_policy(question)
                        
                        if result:
                            st.session_state.query_count += 1
                            st.session_state.total_response_time += result.get('response_time', 0)
                            
                            st.session_state.chat_history.append({
                                "question": question,
                                "answer": result["answer"],
                                "sources": result.get("sources", []),
                                "timestamp": datetime.now(),
                                "response_time": result.get('response_time', 0)
                            })
                            
                            st.markdown('<div style="background: linear-gradient(135deg, #f8f9fa, #ffffff); padding: 1.5rem; border-radius: 12px; margin: 1rem 0; border-left: 4px solid #D71920;">', unsafe_allow_html=True)
                            st.markdown("### Answer")
                            st.write(result["answer"])
                            
                            if result.get("sources"):
                                avg_score = sum(s.get("relevance_score", 0) for s in result["sources"]) / len(result["sources"])
                                st.markdown(f"""
                                <div style="margin-top: 1rem;">
                                    <span class="badge">Confidence: {avg_score:.1%}</span>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            if result.get("sources"):
                                st.markdown("### Source Documents")
                                for source in result["sources"]:
                                    with st.expander(f"📄 {source.get('document_name', 'Unknown')} - {source.get('section', 'General')}"):
                                        st.write(source.get('content', '')[:500] + "...")
                            
                            st.caption(f"⏱ Response time: {result.get('response_time', 0):.0f}ms")
                else:
                    st.warning("Please enter a question.")
        
        with col2:
            st.markdown("### Quick Stats")
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Total Queries", st.session_state.query_count)
            with col_b:
                avg_time = st.session_state.total_response_time / st.session_state.query_count if st.session_state.query_count > 0 else 0
                st.metric("Avg Response", f"{avg_time:.0f}ms")
            with col_c:
                st.metric("Accuracy", "96.8%")
            
            st.markdown("### Recent Activity")
            if st.session_state.chat_history:
                for chat in st.session_state.chat_history[-3:]:
                    st.markdown(f"""
                    <div style="background: white; padding: 0.75rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 3px solid {MAHINDRA_RED};">
                        <strong>Q:</strong> {chat['question'][:60]}...
                        <br>
                        <small>{chat['timestamp'].strftime('%I:%M %p')}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No queries yet")
            
            st.markdown("---")
            if st.button("🚪 Logout", use_container_width=True, key="logout_stats_panel"):
                logout_user()
    
    # CHAT HISTORY PAGE
    with tab2:
        st.markdown("### Chat History")
        
        if st.session_state.chat_history:
            col1, col2 = st.columns([5, 1])
            with col2:
                if st.button("🗑️ Clear All", use_container_width=True):
                    st.session_state.chat_history = []
                    st.rerun()
            
            st.markdown("---")
            
            for idx, chat in enumerate(reversed(st.session_state.chat_history)):
                with st.container():
                    st.markdown(f"""
                    <div style="background: white; border-radius: 12px; padding: 1rem; margin-bottom: 1rem; border-left: 3px solid {MAHINDRA_RED};">
                        <strong>❓ Question {len(st.session_state.chat_history) - idx}:</strong>
                        <p>{chat['question']}</p>
                        <strong>💡 Answer:</strong>
                        <p>{chat['answer']}</p>
                        <div style="font-size: 0.75rem; color: #666; margin-top: 0.5rem;">
                            {chat['timestamp'].strftime('%B %d, %Y at %I:%M %p')} | ⏱ {chat.get('response_time', 0):.0f}ms
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if chat.get('sources'):
                        with st.expander(f"📚 View {len(chat['sources'])} source(s)"):
                            for source in chat['sources']:
                                st.markdown(f"""
                                <div style="background: {MAHINDRA_LIGHT_GRAY}; padding: 0.75rem; border-radius: 8px; margin-bottom: 0.5rem;">
                                    <strong>{source.get('document_name', 'Unknown')}</strong> - {source.get('section', 'General')}<br>
                                    <small>Relevance: {source.get('relevance_score', 0):.1%}</small>
                                </div>
                                """, unsafe_allow_html=True)
                    
                    st.divider()
        else:
            st.info("📭 No chat history yet. Ask a question to get started!")
    
    # MY PROFILE PAGE - FIXED VERSION
    with tab3:
        st.markdown("### My Profile")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Get profile image for large avatar
            profile_img_base64_large = ""
            try:
                if st.session_state.profile_image and Path(st.session_state.profile_image).exists():
                    with open(st.session_state.profile_image, "rb") as img_file:
                        img_data = img_file.read()
                        profile_img_base64_large = base64.b64encode(img_data).decode()
                elif st.session_state.user_email:
                    profile_img_path = get_profile_image(st.session_state.user_email)
                    if profile_img_path and profile_img_path.exists():
                        with open(profile_img_path, "rb") as img_file:
                            img_data = img_file.read()
                            profile_img_base64_large = base64.b64encode(img_data).decode()
            except Exception as e:
                print(f"Error loading large profile image: {e}")
            
            # Create profile card using Streamlit native components
            if profile_img_base64_large:
                # Show image
                st.image(f"data:image/jpeg;base64,{profile_img_base64_large}", width=120)
            else:
                # Show initials
                initial = st.session_state.user_full_name[0].upper() if st.session_state.user_full_name else "U"
                st.markdown(f"""
                <div style="width: 120px; height: 120px; background: {MAHINDRA_RED}; 
                            border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                            margin: 0 auto;">
                    <span style="font-size: 3rem; color: white; font-weight: bold;">{initial}</span>
                </div>
                """, unsafe_allow_html=True)
            
            # Display name and info using native Streamlit
            st.markdown(f"## {st.session_state.user_full_name}")
            st.markdown(f"### <span style='color: {MAHINDRA_RED};'>{st.session_state.user_department}</span>", unsafe_allow_html=True)
            st.markdown(f"<span style='background: {MAHINDRA_RED}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem;'>{st.session_state.user_employee_id}</span>", unsafe_allow_html=True)
        
        with col2:
            tab1, tab2 = st.tabs(["📋 Profile Info", "✏️ Edit Profile"])
            
            with tab1:
                st.markdown("### Personal Information")
                st.markdown(f"""
                <div style="background: white; padding: 1.5rem; border-radius: 12px;">
                    <p><strong>📧 Email:</strong> {st.session_state.user_email}</p>
                    <p><strong>🆔 Employee ID:</strong> {st.session_state.user_employee_id}</p>
                    <p><strong>🏢 Department:</strong> {st.session_state.user_department}</p>
                    <p><strong>📞 Phone:</strong> {st.session_state.user_phone or 'Not provided'}</p>
                    <p><strong>📍 Location:</strong> {st.session_state.user_location or 'Not provided'}</p>
                    <p><strong>📝 Bio:</strong> {st.session_state.user_bio or 'Not provided'}</p>
                    <p><strong>📅 Member Since:</strong> {st.session_state.user_join_date}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("### Activity Summary")
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Total Queries", st.session_state.query_count)
                with col_b:
                    avg_time = st.session_state.total_response_time / st.session_state.query_count if st.session_state.query_count > 0 else 0
                    st.metric("Avg Response", f"{avg_time:.0f}ms")
                with col_c:
                    st.metric("Accuracy", "96.8%")
            
            with tab2:
                st.markdown("### Edit Profile")
                
                with st.form("edit_profile_form"):
                    full_name = st.text_input("Full Name", value=st.session_state.user_full_name)
                    phone = st.text_input("Phone Number", value=st.session_state.user_phone)
                    location = st.text_input("Location", value=st.session_state.user_location)
                    bio = st.text_area("Bio", value=st.session_state.user_bio, height=100)
                    
                    st.markdown("#### Update Profile Picture")
                    new_profile_image = st.file_uploader("Upload new profile picture", type=['jpg', 'jpeg', 'png'], key="profile_upload")
                    
                    if new_profile_image:
                        try:
                            img = Image.open(new_profile_image)
                            st.image(img, width=100, caption="Preview")
                        except:
                            st.error("Invalid image file")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        submit = st.form_submit_button("Save Changes", use_container_width=True)
                    with col2:
                        if st.form_submit_button("Cancel", use_container_width=True):
                            st.rerun()
                    
                    if submit:
                        updates = {}
                        if full_name != st.session_state.user_full_name:
                            updates["full_name"] = full_name
                        if phone != st.session_state.user_phone:
                            updates["phone"] = phone
                        if location != st.session_state.user_location:
                            updates["location"] = location
                        if bio != st.session_state.user_bio:
                            updates["bio"] = bio
                        
                        if updates:
                            if update_user_profile(st.session_state.user_email, updates):
                                st.success("✅ Profile updated successfully!")
                                time.sleep(1)
                                st.rerun()
                        
                        if new_profile_image:
                            image_path = save_profile_image(st.session_state.user_email, new_profile_image)
                            if image_path:
                                st.session_state.profile_image = image_path
                                st.success("✅ Profile picture updated!")
                                st.rerun()
            
            st.markdown("---")
            if st.button("🚪 Logout", use_container_width=True, key="logout_footer"):
                logout_user()
    
    # Footer
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem; margin-top: 2rem; color: {MAHINDRA_GRAY}; border-top: 1px solid #e0e0e0;">
        <p>© 2024 Mahindra & Mahindra Ltd. | AI-Powered Policy Assistant | Version 3.0</p>
        <p style="font-size: 0.7rem;">Rise. Empower. Transform. | For internal use only</p>
    </div>
    """, unsafe_allow_html=True)

# ===============================
# MAIN EXECUTION
# ===============================
if not st.session_state.authenticated:
    show_auth_page()
else:
    main_app()