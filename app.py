"""
Streamlit UI for the AI Employee Onboarding Assistant.
"""

import streamlit as st
import os
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file
except ImportError:
    pass  # dotenv is optional
from db import Database
from ingest import DocumentIngester
from agent import OnboardingAgent
from scheduler import ReminderScheduler


# Page configuration - Ensure sidebar is always visible
st.set_page_config(
    page_title="AI Employee Onboarding Assistant",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"  # Force sidebar to be expanded by default
)

# Initialize session state
if 'db' not in st.session_state:
    st.session_state.db = Database()

if 'ingester' not in st.session_state:
    st.session_state.ingester = DocumentIngester()

# Check for API key in multiple sources: Streamlit secrets, environment variable, or session state
def get_openai_api_key():
    """Get OpenAI API key from multiple sources in order of priority."""
    # 1. Check Streamlit secrets (for Streamlit Cloud deployment)
    try:
        if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
            return st.secrets['OPENAI_API_KEY']
    except Exception:
        pass
    
    # 2. Check environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key
    
    # 3. Check session state (user-entered key)
    if 'openai_api_key' in st.session_state and st.session_state.openai_api_key:
        return st.session_state.openai_api_key
    
    return None

# Initialize or reinitialize agent if API key is available
api_key = get_openai_api_key()
if 'agent' not in st.session_state:
    # First time initialization
    if api_key:
        try:
            # Temporarily set the environment variable for the agent initialization
            os.environ['OPENAI_API_KEY'] = api_key
            st.session_state.agent = OnboardingAgent(openai_api_key=api_key)
        except Exception as e:
            st.session_state.agent = None
            st.session_state.agent_error = str(e)
    else:
        st.session_state.agent = None
        st.session_state.agent_error = "OpenAI API key not found"
elif st.session_state.agent is None and api_key:
    # Reinitialize if agent was None but API key is now available
    try:
        os.environ['OPENAI_API_KEY'] = api_key
        st.session_state.agent = OnboardingAgent(openai_api_key=api_key)
        st.session_state.agent_error = None
    except Exception as e:
        st.session_state.agent = None
        st.session_state.agent_error = str(e)

if 'scheduler' not in st.session_state:
    st.session_state.scheduler = ReminderScheduler()
    st.session_state.scheduler.start_scheduler()

# Custom CSS with 3D Effects and Responsive Design
st.markdown("""
    <style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #e0e7ff 0%, #f3e8ff 100%);
        min-height: 100vh;
    }
    
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: #1a202c !important;
        margin-bottom: 2rem;
        text-align: center;
        text-shadow: 0 2px 10px rgba(102,126,234,0.2);
        animation: fadeInDown 0.8s ease-out;
    }
    
    /* 3D Card Effects - Light Background for Better Visibility */
    .card-3d {
        background: rgba(255, 255, 255, 1);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.15);
        border: 1px solid rgba(102, 126, 234, 0.2);
        transform-style: preserve-3d;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
    }
    
    .card-3d::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #f093fb, #4facfe);
        transform: scaleX(0);
        transform-origin: left;
        transition: transform 0.4s ease;
    }
    
    .card-3d:hover {
        transform: translateY(-10px) rotateX(5deg);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
    }
    
    .card-3d:hover::before {
        transform: scaleX(1);
    }
    
    /* Metric Cards with 3D Effect - Light Background */
    .metric-card-3d {
        background: rgba(255, 255, 255, 1);
        backdrop-filter: blur(20px);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 0.5rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.15);
        border: 1px solid rgba(102, 126, 234, 0.2);
        transform-style: preserve-3d;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card-3d::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(102,126,234,0.1) 0%, transparent 70%);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .metric-card-3d:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 15px 40px rgba(102,126,234,0.3);
    }
    
    .metric-card-3d:hover::after {
        opacity: 1;
    }
    
    /* Sidebar Styling - Light Background for Better Visibility */
    .css-1d391kg {
        background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(240,245,255,0.98) 100%);
        backdrop-filter: blur(10px);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(240,245,255,0.98) 100%) !important;
        backdrop-filter: blur(10px) !important;
        visibility: visible !important;
        display: block !important;
        opacity: 1 !important;
        width: 21rem !important;
        min-width: 21rem !important;
        z-index: 999 !important;
        border-right: 2px solid rgba(102,126,234,0.2) !important;
    }
    
    /* Ensure sidebar is always visible and not collapsed */
    [data-testid="stSidebar"][aria-expanded="false"] {
        visibility: visible !important;
        display: block !important;
    }
    
    /* Sidebar content container */
    [data-testid="stSidebar"] > div {
        visibility: visible !important;
        display: block !important;
    }
    
    [data-testid="stSidebar"] .css-1d391kg {
        background: transparent;
    }
    
    /* Sidebar toggle button - make it visible */
    [data-testid="collapsedControl"] {
        visibility: visible !important;
        display: block !important;
        z-index: 1000 !important;
    }
    
    /* Ensure sidebar navigation button is visible */
    button[aria-label*="sidebar"], button[aria-label*="menu"] {
        visibility: visible !important;
        display: block !important;
        z-index: 1000 !important;
    }
    
    /* Sidebar Text - Dark Text on Light Background for Better Visibility */
    [data-testid="stSidebar"] * {
        color: #1a202c !important;
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #1a202c !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stSidebar"] label {
        color: #1a202c !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stSidebar"] .stRadio label {
        color: #1a202c !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] div {
        color: #2d3748 !important;
    }
    
    /* Radio Button Labels in Sidebar - Dark Text on Light Background */
    [data-testid="stSidebar"] [class*="stRadio"] label {
        color: #1a202c !important;
        font-weight: 600 !important;
    }
    
    /* Make sidebar radio buttons more visible with light background */
    [data-testid="stSidebar"] [class*="stRadio"] > div {
        background: rgba(255, 255, 255, 1) !important;
        border: 2px solid rgba(102, 126, 234, 0.3) !important;
        border-radius: 10px !important;
        padding: 0.75rem !important;
        margin: 0.5rem 0 !important;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1) !important;
    }
    
    [data-testid="stSidebar"] [class*="stRadio"] > div:hover {
        background: rgba(240, 245, 255, 1) !important;
        border-color: rgba(102, 126, 234, 0.5) !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2) !important;
    }
    
    /* Selected radio button in sidebar */
    [data-testid="stSidebar"] [class*="stRadio"] input[type="radio"]:checked + label {
        color: #667eea !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stSidebar"] [class*="stRadio"] > div:has(input[type="radio"]:checked) {
        background: rgba(240, 245, 255, 1) !important;
        border-color: #667eea !important;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102,126,234,0.4);
        transform: perspective(1000px) rotateX(0deg);
    }
    
    .stButton > button:hover {
        transform: perspective(1000px) rotateX(-5deg) translateY(-2px);
        box-shadow: 0 8px 25px rgba(102,126,234,0.6);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        border: 2px solid rgba(102,126,234,0.3);
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border: 2px solid #667eea;
        box-shadow: 0 0 20px rgba(102,126,234,0.3);
        transform: scale(1.02);
    }
    
    /* File Uploader */
    .stFileUploader {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        padding: 2rem;
        border: 2px dashed rgba(102,126,234,0.5);
        transition: all 0.3s ease;
    }
    
    .stFileUploader:hover {
        border-color: #667eea;
        background: rgba(255, 255, 255, 0.95);
        transform: scale(1.02);
    }
    
    /* Animations */
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes float {
        0%, 100% {
            transform: translateY(0px);
        }
        50% {
            transform: translateY(-20px);
        }
    }
    
    @keyframes gradient {
        0% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
        100% {
            background-position: 0% 50%;
        }
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        
        .card-3d {
            padding: 1rem;
        }
        
        .metric-card-3d {
            padding: 1rem;
        }
    }
    
    /* Header Styling - Dark and Visible */
    h1, h2, h3 {
        color: #1a202c !important;
        font-weight: 700 !important;
    }
    
    /* Ensure all text in cards is visible with dark color */
    .card-3d h1, .card-3d h2, .card-3d h3 {
        color: #1a202c !important;
        font-weight: 700 !important;
    }
    
    .card-3d p, .card-3d span, .card-3d div, .card-3d li {
        color: #2d3748 !important;
    }
    
    /* Main content text visibility - Dark text on light background */
    .main .block-container {
        color: #2d3748 !important;
    }
    
    .main .block-container p, .main .block-container span, .main .block-container div {
        color: #2d3748 !important;
    }
    
    /* Dataframe text - Dark and readable */
    .dataframe {
        color: #1a202c !important;
    }
    
    .dataframe th {
        color: #1a202c !important;
        font-weight: 700 !important;
        background-color: rgba(102,126,234,0.1) !important;
    }
    
    .dataframe td {
        color: #2d3748 !important;
    }
    
    /* Input labels - Dark and bold */
    label {
        color: #1a202c !important;
        font-weight: 700 !important;
    }
    
    /* Selectbox and text input labels */
    .stSelectbox label, .stTextInput label, .stTextArea label, .stDateInput label {
        color: #1a202c !important;
        font-weight: 700 !important;
    }
    
    /* Input field text */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        color: #1a202c !important;
        font-weight: 500 !important;
    }
    
    /* Info and success messages text */
    .stInfo, .stSuccess, .stWarning, .stError {
        color: #1a202c !important;
        font-weight: 500 !important;
    }
    
    /* Expander text */
    .streamlit-expanderHeader {
        color: #1a202c !important;
        font-weight: 700 !important;
    }
    
    .streamlit-expanderContent {
        color: #2d3748 !important;
    }
    
    /* Checkbox labels */
    .stCheckbox label {
        color: #1a202c !important;
        font-weight: 600 !important;
    }
    
    /* Progress text */
    .stProgress {
        color: #2d3748 !important;
    }
    
    /* Metric text in cards */
    .metric-card-3d h1, .metric-card-3d h3 {
        color: #1a202c !important;
        font-weight: 700 !important;
    }
    
    /* All text elements in main area */
    .main p, .main span, .main div, .main li {
        color: #2d3748 !important;
    }
    
    /* Strong emphasis */
    strong, b {
        color: #1a202c !important;
        font-weight: 700 !important;
    }
    
    /* Dataframe Styling */
    .dataframe {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* Success/Info Messages */
    .stSuccess, .stInfo {
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* Progress Bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #f093fb 50%, #4facfe 100%);
        background-size: 200% auto;
        animation: gradient 3s ease infinite;
    }
    
    /* Checkbox Styling */
    .stCheckbox {
        margin: 0.5rem 0;
    }
    
    /* Selectbox Styling */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
    }
    
    /* Radio Button Styling */
    .stRadio > div {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        padding: 1rem;
    }
    
    .stRadio label {
        color: #2d3748 !important;
        font-weight: 500 !important;
    }
    
    /* Tab styling for better visibility */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #2d3748 !important;
        font-weight: 600 !important;
    }
    
    .stTabs [aria-selected="true"] {
        color: #667eea !important;
        font-weight: 700 !important;
    }
    
    /* Comprehensive Text Visibility - All Streamlit Components */
    
    /* All Streamlit write/info/success/error/warning text */
    .stAlert, .stAlert > div, .stAlert p, .stAlert span {
        color: #1a202c !important;
        font-weight: 500 !important;
    }
    
    .stInfo, .stInfo > div, .stInfo p, .stInfo span, .stInfo div {
        color: #1a202c !important;
        font-weight: 500 !important;
    }
    
    .stSuccess, .stSuccess > div, .stSuccess p, .stSuccess span, .stSuccess div {
        color: #1a202c !important;
        font-weight: 500 !important;
    }
    
    .stWarning, .stWarning > div, .stWarning p, .stWarning span, .stWarning div {
        color: #1a202c !important;
        font-weight: 500 !important;
    }
    
    .stError, .stError > div, .stError p, .stError span, .stError div {
        color: #1a202c !important;
        font-weight: 500 !important;
    }
    
    /* All markdown content */
    .stMarkdown, .stMarkdown p, .stMarkdown span, .stMarkdown div, .stMarkdown li, .stMarkdown ul, .stMarkdown ol {
        color: #2d3748 !important;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #1a202c !important;
        font-weight: 700 !important;
    }
    
    /* File uploader text */
    .stFileUploader label, .stFileUploader p, .stFileUploader span, .stFileUploader div {
        color: #1a202c !important;
        font-weight: 600 !important;
    }
    
    /* Spinner text */
    .stSpinner, .stSpinner > div, .stSpinner p, .stSpinner span {
        color: #1a202c !important;
        font-weight: 500 !important;
    }
    
    /* Citation and source text */
    .citation, .source-text, [class*="citation"], [class*="source"] {
        color: #2d3748 !important;
        font-weight: 500 !important;
    }
    
    /* Answer text in Q&A */
    .answer-text, [class*="answer"] {
        color: #2d3748 !important;
        font-weight: 400 !important;
        line-height: 1.6 !important;
    }
    
    /* Plan text */
    .plan-text, .plan-overview, .plan-phase, .plan-task {
        color: #2d3748 !important;
        font-weight: 400 !important;
    }
    
    /* Progress tracking text */
    .progress-text, .task-text, .task-name {
        color: #2d3748 !important;
        font-weight: 500 !important;
    }
    
    /* Status text */
    .status-text, [class*="status"] {
        color: #1a202c !important;
        font-weight: 600 !important;
    }
    
    /* Table of contents */
    .stToc, .stToc a, .stToc li {
        color: #2d3748 !important;
    }
    
    /* Code blocks */
    .stCodeBlock, code, pre {
        color: #1a202c !important;
        background: rgba(255, 255, 255, 0.9) !important;
    }
    
    /* JSON viewer */
    .stJson {
        color: #1a202c !important;
    }
    
    /* Balloons and snow */
    .stBalloon, .stSnow {
        /* Keep default colors for these */
    }
    
    /* Metric component text */
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        color: #1a202c !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricDelta"] {
        color: #2d3748 !important;
        font-weight: 600 !important;
    }
    
    /* Empty state messages */
    .empty-state, [class*="empty"] {
        color: #2d3748 !important;
        font-weight: 500 !important;
    }
    
    /* All paragraph and text elements in main */
    .main p, .main span, .main div, .main li, .main ul, .main ol, .main td, .main th {
        color: #2d3748 !important;
    }
    
    /* All headings in main */
    .main h1, .main h2, .main h3, .main h4, .main h5, .main h6 {
        color: #1a202c !important;
        font-weight: 700 !important;
    }
    
    /* Links */
    a {
        color: #667eea !important;
        font-weight: 600 !important;
    }
    
    a:hover {
        color: #764ba2 !important;
    }
    
    /* Blockquote */
    blockquote {
        color: #2d3748 !important;
        border-left: 4px solid #667eea !important;
        padding-left: 1rem !important;
    }
    
    /* Horizontal rule */
    hr {
        border-color: rgba(102,126,234,0.3) !important;
    }
    
    /* List items */
    li {
        color: #2d3748 !important;
    }
    
    /* Definition lists */
    dt {
        color: #1a202c !important;
        font-weight: 700 !important;
    }
    
    dd {
        color: #2d3748 !important;
    }
    
    /* Caption text */
    caption {
        color: #2d3748 !important;
        font-weight: 600 !important;
    }
    
    /* Small text */
    small {
        color: #4a5568 !important;
    }
    
    /* Mark/highlight text */
    mark {
        background-color: rgba(102,126,234,0.2) !important;
        color: #1a202c !important;
    }
    
    /* Deleted text */
    del {
        color: #718096 !important;
    }
    
    /* Inserted text */
    ins {
        color: #2d3748 !important;
    }
    
    /* Subscript and superscript */
    sub, sup {
        color: #2d3748 !important;
    }
    
    /* Abbreviation */
    abbr {
        color: #1a202c !important;
        font-weight: 600 !important;
    }
    
    /* Time element */
    time {
        color: #2d3748 !important;
    }
    
    /* Variable */
    var {
        color: #1a202c !important;
        font-style: italic !important;
    }
    
    /* Sample output */
    samp {
        color: #1a202c !important;
        background: rgba(255, 255, 255, 0.9) !important;
    }
    
    /* Keyboard input */
    kbd {
        color: #1a202c !important;
        background: rgba(102,126,234,0.1) !important;
    }
    
    /* Sidebar error/info messages - Dark text on light background */
    [data-testid="stSidebar"] .stAlert, 
    [data-testid="stSidebar"] .stInfo, 
    [data-testid="stSidebar"] .stSuccess, 
    [data-testid="stSidebar"] .stWarning, 
    [data-testid="stSidebar"] .stError {
        color: #1a202c !important;
        background: rgba(255, 255, 255, 0.9) !important;
    }
    
    [data-testid="stSidebar"] .stAlert p,
    [data-testid="stSidebar"] .stInfo p,
    [data-testid="stSidebar"] .stSuccess p,
    [data-testid="stSidebar"] .stWarning p,
    [data-testid="stSidebar"] .stError p {
        color: #1a202c !important;
    }
    
    /* Ensure all text in expanders is visible */
    [data-testid="stExpander"] p,
    [data-testid="stExpander"] span,
    [data-testid="stExpander"] div,
    [data-testid="stExpander"] li {
        color: #2d3748 !important;
    }
    
    /* Ensure all text in tabs is visible */
    [data-baseweb="tab-panel"] p,
    [data-baseweb="tab-panel"] span,
    [data-baseweb="tab-panel"] div,
    [data-baseweb="tab-panel"] li {
        color: #2d3748 !important;
    }
    
    /* Form text */
    form p, form span, form div, form label {
        color: #1a202c !important;
    }
    
    /* Container text */
    .block-container p, .block-container span, .block-container div {
        color: #2d3748 !important;
    }
    
    /* Element container text */
    .element-container p, .element-container span, .element-container div {
        color: #2d3748 !important;
    }
    
    /* Widget label container */
    .widget-label {
        color: #1a202c !important;
        font-weight: 700 !important;
    }
    
    /* Value text in widgets */
    .stText, .stNumber, .stSlider {
        color: #1a202c !important;
    }
    
    /* Date input text */
    .stDateInput label, .stDateInput input {
        color: #1a202c !important;
    }
    
    /* Time input text */
    .stTimeInput label, .stTimeInput input {
        color: #1a202c !important;
    }
    
    /* Multiselect text */
    .stMultiSelect label, .stMultiSelect [role="listbox"] {
        color: #1a202c !important;
    }
    
    /* Color picker text */
    .stColorPicker label {
        color: #1a202c !important;
    }
    
    /* Number input text */
    .stNumberInput label, .stNumberInput input {
        color: #1a202c !important;
    }
    
    /* Text area placeholder */
    .stTextArea textarea::placeholder {
        color: #718096 !important;
    }
    
    /* Text input placeholder */
    .stTextInput input::placeholder {
        color: #718096 !important;
    }
    
    /* Selectbox placeholder */
    .stSelectbox select option[value=""], .stSelectbox select option:first-child {
        color: #718096 !important;
    }
    
    /* Hide Streamlit default elements - but keep sidebar visible */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Force sidebar to be visible */
    section[data-testid="stSidebar"] {
        visibility: visible !important;
        display: block !important;
        opacity: 1 !important;
    }
    
    /* Sidebar content visibility */
    [data-testid="stSidebar"] section {
        visibility: visible !important;
        display: block !important;
    }
    
    /* Make sure sidebar doesn't get hidden by any parent */
    [data-testid="stSidebar"] * {
        visibility: visible !important;
    }
    </style>
""", unsafe_allow_html=True)


def main():
    """Main application."""
    # Enhanced header with 3D effect
    st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <div class="main-header">🚀 AI Employee Onboarding Assistant</div>
            <p style="color: #2d3748; font-size: 1.2rem; margin-top: -1rem; font-weight: 500;">
                Intelligent Onboarding Made Simple
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Enhanced sidebar navigation
    st.sidebar.markdown("""
        <div style="text-align: center; padding: 1rem 0; margin-bottom: 2rem;">
            <h2 style="color: #1a202c; font-weight: 700;">
                📋 Navigation
            </h2>
        </div>
    """, unsafe_allow_html=True)
    
    page = st.sidebar.radio(
        "Choose a page",
        ["Dashboard", "Document Upload", "Employee Management", 
         "Onboarding Plans", "Q&A Assistant", "Progress Tracking"],
        label_visibility="collapsed"
    )
    
    # Check for agent initialization and provide API key input
    if st.session_state.agent is None:
        st.sidebar.error("⚠️ OpenAI API key not configured")
        
        # Show error details if available
        if hasattr(st.session_state, 'agent_error') and st.session_state.agent_error:
            st.sidebar.caption(f"Error: {st.session_state.agent_error}")
        
        # Provide input field for API key
        st.sidebar.markdown("### 🔑 Configure API Key")
        api_key_input = st.sidebar.text_input(
            "Enter OpenAI API Key",
            type="password",
            help="Enter your OpenAI API key here. It will be stored in session state.",
            key="api_key_input"
        )
        
        if st.sidebar.button("💾 Save API Key"):
            if api_key_input:
                st.session_state.openai_api_key = api_key_input
                # Set environment variable
                os.environ['OPENAI_API_KEY'] = api_key_input
                # Try to initialize agent
                try:
                    st.session_state.agent = OnboardingAgent(openai_api_key=api_key_input)
                    st.session_state.agent_error = None
                    st.sidebar.success("✅ API key saved and validated!")
                    st.rerun()
                except Exception as e:
                    st.session_state.agent = None
                    st.session_state.agent_error = str(e)
                    st.sidebar.error(f"❌ Error: {str(e)}")
            else:
                st.sidebar.warning("Please enter an API key")
        
        st.sidebar.markdown("---")
        st.sidebar.info("""
        **For deployment:**
        - **Streamlit Cloud**: Add `OPENAI_API_KEY` in Settings → Secrets
        - **Local**: Set in `.env` file or environment variable
        - **Or**: Enter it above to use in this session
        """)
    else:
        # Show success status
        st.sidebar.success("✅ OpenAI API key configured")
        # Option to clear/change API key
        if st.sidebar.button("🔄 Change API Key"):
            st.session_state.agent = None
            st.session_state.openai_api_key = None
            if 'OPENAI_API_KEY' in os.environ:
                del os.environ['OPENAI_API_KEY']
            st.rerun()
    
    # Route to appropriate page
    if page == "Dashboard":
        show_dashboard()
    elif page == "Document Upload":
        show_document_upload()
    elif page == "Employee Management":
        show_employee_management()
    elif page == "Onboarding Plans":
        show_onboarding_plans()
    elif page == "Q&A Assistant":
        show_qa_assistant()
    elif page == "Progress Tracking":
        show_progress_tracking()


def show_dashboard():
    """Display dashboard with overview metrics."""
    st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="color: #1a202c; font-weight: 700;">
                📊 Dashboard
            </h1>
        </div>
    """, unsafe_allow_html=True)
    
    db = st.session_state.db
    
    # Get statistics
    employees = db.get_all_employees()
    documents = db.get_documents()
    active_employees = [e for e in employees if e['status'] == 'active']
    
    # Enhanced Metrics with 3D cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div class="metric-card-3d">
                <h3 style="color: #667eea; margin: 0; font-size: 0.9rem;">Total Employees</h3>
                <h1 style="color: #2d3748; margin: 0.5rem 0; font-size: 2.5rem;">{}</h1>
            </div>
        """.format(len(employees)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="metric-card-3d">
                <h3 style="color: #667eea; margin: 0; font-size: 0.9rem;">Active Employees</h3>
                <h1 style="color: #2d3748; margin: 0.5rem 0; font-size: 2.5rem;">{}</h1>
            </div>
        """.format(len(active_employees)), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="metric-card-3d">
                <h3 style="color: #667eea; margin: 0; font-size: 0.9rem;">Documents Uploaded</h3>
                <h1 style="color: #2d3748; margin: 0.5rem 0; font-size: 2.5rem;">{}</h1>
            </div>
        """.format(len(documents)), unsafe_allow_html=True)
    
    with col4:
        processed_docs = len([d for d in documents if d['status'] == 'processed'])
        st.markdown("""
            <div class="metric-card-3d">
                <h3 style="color: #667eea; margin: 0; font-size: 0.9rem;">Processed Documents</h3>
                <h1 style="color: #2d3748; margin: 0.5rem 0; font-size: 2.5rem;">{}</h1>
            </div>
        """.format(processed_docs), unsafe_allow_html=True)
    
    # Recent employees with 3D card
    st.markdown("""
        <div class="card-3d" style="margin-top: 2rem;">
            <h2 style="color: #2d3748; margin-bottom: 1rem;">👥 Recent Employees</h2>
    """, unsafe_allow_html=True)
    
    if employees:
        df = pd.DataFrame(employees[:10])
        st.dataframe(df[['employee_id', 'name', 'email', 'role', 'department', 'start_date']], 
                    use_container_width=True)
    else:
        st.info("No employees added yet.")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Recent documents with 3D card
    st.markdown("""
        <div class="card-3d" style="margin-top: 2rem;">
            <h2 style="color: #2d3748; margin-bottom: 1rem;">📄 Recent Documents</h2>
    """, unsafe_allow_html=True)
    
    if documents:
        df = pd.DataFrame(documents)
        st.dataframe(df[['filename', 'file_type', 'status', 'uploaded_at']], 
                    use_container_width=True)
    else:
        st.info("No documents uploaded yet.")
    
    st.markdown("</div>", unsafe_allow_html=True)


def show_document_upload():
    """Document upload and processing interface."""
    # Add specific CSS for Document Upload page to ensure all fonts are visible
    st.markdown("""
        <style>
        /* Document Upload Page Specific Styles - Ensure All Text is Visible */
        .stFileUploader label {
            color: #1a202c !important;
            font-weight: 700 !important;
            font-size: 1.1rem !important;
        }
        
        .stFileUploader p, .stFileUploader span, .stFileUploader div {
            color: #1a202c !important;
            font-weight: 500 !important;
        }
        
        /* File uploader area text */
        [data-testid="stFileUploader"] label,
        [data-testid="stFileUploader"] p,
        [data-testid="stFileUploader"] span,
        [data-testid="stFileUploader"] div {
            color: #1a202c !important;
            font-weight: 600 !important;
        }
        
        /* Upload button text */
        [data-testid="stFileUploader"] button {
            color: #ffffff !important;
        }
        
        /* Ensure all text in document upload cards is visible */
        .card-3d h2 {
            color: #1a202c !important;
            font-weight: 700 !important;
        }
        
        .card-3d p, .card-3d span, .card-3d div, .card-3d strong, .card-3d b {
            color: #1a202c !important;
            font-weight: 500 !important;
        }
        
        /* Status text visibility */
        .card-3d markdown, .card-3d [class*="markdown"] {
            color: #1a202c !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="color: #1a202c; font-weight: 700; font-size: 2.5rem;">
                📤 Document Upload
            </h1>
            <p style="color: #2d3748; font-size: 1.1rem; font-weight: 600;">
                Upload company documents (PDFs) to build the knowledge base
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="card-3d">', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None:
        # Save uploaded file
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        
        file_path = upload_dir / uploaded_file.name
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        # Process file
        if st.button("🔄 Process Document"):
            with st.spinner("Processing document and building knowledge base..."):
                success, error_message = st.session_state.ingester.process_pdf(str(file_path))
                
                if success:
                    st.success("✨ Document processed successfully and added to knowledge base!")
                else:
                    st.error("❌ Error processing document")
                    if error_message:
                        st.warning(f"**Details:** {error_message}")
                        # Provide helpful suggestions based on error
                        if "readonly" in error_message.lower() or "read-only" in error_message.lower() or "permission" in error_message.lower() or "database" in error_message.lower():
                            st.error("🔒 **Database Permission Error**")
                            st.info("""
                            **This error occurs when the database file is read-only.**
                            
                            **For Streamlit Cloud:**
                            - This is a known limitation. The database file may need to be in a writable location.
                            - Try restarting the app or redeploying.
                            
                            **For Local Development:**
                            - Check file permissions on `onboarding.db`
                            - Ensure you have write access to the directory
                            - Try deleting the database file and letting the app recreate it
                            
                            **Workaround:** The app will try to use an alternative location automatically.
                            """)
                        elif "password" in error_message.lower() or "encrypted" in error_message.lower():
                            st.info("💡 **Tip:** Remove the password from your PDF file and try again.")
                        elif "scanned" in error_message.lower() or "image-based" in error_message.lower() or "no extractable text" in error_message.lower():
                            st.info("💡 **Tip:** This appears to be a scanned PDF (image-based). You may need to use OCR (Optical Character Recognition) software to extract text first.")
                        elif "corrupted" in error_message.lower() or "invalid" in error_message.lower():
                            st.info("💡 **Tip:** The PDF file may be corrupted. Try opening it in a PDF viewer to verify it's valid, or try re-saving it.")
                    else:
                        st.warning("Please check the file format and ensure it's a valid PDF file.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # List existing documents with 3D cards
    st.markdown("""
        <div class="card-3d" style="margin-top: 2rem;">
            <h2 style="color: #1a202c; margin-bottom: 1rem; font-weight: 700; font-size: 1.5rem;">📚 Uploaded Documents</h2>
    """, unsafe_allow_html=True)
    
    documents = st.session_state.db.get_documents()
    
    if documents:
        for doc in documents:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"<p style='color: #1a202c; font-weight: 600; font-size: 1rem;'><strong>📄 {doc['filename']}</strong></p>", unsafe_allow_html=True)
            with col2:
                status_color = "🟢" if doc['status'] == 'processed' else "🟡" if doc['status'] == 'pending' else "🔴"
                status_text = doc['status'].title()
                st.markdown(f"<p style='color: #1a202c; font-weight: 600; font-size: 0.95rem;'>{status_color} <strong>{status_text}</strong></p>", unsafe_allow_html=True)
            with col3:
                if st.button("🗑️ Delete", key=f"delete_{doc['id']}"):
                    st.session_state.ingester.delete_document(doc['filename'])
                    st.rerun()
    else:
        st.info("📭 No documents uploaded yet.")
    
    st.markdown('</div>', unsafe_allow_html=True)


def show_employee_management():
    """Employee management interface."""
    st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="color: #1a202c; font-weight: 700;">
                👥 Employee Management
            </h1>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["➕ Add Employee", "📋 View Employees"])
    
    with tab1:
        st.markdown('<div class="card-3d">', unsafe_allow_html=True)
        st.markdown("### ➕ Add New Employee")
        
        with st.form("add_employee_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                employee_id = st.text_input("Employee ID *")
                name = st.text_input("Full Name *")
                email = st.text_input("Email *")
            
            with col2:
                phone = st.text_input("Phone Number")
                role = st.text_input("Role")
                department = st.text_input("Department")
            
            start_date = st.date_input("Start Date")
            
            submitted = st.form_submit_button("Add Employee")
            
            if submitted:
                if employee_id and name and email:
                    success = st.session_state.db.add_employee(
                        employee_id=employee_id,
                        name=name,
                        email=email,
                        phone=phone if phone else None,
                        role=role if role else None,
                        department=department if department else None,
                        start_date=start_date.isoformat() if start_date else None
                    )
                    
                    if success:
                        st.success(f"Employee {name} added successfully!")
                        
                        # Schedule welcome reminder
                        if start_date:
                            st.session_state.scheduler.schedule_welcome_reminder(
                                employee_id, start_date.isoformat()
                            )
                    else:
                        st.error("Employee ID already exists. Please use a different ID.")
                else:
                    st.error("Please fill in all required fields (*)")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="card-3d">', unsafe_allow_html=True)
        st.markdown("### 📋 All Employees")
        employees = st.session_state.db.get_all_employees()
        
        if employees:
            df = pd.DataFrame(employees)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No employees added yet.")
        
        st.markdown('</div>', unsafe_allow_html=True)


def show_onboarding_plans():
    """Onboarding plan generation and viewing."""
    st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="color: #1a202c; font-weight: 700;">
                📋 Onboarding Plans
            </h1>
        </div>
    """, unsafe_allow_html=True)
    
    db = st.session_state.db
    employees = db.get_all_employees()
    
    if not employees:
        st.info("Please add employees first.")
        return
    
    st.markdown('<div class="card-3d">', unsafe_allow_html=True)
    
    # Select employee
    employee_options = {f"{e['name']} ({e['employee_id']})": e['employee_id'] 
                        for e in employees}
    selected_employee_key = st.selectbox("Select Employee", list(employee_options.keys()))
    selected_employee_id = employee_options[selected_employee_key]
    
    employee = db.get_employee(selected_employee_id)
    
    if not employee:
        st.error("Employee not found.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Check if plan exists
    existing_plan = db.get_onboarding_plan(selected_employee_id)
    
    if existing_plan:
        st.markdown(f"### 📋 Onboarding Plan for {employee['name']}")
        
        # Display plan
        st.markdown("### 📊 Plan Overview")
        st.write(existing_plan['plan_data'].get('overview', 'No overview available.'))
        
        # Display phases
        st.markdown("### 📅 Plan Phases")
        for phase in existing_plan['plan_data'].get('phases', []):
            with st.expander(phase.get('title', 'Phase')):
                for task in phase.get('tasks', []):
                    st.write(f"• {task}")
        
        # Display checklist
        st.markdown("### ✅ Checklist")
        checklist = existing_plan['checklist_items']
        
        for item in checklist:
            status = item.get('status', 'pending')
            checkbox = st.checkbox(
                item.get('task', ''),
                value=(status == 'completed'),
                key=f"checklist_{item['id']}"
            )
            
            if checkbox and status != 'completed':
                db.update_task_status(selected_employee_id, item['id'], 'completed')
                st.rerun()
            elif not checkbox and status == 'completed':
                db.update_task_status(selected_employee_id, item['id'], 'pending')
                st.rerun()
        
        if st.button("🔄 Regenerate Plan"):
            if st.session_state.agent:
                with st.spinner("Regenerating plan..."):
                    try:
                        plan_data = st.session_state.agent.generate_onboarding_plan(
                            selected_employee_id, employee
                        )
                        st.success("Plan regenerated!")
                        st.rerun()
                    except Exception as e:
                        error_msg = str(e)
                        if 'rate limit' in error_msg.lower():
                            st.error("⚠️ **Rate Limit Error**")
                            st.warning(
                                "OpenAI API rate limit exceeded. Please wait a few minutes and try again. "
                                "If this persists, you may need to upgrade your OpenAI plan."
                            )
                        else:
                            st.error(f"❌ Error regenerating plan: {error_msg}")
            else:
                st.error("AI agent not configured.")
    else:
        st.info(f"📭 No onboarding plan exists for {employee['name']}.")
        
        if st.button("✨ Generate Onboarding Plan"):
            if st.session_state.agent:
                with st.spinner("Generating personalized onboarding plan..."):
                    try:
                        plan_data = st.session_state.agent.generate_onboarding_plan(
                            selected_employee_id, employee
                        )
                        st.success("✨ Onboarding plan generated successfully!")
                        st.rerun()
                    except Exception as e:
                        error_msg = str(e)
                        if 'rate limit' in error_msg.lower():
                            st.error("⚠️ **Rate Limit Error**")
                            st.warning(
                                "OpenAI API rate limit exceeded. Please wait a few minutes and try again. "
                                "If this persists, you may need to upgrade your OpenAI plan."
                            )
                        else:
                            st.error(f"❌ Error generating plan: {error_msg}")
            else:
                st.error("AI agent not configured. Please set OPENAI_API_KEY.")
    
    st.markdown('</div>', unsafe_allow_html=True)


def show_qa_assistant():
    """Q&A assistant interface."""
    st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="color: #1a202c; font-weight: 700;">
                💬 Q&A Assistant
            </h1>
            <p style="color: #2d3748; font-size: 1.1rem; font-weight: 500;">
                Ask questions about company policies, procedures, and onboarding
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.agent:
        st.error("AI agent not configured. Please set OPENAI_API_KEY in your .env file.")
        return
    
    st.markdown('<div class="card-3d">', unsafe_allow_html=True)
    
    # Employee context (optional)
    employees = st.session_state.db.get_all_employees()
    if employees:
        employee_options = {f"{e['name']} ({e['employee_id']})": e 
                           for e in employees}
        employee_options["General Question"] = None
        selected = st.selectbox("Select Employee Context (Optional)", 
                               list(employee_options.keys()))
        employee_context = employee_options[selected] if selected != "General Question" else None
    else:
        employee_context = None
    
    # Question input
    question = st.text_area("Enter your question:", height=100)
    
    if st.button("Ask Question"):
        if question:
            with st.spinner("Searching knowledge base and generating answer..."):
                try:
                    result = st.session_state.agent.answer_question(question, employee_context)
                    
                    # Display answer
                    st.markdown("### Answer")
                    st.write(result['answer'])
                    
                    # Display citations
                    if result['citations']:
                        st.markdown("### Sources")
                        for citation in result['citations']:
                            st.write(f"• **{citation['source']}** (Page {citation['page']})")
                            if citation.get('relevance_score'):
                                st.progress(citation['relevance_score'])
                    else:
                        st.info("No specific sources found for this question.")
                except Exception as e:
                    error_msg = str(e)
                    if 'rate limit' in error_msg.lower():
                        st.error("⚠️ **Rate Limit Error**")
                        st.warning(
                            "OpenAI API rate limit exceeded. This usually happens when:\n"
                            "- You've made too many requests in a short time\n"
                            "- Your OpenAI account has usage limits\n\n"
                            "**Solutions:**\n"
                            "- Wait a few minutes and try again\n"
                            "- Upgrade your OpenAI plan for higher rate limits\n"
                            "- Reduce the frequency of requests"
                        )
                    else:
                        st.error(f"❌ Error: {error_msg}")
        else:
            st.warning("Please enter a question.")
    
    st.markdown('</div>', unsafe_allow_html=True)


def show_progress_tracking():
    """Progress tracking interface."""
    st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="color: #1a202c; font-weight: 700;">
                📈 Progress Tracking
            </h1>
        </div>
    """, unsafe_allow_html=True)
    
    db = st.session_state.db
    employees = db.get_all_employees()
    
    if not employees:
        st.info("Please add employees first.")
        return
    
    st.markdown('<div class="card-3d">', unsafe_allow_html=True)
    
    # Select employee
    employee_options = {f"{e['name']} ({e['employee_id']})": e['employee_id'] 
                        for e in employees}
    selected_employee_key = st.selectbox("Select Employee", list(employee_options.keys()))
    selected_employee_id = employee_options[selected_employee_key]
    
    # Get progress
    progress = db.get_progress(selected_employee_id)
    
    if progress:
        # Calculate statistics
        total_tasks = len(progress)
        completed_tasks = len([p for p in progress if p['status'] == 'completed'])
        pending_tasks = total_tasks - completed_tasks
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
                <div class="metric-card-3d">
                    <h3 style="color: #667eea; margin: 0; font-size: 0.9rem;">Total Tasks</h3>
                    <h1 style="color: #2d3748; margin: 0.5rem 0; font-size: 2.5rem;">{}</h1>
                </div>
            """.format(total_tasks), unsafe_allow_html=True)
        with col2:
            st.markdown("""
                <div class="metric-card-3d">
                    <h3 style="color: #667eea; margin: 0; font-size: 0.9rem;">Completed</h3>
                    <h1 style="color: #2d3748; margin: 0.5rem 0; font-size: 2.5rem;">{}</h1>
                </div>
            """.format(completed_tasks), unsafe_allow_html=True)
        with col3:
            st.markdown("""
                <div class="metric-card-3d">
                    <h3 style="color: #667eea; margin: 0; font-size: 0.9rem;">Completion Rate</h3>
                    <h1 style="color: #2d3748; margin: 0.5rem 0; font-size: 2.5rem;">{}%</h1>
                </div>
            """.format(f"{completion_rate:.1f}"), unsafe_allow_html=True)
        
        # Progress bar
        st.progress(completion_rate / 100)
        
        # Task list
        st.markdown("### ✅ Tasks")
        for task in progress:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                status_icon = "✅" if task['status'] == 'completed' else "⏳"
                st.markdown(f"**{status_icon} {task['task_name']}**")
            with col2:
                st.markdown(f"**{task['status'].title()}**")
            with col3:
                if task['status'] == 'pending':
                    if st.button("✓ Mark Complete", key=f"complete_{task['id']}"):
                        db.update_task_status(selected_employee_id, task['id'], 'completed')
                        st.rerun()
                else:
                    st.markdown(f"*Completed: {task.get('completed_at', 'N/A')[:10] if task.get('completed_at') else 'N/A'}*")
    else:
        st.info("📭 No tasks tracked yet. Generate an onboarding plan first.")
    
    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()

