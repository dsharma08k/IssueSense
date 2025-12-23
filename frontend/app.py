"""
IssueSense - Cyberpunk Developer Command Center
Main Streamlit Application
"""

import streamlit as st
from config import APP_TITLE, APP_ICON, APP_DESCRIPTION, SESSION_TOKEN_KEY, SESSION_USER_KEY
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Page config
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Minimal Clean CSS
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Hide default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Clean background */
    .stApp {
        background: #ffffff;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    
    [data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
        background: transparent !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
        margin: 2px 8px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        color: #475569 !important;
        transition: all 0.2s ease !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {
        background: #e2e8f0 !important;
        color: #1e293b !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"] {
        background: #3b82f6 !important;
        color: white !important;
    }
    
    /* Clean Cards */
    .clean-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 24px;
        margin: 12px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* Stat Cards */
    .stat-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    
    .stat-card h1 {
        font-family: 'Inter', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: #1e293b;
        margin: 0;
    }
    
    .stat-card p {
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        color: #64748b;
        margin-top: 4px;
    }
    
    .stat-card.blue { border-left: 4px solid #3b82f6; }
    .stat-card.green { border-left: 4px solid #10b981; }
    .stat-card.yellow { border-left: 4px solid #f59e0b; }
    .stat-card.red { border-left: 4px solid #ef4444; }
    
    /* Page Header */
    .page-header {
        font-family: 'Inter', sans-serif;
        font-size: 1.75rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 8px;
    }
    
    .page-subheader {
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        color: #64748b;
        margin-bottom: 24px;
    }
    
    /* Buttons */
    .stButton button {
        background: #3b82f6 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        color: white !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton button:hover {
        background: #2563eb !important;
    }
    
    /* Input Fields */
    .stTextInput input, .stTextArea textarea, .stSelectbox > div > div {
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: #f8fafc;
        border-radius: 8px;
        padding: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        background: #f8fafc !important;
        border-radius: 8px !important;
    }
    
    /* Metrics */
    [data-testid="metric-container"] {
        background: #f8fafc;
        border-radius: 8px;
        padding: 12px;
    }
    
    [data-testid="stMetricValue"] {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        color: #1e293b;
    }
    
    /* Code blocks */
    code {
        font-family: 'Consolas', 'Monaco', monospace !important;
        background: #f1f5f9 !important;
        color: #1e293b !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
    }
    
    /* Status badges */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
    }
    
    .badge-blue { background: #dbeafe; color: #1d4ed8; }
    .badge-green { background: #dcfce7; color: #15803d; }
    .badge-yellow { background: #fef3c7; color: #b45309; }
    .badge-red { background: #fee2e2; color: #b91c1c; }
    .badge-gray { background: #f1f5f9; color: #475569; }
</style>
""", unsafe_allow_html=True)

# Initialize Supabase client
@st.cache_resource
def get_supabase_client() -> Client:
    """Get Supabase client"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    return create_client(supabase_url, supabase_key)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if SESSION_TOKEN_KEY not in st.session_state:
    st.session_state[SESSION_TOKEN_KEY] = None

if SESSION_USER_KEY not in st.session_state:
    st.session_state[SESSION_USER_KEY] = None


def login_page():
    """Login/Signup page with clean minimal design"""
    
    # Clean header
    st.markdown("""
        <div style="text-align: center; padding: 40px 0;">
            <div class="page-header">🐛 IssueSense</div>
            <div class="page-subheader">Track, analyze, and resolve errors with AI</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
            <div class="clean-card">
                <h3 style="text-align: center; font-family: 'Inter', sans-serif; color: #1e293b; margin-bottom: 20px;">
                    Welcome back
                </h3>
            </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Sign In", "Create Account"])
        
        with tab1:
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="you@example.com")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Sign In", use_container_width=True)
                
                if submit:
                    try:
                        supabase = get_supabase_client()
                        response = supabase.auth.sign_in_with_password({
                            "email": email,
                            "password": password
                        })
                        
                        if response.user:
                            st.session_state[SESSION_TOKEN_KEY] = response.session.access_token
                            st.session_state[SESSION_USER_KEY] = response.user
                            st.session_state.authenticated = True
                            st.success("✓ Signed in successfully!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Sign in failed: {str(e)}")
        
        with tab2:
            with st.form("signup_form"):
                email = st.text_input("Email", key="signup_email", placeholder="you@example.com")
                password = st.text_input("Password", type="password", key="signup_password")
                password_confirm = st.text_input("Confirm Password", type="password")
                submit = st.form_submit_button("Create Account", use_container_width=True)
                
                if submit:
                    if password != password_confirm:
                        st.error("Passwords don't match")
                    else:
                        try:
                            supabase = get_supabase_client()
                            response = supabase.auth.sign_up({
                                "email": email,
                                "password": password
                            })
                            
                            if response.user:
                                st.success("✓ Account created! You can now sign in.")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")


def main_app():
    """Main application - Dashboard"""
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
            <div style="text-align: center; padding: 20px 0;">
                <div style="font-family: 'Inter', sans-serif; font-size: 1.25rem; 
                     font-weight: 700; color: #1e293b;">
                    🐛 IssueSense
                </div>
                <div style="font-family: 'Inter', sans-serif; font-size: 0.75rem; 
                     color: #64748b; margin-top: 4px;">
                    Error Tracking System
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        user = st.session_state.get(SESSION_USER_KEY)
        if user:
            st.markdown(f"""
                <div style="font-family: 'Inter', sans-serif; color: #10b981; font-size: 0.8rem;">
                    ● Online
                </div>
                <div style="font-family: 'Inter', sans-serif; color: #64748b; font-size: 0.8rem;">
                    {user.email}
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        if st.button("Sign Out", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state[SESSION_TOKEN_KEY] = None
            st.session_state[SESSION_USER_KEY] = None
            st.rerun()
    
    # Main content - Dashboard Header
    st.markdown("""
        <div class="page-header">Dashboard</div>
        <div class="page-subheader">Overview of your error tracking</div>
    """, unsafe_allow_html=True)
    
    # Welcome message
    user = st.session_state.get(SESSION_USER_KEY)
    if user:
        username = user.email.split('@')[0]
        st.markdown(f"""
            <div style="font-family: 'Inter', sans-serif; color: #64748b; margin-bottom: 24px;">
                Welcome back, <strong style="color: #1e293b;">{username}</strong>
            </div>
        """, unsafe_allow_html=True)
    
    # Stats Cards
    try:
        from api_client import api_client
        stats = api_client.get_dashboard_stats()
        
        cols = st.columns(4)
        
        with cols[0]:
            st.markdown(f"""
                <div class="stat-card blue">
                    <h1>{stats['total_issues']}</h1>
                    <p>Total Issues</p>
                </div>
            """, unsafe_allow_html=True)
        
        with cols[1]:
            st.markdown(f"""
                <div class="stat-card green">
                    <h1>{stats['resolved_issues']}</h1>
                    <p>Resolved</p>
                </div>
            """, unsafe_allow_html=True)
        
        with cols[2]:
            st.markdown(f"""
                <div class="stat-card yellow">
                    <h1>{stats['open_issues']}</h1>
                    <p>Open</p>
                </div>
            """, unsafe_allow_html=True)
        
        with cols[3]:
            rate = int(stats['resolution_rate'] * 100)
            st.markdown(f"""
                <div class="stat-card">
                    <h1>{rate}%</h1>
                    <p>Resolution Rate</p>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Quick Navigation
        st.markdown("""
            <div class="clean-card">
                <h4 style="font-family: 'Inter', sans-serif; color: #1e293b; margin-bottom: 16px;">Quick Navigation</h4>
                <p style="font-family: 'Inter', sans-serif; color: #64748b; font-size: 0.9rem; line-height: 2;">
                    <strong>📝 Issues</strong> — Log and manage programming errors<br>
                    <strong>🔍 Search</strong> — Find similar issues with AI-powered search<br>
                    <strong>📊 Analytics</strong> — Visualize error patterns and trends
                </p>
            </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.markdown("""
            <div class="clean-card" style="border-left: 4px solid #f59e0b;">
                <h4 style="font-family: 'Inter', sans-serif; color: #b45309;">Backend Connection</h4>
                <p style="font-family: 'Inter', sans-serif; color: #64748b;">
                    Start the backend server to see your stats.
                </p>
                <code>cd backend && uvicorn app.main:app --reload</code>
            </div>
        """, unsafe_allow_html=True)


# Main app logic
if st.session_state.authenticated:
    main_app()
else:
    login_page()
