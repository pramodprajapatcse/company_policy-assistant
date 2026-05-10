import streamlit as st
import requests
import json
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from streamlit_option_menu import option_menu
import time
from PIL import Image
import io
import base64

# Page configuration
st.set_page_config(
    page_title="Mahindra Rise - AI Policy Assistant",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Mahindra Brand Colors
MAHINDRA_RED = "#D71920"
MAHINDRA_DARK_RED = "#A5151C"
MAHINDRA_GRAY = "#4A4A4A"
MAHINDRA_LIGHT_GRAY = "#F5F5F5"
MAHINDRA_DARK_GRAY = "#2C2C2C"
MAHINDRA_GOLD = "#C5A028"

# API endpoint
API_URL = "http://localhost:8000/api/v1"

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'token' not in st.session_state:
    st.session_state.token = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'query_count' not in st.session_state:
    st.session_state.query_count = 0
if 'total_response_time' not in st.session_state:
    st.session_state.total_response_time = 0
if 'user_feedback' not in st.session_state:
    st.session_state.user_feedback = {}

# Custom CSS
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {{
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #ffffff 0%, {MAHINDRA_LIGHT_GRAY} 100%);
    }}
    
    /* Auth Card */
    .auth-card {{
        max-width: 450px;
        margin: 2rem auto;
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        border: 1px solid rgba(0,0,0,0.05);
    }}
    
    .auth-header {{
        text-align: center;
        margin-bottom: 2rem;
    }}
    
    .auth-logo {{
        width: 80px;
        height: 80px;
        background: linear-gradient(135deg, {MAHINDRA_RED}, {MAHINDRA_DARK_RED});
        border-radius: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1rem;
        font-size: 2.5rem;
        font-weight: bold;
        color: white;
    }}
    
    .auth-title {{
        font-size: 1.8rem;
        font-weight: 700;
        color: {MAHINDRA_DARK_GRAY};
        margin-bottom: 0.5rem;
    }}
    
    .auth-subtitle {{
        color: {MAHINDRA_GRAY};
        font-size: 0.9rem;
    }}
    
    /* Profile Section */
    .profile-header {{
        background: linear-gradient(135deg, {MAHINDRA_DARK_GRAY} 0%, {MAHINDRA_GRAY} 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
    }}
    
    .profile-avatar {{
        width: 80px;
        height: 80px;
        background: {MAHINDRA_RED};
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }}
    
    .profile-info {{
        margin-top: 1rem;
    }}
    
    .profile-field {{
        padding: 0.75rem;
        background: {MAHINDRA_LIGHT_GRAY};
        border-radius: 8px;
        margin-bottom: 0.5rem;
    }}
    
    /* Button Styles */
    .stButton > button {{
        background: linear-gradient(135deg, {MAHINDRA_RED} 0%, {MAHINDRA_DARK_RED} 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(215,25,32,0.3);
    }}
    
    /* Input Styles */
    .stTextInput > div > div > input {{
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        padding: 0.75rem;
    }}
    
    .stTextInput > div > div > input:focus {{
        border-color: {MAHINDRA_RED};
    }}
    
    /* Tab Styles */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 2rem;
        background-color: transparent;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        font-size: 1rem;
        font-weight: 500;
    }}
    
    /* Main Header */
    .mahindra-header {{
        background: linear-gradient(135deg, {MAHINDRA_DARK_GRAY} 0%, {MAHINDRA_GRAY} 100%);
        padding: 1.5rem 2rem;
        border-radius: 0px 0px 20px 20px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }}
    
    .header-content {{
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}
    
    .logo-section {{
        display: flex;
        align-items: center;
        gap: 1rem;
    }}
    
    .logo-placeholder {{
        width: 50px;
        height: 50px;
        background: linear-gradient(135deg, {MAHINDRA_RED}, {MAHINDRA_DARK_RED});
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        font-weight: bold;
        color: white;
    }}
    
    .user-menu {{
        display: flex;
        align-items: center;
        gap: 1rem;
        background: rgba(255,255,255,0.1);
        padding: 0.5rem 1rem;
        border-radius: 50px;
    }}
    
    .user-avatar {{
        width: 35px;
        height: 35px;
        background: {MAHINDRA_RED};
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
    }}
    
    /* Answer Box */
    .answer-box {{
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        padding: 2rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 4px solid {MAHINDRA_RED};
    }}
    
    /* Badge */
    .badge {{
        display: inline-block;
        padding: 0.25rem 0.75rem;
        background: {MAHINDRA_RED};
        color: white;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }}
</style>
""", unsafe_allow_html=True)

def query_policy(question, token):
    """Send query to API with authentication"""
    try:
        start_time = time.time()
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            f"{API_URL}/query",
            json={
                "question": question,
                "user_id": st.session_state.user.get('user_id', 'anonymous'),
                "top_k": 5
            },
            headers=headers,
            timeout=30
        )
        response_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            result = response.json()
            result['api_response_time'] = response_time
            return result
        elif response.status_code == 401:
            st.session_state.authenticated = False
            st.error("Session expired. Please login again.")
            return None
        else:
            st.error(f"Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None

def login_user(email, password):
    """Login user"""
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            json={"email": email, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.authenticated = True
            st.session_state.user = data['user']
            st.session_state.token = data['access_token']
            return True
        else:
            st.error("Invalid email or password")
            return False
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return False

def signup_user(user_data):
    """Signup new user"""
    try:
        response = requests.post(
            f"{API_URL}/auth/signup",
            json=user_data
        )
        
        if response.status_code == 200:
            st.success("Account created successfully! Please login.")
            return True
        else:
            error_detail = response.json().get('detail', 'Signup failed')
            st.error(error_detail)
            return False
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return False

def logout_user():
    """Logout user"""
    if st.session_state.token:
        try:
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            requests.post(f"{API_URL}/auth/logout", headers=headers)
        except:
            pass
    
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.token = None
    st.session_state.chat_history = []
    st.session_state.query_count = 0
    st.rerun()

def update_profile(updates):
    """Update user profile"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.put(
            f"{API_URL}/auth/me",
            json=updates,
            headers=headers
        )
        
        if response.status_code == 200:
            st.session_state.user = response.json()
            st.success("Profile updated successfully!")
            return True
        else:
            st.error("Failed to update profile")
            return False
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return False

def change_password(old_password, new_password):
    """Change user password"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.post(
            f"{API_URL}/auth/change-password",
            params={"old_password": old_password, "new_password": new_password},
            headers=headers
        )
        
        if response.status_code == 200:
            st.success("Password changed successfully!")
            return True
        else:
            st.error("Failed to change password")
            return False
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return False

def main_app():
    """Main application after authentication"""
    
    # Header with user menu
    st.markdown(f"""
    <div class="mahindra-header">
        <div class="header-content">
            <div class="logo-section">
                <div class="logo-placeholder">M</div>
                <div>
                    <h1 style="color: white; margin: 0;">Mahindra Rise</h1>
                    <p style="color: rgba(255,255,255,0.8); margin: 0;">AI-Powered Policy Assistant</p>
                </div>
            </div>
            <div class="user-menu">
                <div class="user-avatar">{st.session_state.user['full_name'][0].upper()}</div>
                <div style="color: white;">
                    <strong>{st.session_state.user['full_name']}</strong><br>
                    <small>{st.session_state.user['employee_id']} | {st.session_state.user['department']}</small>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation menu
    selected = option_menu(
        menu_title=None,
        options=["Ask Question", "My Profile", "Policy Directory", "Analytics", "Help"],
        icons=["chat-square-text", "person-circle", "journal-bookmark", "graph-up", "info-circle"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "white", "border-radius": "12px", "margin-bottom": "2rem"},
            "icon": {"color": MAHINDRA_GRAY, "font-size": "18px"},
            "nav-link": {
                "font-size": "15px",
                "text-align": "center",
                "margin": "0px",
                "--hover-color": f"rgba(215,25,32,0.05)",
                "color": MAHINDRA_GRAY,
                "font-weight": "500"
            },
            "nav-link-selected": {"background-color": MAHINDRA_RED, "color": "white"},
        }
    )
    
    if selected == "Ask Question":
        ask_question_tab()
    elif selected == "My Profile":
        profile_tab()
    elif selected == "Policy Directory":
        policy_directory_tab()
    elif selected == "Analytics":
        analytics_tab()
    elif selected == "Help":
        help_tab()

def ask_question_tab():
    """Ask question interface"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Ask Mahindra Policy Assistant")
        
        question = st.text_area(
            "",
            height=120,
            placeholder="Example: What is the paternity leave policy for Mahindra employees?",
            key="question_input"
        )
        
        st.markdown("**Quick Examples:**")
        example_cols = st.columns(3)
        examples = [
            "Annual leave policy?",
            "Travel reimbursement limits?",
            "IT security guidelines?"
        ]
        
        for idx, (col, example) in enumerate(zip(example_cols, examples)):
            with col:
                if st.button(example, key=f"example_{idx}"):
                    question = example
                    st.rerun()
        
        if st.button("Get Answer", type="primary", use_container_width=True):
            if question:
                with st.spinner("Searching policy documents..."):
                    result = query_policy(question, st.session_state.token)
                    
                    if result:
                        st.session_state.query_count += 1
                        st.session_state.total_response_time += result.get('api_response_time', 0)
                        
                        st.session_state.chat_history.append({
                            "question": question,
                            "answer": result["answer"],
                            "sources": result["sources"],
                            "timestamp": datetime.now()
                        })
                        
                        st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                        st.markdown("### Answer")
                        st.write(result["answer"])
                        
                        if result["sources"]:
                            avg_score = sum(s["relevance_score"] for s in result["sources"]) / len(result["sources"])
                            st.markdown(f"""
                            <div style="margin-top: 1rem;">
                                <span class="badge">Confidence: {avg_score:.1%}</span>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        if result["sources"]:
                            st.markdown("### Source Documents")
                            for i, source in enumerate(result["sources"], 1):
                                with st.expander(f"📄 {source['document_name']} - {source['section']}"):
                                    st.markdown(f"**Relevance:** {source['relevance_score']:.1%}")
                                    st.markdown(f"**Content:** {source['content'][:500]}...")
                        
                        st.caption(f"Response time: {result.get('api_response_time', 0):.0f}ms")
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
            for chat in st.session_state.chat_history[-5:]:
                with st.container():
                    st.markdown(f"""
                    <div style="background: white; padding: 0.75rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 3px solid {MAHINDRA_RED};">
                        <strong>Q:</strong> {chat['question'][:80]}...<br>
                        <small>{chat['timestamp'].strftime('%I:%M %p')}</small>
                    </div>
                    """, unsafe_allow_html=True)

def profile_tab():
    """User profile management"""
    st.markdown("### My Profile")
    
    user = st.session_state.user
    
    # Profile header
    st.markdown(f"""
    <div class="profile-header">
        <div class="profile-avatar">{user['full_name'][0].upper()}</div>
        <h2>{user['full_name']}</h2>
        <p>{user['role'].upper()} • {user['employee_id']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Profile Information", "Edit Profile", "Change Password"])
    
    with tab1:
        st.markdown("### Personal Information")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="profile-field">
                <strong>Email:</strong><br>
                {user['email']}
            </div>
            <div class="profile-field">
                <strong>Employee ID:</strong><br>
                {user['employee_id']}
            </div>
            <div class="profile-field">
                <strong>Department:</strong><br>
                {user['department']}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="profile-field">
                <strong>Phone Number:</strong><br>
                {user.get('phone_number', 'Not provided')}
            </div>
            <div class="profile-field">
                <strong>Location:</strong><br>
                {user.get('location', 'Not provided')}
            </div>
            <div class="profile-field">
                <strong>Joined:</strong><br>
                {user.get('created_at', 'N/A')[:10] if user.get('created_at') else 'N/A'}
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### Edit Profile Information")
        
        with st.form("edit_profile_form"):
            full_name = st.text_input("Full Name", value=user['full_name'])
            phone = st.text_input("Phone Number", value=user.get('phone_number', ''))
            location = st.text_input("Location", value=user.get('location', ''))
            
            submitted = st.form_submit_button("Update Profile")
            
            if submitted:
                updates = {}
                if full_name != user['full_name']:
                    updates['full_name'] = full_name
                if phone != user.get('phone_number'):
                    updates['phone_number'] = phone
                if location != user.get('location'):
                    updates['location'] = location
                
                if updates:
                    if update_profile(updates):
                        st.rerun()
    
    with tab3:
        st.markdown("### Change Password")
        
        with st.form("change_password_form"):
            old_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            submitted = st.form_submit_button("Change Password")
            
            if submitted:
                if not old_password or not new_password:
                    st.error("Please fill all fields")
                elif new_password != confirm_password:
                    st.error("New passwords do not match")
                elif len(new_password) < 8:
                    st.error("Password must be at least 8 characters")
                else:
                    if change_password(old_password, new_password):
                        st.rerun()
    
    # Logout button
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        logout_user()

def policy_directory_tab():
    """Policy directory"""
    st.markdown("### Mahindra Policy Document Directory")
    
    policies = [
        {"name": "Mahindra HR Policies", "version": "v5.2", "date": "Jan 2024", "sections": 14},
        {"name": "Leave & Attendance Rules", "version": "v4.1", "date": "Jan 2024", "sections": 10},
        {"name": "Procurement Guidelines", "version": "v6.0", "date": "Jan 2024", "sections": 18},
        {"name": "Travel & Reimbursement", "version": "v5.3", "date": "Jan 2024", "sections": 12},
        {"name": "Safety & Compliance", "version": "v7.0", "date": "Jan 2024", "sections": 22},
        {"name": "IT Security Policy", "version": "v4.0", "date": "Jan 2024", "sections": 16},
        {"name": "Code of Conduct", "version": "v5.0", "date": "Jan 2024", "sections": 15}
    ]
    
    for policy in policies:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                st.markdown(f"**{policy['name']}**")
                st.caption(f"Version: {policy['version']}")
            with col2:
                st.markdown(f"**Sections**")
                st.write(policy['sections'])
            with col3:
                st.markdown(f"**Effective**")
                st.write(policy['date'])
            with col4:
                if st.button("View", key=policy['name']):
                    st.info(f"Full document viewer coming soon.")
            st.divider()

def analytics_tab():
    """Analytics dashboard"""
    st.markdown("### Mahindra Policy Analytics Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Query Distribution")
        categories_data = {
            'HR': 28, 'Leave': 22, 'Travel': 16,
            'IT Security': 13, 'Procurement': 9, 'Safety': 7, 'Code': 5
        }
        
        fig = go.Figure(data=[go.Pie(
            labels=list(categories_data.keys()),
            values=list(categories_data.values()),
            hole=0.35,
            marker=dict(colors=[MAHINDRA_RED, MAHINDRA_DARK_RED, MAHINDRA_GOLD, MAHINDRA_GRAY, '#666', '#888', '#AAA'])
        )])
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### User Satisfaction")
        satisfaction_data = pd.DataFrame({
            'Rating': ['Excellent', 'Good', 'Average', 'Poor'],
            'Percentage': [68, 24, 6, 2]
        })
        
        fig = go.Figure(data=[go.Bar(
            x=satisfaction_data['Rating'],
            y=satisfaction_data['Percentage'],
            marker_color=MAHINDRA_RED
        )])
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("#### Most Asked Questions")
    top_queries = [
        "How many sick leave days?",
        "Travel reimbursement process?",
        "Paternity leave policy?",
        "IT security guidelines?"
    ]
    
    for idx, query in enumerate(top_queries, 1):
        st.markdown(f"""
        <div style="background: white; padding: 0.75rem; border-radius: 8px; margin-bottom: 0.5rem;">
            <span class="badge">#{idx}</span> {query}
        </div>
        """, unsafe_allow_html=True)

def help_tab():
    """Help and support"""
    st.markdown("### Help & Support")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### Getting Started
        
        **How to Use:**
        1. Type your policy question
        2. Click "Get Answer"
        3. Review answer with sources
        4. Provide feedback
        
        **Tips:**
        - Be specific about policy area
        - Use complete sentences
        - Check source citations
        """)
    
    with col2:
        st.markdown("""
        #### Support Contacts
        
        **Email Support:** policy.help@mahindra.com
        
        **HR Helpline:** 1800-123-4567 (Ext: 1234)
        
        **Live Chat:** Available 9 AM - 6 PM
        """)
    
    st.markdown("---")
    st.info("For urgent policy assistance, please contact your HR Business Partner directly.")

def auth_page():
    """Authentication page (Login/Signup)"""
    
    st.markdown("""
    <div class="auth-card">
        <div class="auth-header">
            <div class="auth-logo">M</div>
            <div class="auth-title">Mahindra Rise</div>
            <div class="auth-subtitle">AI-Powered Policy Assistant</div>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            
            submitted = st.form_submit_button("Login", use_container_width=True)
            
            if submitted:
                if email and password:
                    if login_user(email, password):
                        st.rerun()
                else:
                    st.error("Please fill all fields")
    
    with tab2:
        with st.form("signup_form"):
            full_name = st.text_input("Full Name")
            email = st.text_input("Email")
            employee_id = st.text_input("Employee ID")
            department = st.selectbox("Department", [
                "HR", "IT", "Finance", "Operations", "Sales", "Marketing", "Engineering"
            ])
            phone = st.text_input("Phone Number (Optional)")
            location = st.text_input("Location (Optional)")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            submitted = st.form_submit_button("Sign Up", use_container_width=True)
            
            if submitted:
                if not all([full_name, email, employee_id, department, password]):
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
                        "phone_number": phone,
                        "location": location,
                        "password": password
                    }
                    
                    if signup_user(user_data):
                        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# Main application flow
if not st.session_state.authenticated:
    auth_page()
else:
    main_app()