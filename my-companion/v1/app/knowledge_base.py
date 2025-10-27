import streamlit as st
import json
import os
from utils.data_store import load_data
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ATTACHMENTS_DIR = os.getenv("ATTACHMENTS_DIR", "data/attachments")

def show(data):
    st.subheader("🧠 Knowledge Base")

    # Create tabs for Raw JSON and Readable View
    tab1, tab2 = st.tabs(["📄 Raw JSON", "📘 Readable View"])

    # --- RAW JSON TAB ---
    with tab1:
        st.markdown("### 📄 Raw JSON View")
        st.info("Read-only JSON data. Click '🔄 Refresh' to reload the latest saved file.")

        if st.button("🔄 Refresh Data"):
            data = load_data()
            st.success("Data refreshed successfully!")

        st.json(data)

    # --- READABLE VIEW TAB ---
    with tab2:
        st.markdown("### 📘 Structured View")

        # --- BASIC INFO ---
        basic_info = data.get("user_profile", {})
        with st.expander("👤 Basic Info", expanded=True):
            st.markdown(f"**Name:** {basic_info.get('name', '_Not provided_')}")
            st.markdown(f"**Role:** {basic_info.get('current_role', '_Not provided_')}")
            st.markdown(f"**Summary:** {basic_info.get('profile_summary', '_Not provided_')}")

            # Attachments
            attachments = basic_info.get("attachments", [])
            if attachments:
                st.markdown("**Attachments:**")
                for att in attachments:
                    file_path = os.path.join(ATTACHMENTS_DIR +'/basic_info', att)
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as f:
                            st.download_button(
                                label=f"📎 {att}",
                                data=f,
                                file_name=att,
                                mime="application/octet-stream",
                                key=f"download_basic_{att}"
                            )
                    else:
                        st.warning(f"⚠️ {att} (file not found)")
            else:
                st.info("No attachments uploaded.")

            # URLs
            urls = basic_info.get("urls", [])
            if urls:
                st.markdown("**URLs:**")
                for u in urls:
                    st.markdown(f"- 🔗 [{u}]({u})")
            else:
                st.info("No URLs added.")

        # --- TECHNICAL SKILLS ---
        skills = data.get("technical_skills", {})
        with st.expander("💡 Technical Skills", expanded=False):
            if skills:
                for category, skill_list in skills.items():
                    st.markdown(f"**{category}:** {', '.join(skill_list)}")
            else:
                st.info("No technical skills added yet.")

        # --- PROJECTS ---
        projects = data.get("projects", [])
        with st.expander("🧱 Projects", expanded=False):
            if projects:
                for idx, proj in enumerate(projects, 1):
                    st.markdown(f"#### {idx}. {proj.get('domain', 'Untitled Project')}")
                    st.markdown(f"**Role:** {proj.get('role', '_Not provided_')}")
                    st.markdown(f"**Description:** {proj.get('description', '')}")

                    responsibilities = proj.get("responsibilities", "")
                    if responsibilities:
                        st.markdown("**Responsibilities:**")
                        st.markdown(responsibilities)

                    related_skills = proj.get("related_skills", [])
                    if related_skills:
                        st.markdown(f"**Related Skills:** {', '.join(related_skills)}")

                    tags = proj.get("tags", [])
                    if tags:
                        st.markdown(f"**Tags:** {', '.join(tags)}")

                    st.markdown("---")
            else:
                st.info("No projects found.")

        # --- OTHER ACTIVITIES ---
        other_activities = data.get("other_activities", [])
        with st.expander("🎯 Other Activities", expanded=False):
            if other_activities:
                for idx, act in enumerate(other_activities, 1):
                    st.markdown(f"#### {idx}. {act.get('title', 'Untitled Activity')}")
                    st.markdown(f"**Description:** {act.get('description', '_Not provided_')}")

                    related_skills = act.get("related_skills", [])
                    if related_skills:
                        st.markdown(f"**Related Skills:** {', '.join(related_skills)}")

                    attachments = act.get("attachments", [])
                    if attachments:
                        st.markdown("**Attachments:**")
                        for att in attachments:
                            file_path = os.path.join(ATTACHMENTS_DIR + '/other_activities', att)
                            if os.path.exists(file_path):
                                with open(file_path, "rb") as f:
                                    st.download_button(
                                        label=f"📎 {att}",
                                        data=f,
                                        file_name=att,
                                        mime="application/octet-stream",
                                        key=f"download_act_{idx}_{att}"
                                    )
                            else:
                                st.warning(f"⚠️ {att} (file not found)")
                    else:
                        st.info("No attachments.")

                    urls = act.get("urls", [])
                    if urls:
                        st.markdown("**URLs:**")
                        for u in urls:
                            st.markdown(f"- 🔗 [{u}]({u})")
                    else:
                        st.info("No URLs.")

                    tags = act.get("tags", [])
                    if tags:
                        st.markdown(f"**Tags:** {', '.join(tags)}")

                    st.markdown("---")
            else:
                st.info("No other activities found.")
