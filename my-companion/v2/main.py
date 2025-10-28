"""
My Companion v2 - Lightweight Agentic AI
Minimal enhancement over v1: just adds basic agent planning and simple guardrails
"""
import streamlit as st
import json
import os
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import v2 core components
from core.agent import Agent
from core.guardrails import Guardrails
from core.vector_db import VectorDB

# Configure Streamlit (same as v1)
st.set_page_config(
    page_title="My Companion (v2)",
    page_icon="🤖",
    layout="wide"
)

@st.cache_resource
def load_data():
    """Load knowledge base data (same as v1)"""
    try:
        with open("data/knowledge_base.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "basic_info": {},
            "technical_skills": [],
            "projects": [],
            "other_activities": []
        }

@st.cache_resource
def get_llm_client():
    """Initialize LLM client with environment variables"""
    return OpenAI(
        base_url=os.getenv("LLM_BASE_URL", "http://localhost:1234/v1"),
        api_key=os.getenv("LLM_API_KEY", "lm-studio")
    )

@st.cache_resource
def init_vector_db():
    """Initialize the lightweight vector database"""
    vector_db = VectorDB()
    # Auto-rebuild if no vectors exist
    if vector_db.get_stats()["total_documents"] == 0:
        data = load_data()
        vector_db.rebuild_from_data(data)
    return vector_db

@st.cache_resource
def init_agent():
    """Initialize the lightweight agent with RAG"""
    llm_client = get_llm_client()
    vector_db = init_vector_db()
    agent = Agent(llm_client, load_data, vector_db)
    return agent

@st.cache_resource  
def init_guardrails():
    """Initialize simple guardrails"""
    return Guardrails()

def main():
    """Main application - enhanced v1 with minimal agentic AI"""
    
    # Initialize components
    agent = init_agent()
    guardrails = init_guardrails()
    vector_db = init_vector_db()
    data = load_data()
    
    # Header (similar to v1)
    st.title("🤖 My Companion (v2)")
    #st.caption("Enhanced with basic agentic AI and simple guardrails")
    
    # Sidebar with navigation and stats
    with st.sidebar:
        st.header("🧭 Navigation")
        
        # Main navigation (Level 1 only)
        selected_page = st.selectbox("Choose a page:", [
            "Work Experience", 
            "My Profile", 
            "AI Assistant"
        ])
        
        st.divider()
        
        st.header("📊 Status")
        
        # Agent stats
        agent_stats = agent.get_stats()
        st.write(f"**Conversations:** {agent_stats['conversation_length']}")
        st.write(f"**Status:** {agent_stats['status']}")
        
        # Cache stats
        cache_stats = agent_stats.get('cache', {})
        cache_entries = cache_stats.get('total_entries', 0)
        cache_hits = cache_stats.get('total_hits', 0)
        st.write(f"**Cache:** {cache_entries} entries, {cache_hits} hits")
        
        # Data stats (V1 schema)
        st.write(f"**Projects:** {len(data.get('projects', []))}")
        skills_count = len(data.get('technical_skills', {})) if isinstance(data.get('technical_skills'), dict) else len(data.get('technical_skills', []))
        st.write(f"**Skills:** {skills_count}")
        st.write(f"**Activities:** {len(data.get('other_activities', []))}")
        if data.get('user_profile'):
            st.write(f"**Profile:** ✅ Loaded")
        
        # Vector DB stats
        vector_stats = vector_db.get_stats()
        st.write(f"**Vector DB:** {vector_stats['total_documents']} docs")
        
        # Guardrails stats
        gr_stats = guardrails.get_stats()
        st.write(f"**Guardrails:** {'✅ Active' if gr_stats['enabled'] else '❌ Disabled'}")
        
        st.divider()
        
        # Actions
        if st.button("🔄 Rebuild Vector DB"):
            with st.spinner("Rebuilding..."):
                result = agent.rebuild_knowledge_base()
                if result["success"]:
                    st.success(f"✅ {result['message']}")
                    st.rerun()
                else:
                    st.error(f"❌ {result['error']}")
        
        if st.button("🧹 Clear Chat History"):
            agent.clear_history()
            st.success("Chat history cleared!")
            st.rerun()
        
        if st.button("🗑️ Clear Response Cache"):
            agent.clear_cache()
            st.success("Response cache cleared!")
            st.rerun()
    
    # Main content with tabs based on navigation selection
    
    # === WORK EXPERIENCE PAGES ===
    if selected_page == "Work Experience":
        st.header("📝 Work Experience")
        
        # Create tabs for Work Experience sections
        tab1, tab2, tab3, tab4 = st.tabs(["User Profile", "Technical Skills", "Projects", "Other Activities"])
        
        with tab1:
            # Import and use V1 user profile functionality
            from app.user_profile import show
            show(data)
        
        with tab2:
            # Import and use V1 technical skills functionality
            from app.technical_skills import show
            show(data)
        
        with tab3:
            # Import and use V1 projects functionality
            from app.projects import show
            show(data)
        
        with tab4:
            # Import and use V1 other activities functionality
            from app.other_activities import show
            show(data)
    
    # === MY PROFILE PAGES ===
    elif selected_page == "My Profile":
        st.header("📋 My Profile")
        
        # Create tabs for My Profile sections
        tab1, tab2, tab3 = st.tabs(["Overview", "Search", "Insights"])
        
        with tab1:
            # Import and use profile overview functionality
            from app.profile_overview import show
            show(data)
        
        with tab2:
            # Import and use profile search functionality
            from app.profile_search import show
            show(data, vector_db)
        
        with tab3:
            # Import and use profile insights functionality
            from app.profile_insights import show
            show(data, agent)
    
    # === AI ASSISTANT PAGE ===
    elif selected_page == "AI Assistant":
        # Import and use AI Assistant functionality
        from app.ai_assistant import show
        show(data, agent, guardrails)

if __name__ == "__main__":
    main()