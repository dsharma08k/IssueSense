"""Streamlit configuration"""

import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

# App Configuration
APP_TITLE = "IssueSense"
APP_ICON = "🐛"
APP_DESCRIPTION = "ML-Powered Error Knowledge Base"

# Session keys
SESSION_TOKEN_KEY = "access_token"
SESSION_USER_KEY = "user"
