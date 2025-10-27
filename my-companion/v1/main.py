import streamlit as st
import os
from app import basic_info, technical_skills, projects, other_activities, knowledge_base, ask_companion
from utils.data_store import load_data, save_data
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Load data ---
data = load_data()

# --- Sidebar Navigation ---
st.sidebar.title(os.getenv("APP_TITLE"))
section = st.sidebar.radio("Navigate to:", [
    "💼 Work Experience",
    "🧠 Knowledge Base",
    "💬 Ask Companion"
])

# --- Main Content ---
if section == "💼 Work Experience":
    st.title("💼 Work Experience")
    
    # Create tabs for Work Experience sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "👤 Basic Information",
        "⚙️ Technical Skills", 
        "🧱 Projects",
        "🌟 Other Activities"
    ])
    
    with tab1:
        basic_info.show(data)
    
    with tab2:
        technical_skills.show(data)
    
    with tab3:
        projects.show(data)
    
    with tab4:
        other_activities.show(data)

elif section == "🧠 Knowledge Base":
    knowledge_base.show(data)
elif section == "💬 Ask Companion":
    ask_companion.show(data)

# --- Save after every section change ---
save_data(data)
