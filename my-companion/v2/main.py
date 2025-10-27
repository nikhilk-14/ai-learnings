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
    st.caption("Enhanced with basic agentic AI and simple guardrails")
    
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
    
    # Main content with tabs based on navigation selection
    
    # === WORK EXPERIENCE PAGES ===
    if selected_page == "Work Experience":
        st.header("📝 Work Experience")
        
        # Create tabs for Work Experience sections
        tab1, tab2, tab3, tab4 = st.tabs(["User Profile", "Technical Skills", "Projects", "Other Activities"])
        
        with tab1:
            st.subheader("👤 User Profile")
            # Import and use V1 user profile functionality
            from app.user_profile import show
            show(data)
        
        with tab2:
            st.subheader("💻 Technical Skills")
            # Import and use V1 technical skills functionality
            from app.technical_skills import show
            show(data)
        
        with tab3:
            st.subheader("🚀 Projects")
            # Import and use V1 projects functionality
            from app.projects import show
            show(data)
        
        with tab4:
            st.subheader("🎯 Other Activities")
            # Import and use V1 other activities functionality
            from app.other_activities import show
            show(data)
    
    # === MY PROFILE PAGES ===
    elif selected_page == "My Profile":
        st.header("📋 My Profile")
        
        # Create tabs for My Profile sections
        tab1, tab2, tab3 = st.tabs(["Overview", "Search", "Insights"])
        
        with tab1:
            st.header("📊 Profile Overview")
            st.write("Complete profile view - all sections")
            
            # Display all profile data (same as current "My Profile" tab)
            if data.get("user_profile"):
                st.subheader("👤 User Profile")
                profile = data["user_profile"]
                if profile.get("name"):
                    st.write(f"**Name:** {profile['name']}")
                if profile.get("current_role"):
                    st.write(f"**Current Role:** {profile['current_role']}")
                if profile.get("profile_summary"):
                    st.write(f"**Profile Summary:**")
                    st.write(profile['profile_summary'])
            
            if data.get("technical_skills"):
                st.subheader("💻 Technical Skills")
                skills = data["technical_skills"]
                if isinstance(skills, dict):
                    for category, skill_list in skills.items():
                        if isinstance(skill_list, list):
                            skills_comma_separated = ", ".join(skill_list)
                            st.write(f"**{category}:** {skills_comma_separated}")
                        else:
                            st.write(f"**{category}:** {skill_list}")
                else:
                    st.write("Skills data format not supported in overview.")
            
            if data.get("projects"):
                st.subheader("🚀 Projects")
                for project in data["projects"]:
                    with st.expander(f"{project.get('domain', 'Unknown Project')}"):
                        if project.get('role'):
                            st.write(f"**Role:** {project['role']}")
                        if project.get('description'):
                            st.write(f"**Description:** {project['description']}")
                        if project.get('related_skills'):
                            st.write(f"**Skills:** {', '.join(project['related_skills'])}")
            
            if data.get("other_activities"):
                st.subheader("🎯 Other Activities")
                for activity in data["other_activities"]:
                    with st.expander(f"{activity.get('name', 'Unknown Activity')}"):
                        st.write(f"**Type:** {activity.get('type', 'N/A')}")
                        st.write(f"**Description:** {activity.get('description', 'N/A')}")
        
        with tab2:
            st.subheader("🔍 Search Profile")
            st.write("Search through all your profile data using semantic search")
            
            # Search interface
            search_query = st.text_input("Search your profile:", placeholder="e.g., 'angular projects', 'cloud experience', 'leadership skills'")
            
            max_results = st.number_input("Max results:", min_value=1, max_value=20, value=5)
            
            if st.button("🔍 Search", type="primary"):
                if search_query:
                    with st.spinner("Searching..."):
                        try:
                            # Use the existing vector database for search (search entire profile)
                            search_results = vector_db.search(search_query, top_k=max_results)
                            
                            if search_results:
                                st.success(f"Found {len(search_results)} results:")
                                
                                for i, result in enumerate(search_results, 1):
                                    metadata = result.get('metadata', {})
                                    source = metadata.get('source', 'Unknown')
                                    result_type = metadata.get('type', 'content')
                                    
                                    # Create a more descriptive title
                                    if source == 'user_profile':
                                        title = f"Profile - {metadata.get('key', 'Info')}"
                                    elif source == 'technical_skills':
                                        title = f"Skill - {metadata.get('category', 'General')}"
                                    elif source == 'projects':
                                        title = f"Project - {metadata.get('name', 'Unknown')}"
                                    elif source == 'other_activities':
                                        title = f"Activity - {metadata.get('name', 'Unknown')}"
                                    else:
                                        title = f"{source.title()} - {result_type}"
                                    
                                    with st.expander(f"#{i} - {title} (Score: {result['score']:.3f})"):
                                        st.write(f"**Content:** {result['text']}")
                                        st.write(f"**Source:** {source.replace('_', ' ').title()}")
                                        if metadata.get('category'):
                                            st.write(f"**Category:** {metadata['category']}")
                                        if metadata.get('name') and source != 'projects':
                                            st.write(f"**Name:** {metadata['name']}")
                            else:
                                st.info("No results found. Try different keywords or check if your profile data is indexed.")
                                
                        except Exception as e:
                            st.error(f"Search error: {str(e)}")
                            st.info("💡 Try rebuilding the vector database from the sidebar if search isn't working.")
                            
                else:
                    st.warning("Please enter a search term.")
        
        with tab3:
            st.subheader("💡 AI Insights")
            st.write("Get AI-powered insights about your profile, skills, and career opportunities")
            
            # Insights interface with caching
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🎯 Analyze Profile", type="primary"):
                    with st.spinner("Analyzing your profile..."):
                        try:
                            prompt = """Analyze this professional profile and provide insights on:
                            1. Key strengths and expertise areas
                            2. Profile completeness and suggestions for improvement
                            3. Professional positioning and value proposition
                            4. Areas that could use more detail or examples
                            
                            Please be specific and actionable in your recommendations."""
                            
                            result = agent.ask_question(prompt)
                            if result["success"]:
                                st.success("✅ Profile Analysis Complete!")
                                st.write(result["response"])
                            else:
                                st.error(f"Analysis failed: {result.get('error', 'Unknown error')}")
                        except Exception as e:
                            st.error(f"Error during analysis: {str(e)}")
                
                if st.button("📈 Career Suggestions"):
                    with st.spinner("Generating career suggestions..."):
                        try:
                            prompt = """Based on this professional profile, suggest:
                            1. Potential career advancement opportunities
                            2. Related roles that would be a good fit
                            3. Industries or companies that would value this skillset
                            4. Next steps for career growth
                            
                            Focus on realistic and achievable suggestions."""
                            
                            result = agent.ask_question(prompt)
                            if result["success"]:
                                st.success("✅ Career Suggestions Ready!")
                                st.write(result["response"])
                            else:
                                st.error(f"Suggestion failed: {result.get('error', 'Unknown error')}")
                        except Exception as e:
                            st.error(f"Error generating suggestions: {str(e)}")
            
            with col2:
                if st.button("🚀 Project Ideas"):
                    with st.spinner("Brainstorming project ideas..."):
                        try:
                            prompt = """Suggest project ideas based on this professional profile:
                            1. Projects that would showcase current skills
                            2. Projects to learn new technologies
                            3. Open source contribution opportunities
                            4. Portfolio projects for career advancement
                            
                            Make suggestions specific and actionable with clear next steps."""
                            
                            result = agent.ask_question(prompt)
                            if result["success"]:
                                st.success("✅ Project Ideas Generated!")
                                st.write(result["response"])
                            else:
                                st.error(f"Project generation failed: {result.get('error', 'Unknown error')}")
                        except Exception as e:
                            st.error(f"Error generating projects: {str(e)}")
                
                if st.button("📊 Skill Analysis"):
                    with st.spinner("Analyzing skills and gaps..."):
                        try:
                            prompt = """Analyze the technical skills in this profile:
                            1. Skill strengths and areas of expertise
                            2. Potential skill gaps for current role/goals
                            3. Emerging technologies to consider learning
                            4. Skill combinations that create unique value
                            
                            Provide specific learning recommendations and resources when possible."""
                            
                            result = agent.ask_question(prompt)
                            if result["success"]:
                                st.success("✅ Skill Analysis Complete!")
                                st.write(result["response"])
                            else:
                                st.error(f"Skill analysis failed: {result.get('error', 'Unknown error')}")
                        except Exception as e:
                            st.error(f"Error during skill analysis: {str(e)}")
            
            # Cache info
            st.divider()
            st.info("💡 **Tip:** AI insights are generated in real-time based on your current profile data. Update your profile and regenerate insights to see new recommendations.")
    
    # === AI ASSISTANT PAGE ===
    elif selected_page == "AI Assistant":
        st.header("💬 Enhanced AI Assistant")
        st.write("Now with planning and memory! Ask me anything about your profile.")
        
        # Simple chat interface (enhanced from v1)
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                
                # Show simple metadata if available
                if "metadata" in message and message["metadata"]:
                    with st.expander("Details"):
                        if "plan" in message["metadata"]:
                            st.write(f"**Plan:** {' → '.join(message['metadata']['plan'])}")
                        if "execution_time" in message["metadata"]:
                            st.write(f"**Time:** {message['metadata']['execution_time']}")
                        if "context_used" in message["metadata"]:
                            st.write(f"**Context:** {message['metadata']['context_used']} items")
        
        # Chat input
        if prompt := st.chat_input("Ask me about your profile..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.write(prompt)
            
            # Process with agent and guardrails
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        # Step 1: Validate input with simple guardrails
                        is_allowed, cleaned_prompt, violations = guardrails.validate_input(prompt)
                        
                        if not is_allowed:
                            response = "I can't process that request due to safety restrictions."
                            metadata = {"violations": [v.message for v in violations]}
                        else:
                            # Step 2: Process with agent (now with planning!)
                            result = agent.ask_question(cleaned_prompt)
                            
                            if result["success"]:
                                # Step 3: Filter response
                                filtered_response, response_violations = guardrails.filter_response(result["response"])
                                
                                response = filtered_response
                                metadata = {
                                    "plan": result.get("plan", []),
                                    "execution_time": result.get("execution_time", "N/A"),
                                    "context_used": result.get("context_used", 0),
                                    "violations": len(violations + response_violations)
                                }
                            else:
                                response = result.get("response", "Sorry, I encountered an error.")
                                metadata = {"error": result.get("error", "")}
                        
                        st.write(response)
                        
                        # Show metadata
                        if metadata and any(v for v in metadata.values() if v):
                            with st.expander("Response Details"):
                                for key, value in metadata.items():
                                    if value:
                                        st.write(f"**{key.replace('_', ' ').title()}:** {value}")
                        
                        # Add to session
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response,
                            "metadata": metadata
                        })
                        
                    except Exception as e:
                        error_msg = f"Error: {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_msg,
                            "metadata": {"error": str(e)}
                        })

if __name__ == "__main__":
    main()