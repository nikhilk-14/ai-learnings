"""
Profile Overview Module
Displays consolidated view of all profile data including user profile, technical skills, projects, and other activities.
"""
import streamlit as st


def show(data):
    """Display complete profile overview - all sections"""
    st.header("📊 Profile Overview")
    st.write("Complete profile view - all sections")
    
    # Display all profile data
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
            with st.expander(f"{activity.get('title', 'Unknown Activity')}"):
                st.write(f"**Type:** {activity.get('title', 'N/A')}")
                st.write(f"**Description:** {activity.get('description', 'N/A')}")