# projects.py
import streamlit as st
from utils.data_store import save_data

def show(data):
    st.subheader("🧱 Project Experience")

    if "projects" not in data:
        data["projects"] = []
    projects = data["projects"]

    # --- Session flag to safely clear add-project form ---
    if "clear_add_project_form" not in st.session_state:
        st.session_state.clear_add_project_form = False

    # Clear form safely at the start of the run
    if st.session_state.clear_add_project_form:
        for key in ["add_domain","add_role","add_description","add_responsibilities","add_related_skills","add_tags"]:
            st.session_state[key] = ""
        st.session_state.clear_add_project_form = False

    # --- Add New Project ---
    st.markdown("### ➕ Add New Project")
    domain = st.text_input("Project Domain", key="add_domain")
    role = st.text_input("Role", key="add_role")
    description = st.text_area("Description", key="add_description", height=100)
    responsibilities = st.text_area("Responsibilities", key="add_responsibilities", height=100)
    related_skills = st.text_area("Related Skills (comma-separated)", key="add_related_skills")
    tags = st.text_area("Tags (comma-separated)", key="add_tags")

    if st.button("💾 Add Project"):
        if not domain.strip() or not role.strip():
            st.warning("Please enter at least Domain and Role.")
        else:
            new_project = {
                "domain": domain.strip(),
                "role": role.strip(),
                "description": description.strip(),
                "responsibilities": responsibilities.strip(),
                "related_skills": [s.strip() for s in related_skills.split(",") if s.strip()],
                "tags": [t.strip() for t in tags.split(",") if t.strip()]
            }
            projects.append(new_project)
            data["projects"] = projects
            save_data(data)
            st.success("✅ Project added successfully!")
            st.session_state.clear_add_project_form = True
            st.rerun()  # triggers page rerun so cleared fields apply safely

    st.divider()
    st.markdown("### 📋 Existing Projects")

    if not projects:
        st.info("No projects found. Add your first one above.")
    else:
        for idx, proj in enumerate(projects):
            with st.expander(f"🔹 {proj.get('domain', 'Untitled')} — {proj.get('role', '')}", expanded=False):
                # Editable fields
                domain_edit = st.text_input("Domain", value=proj.get("domain",""), key=f"domain_{idx}")
                role_edit = st.text_input("Role", value=proj.get("role",""), key=f"role_{idx}")
                description_edit = st.text_area("Description", value=proj.get("description",""), key=f"description_{idx}", height=100)
                responsibilities_edit = st.text_area(
                    "Responsibilities",
                    value=proj.get("responsibilities",""),
                    key=f"responsibilities_{idx}",
                    height=100
                )
                related_skills_edit = st.text_area(
                    "Related Skills (comma-separated)",
                    value=", ".join(proj.get("related_skills",[])),
                    key=f"related_skills_{idx}"
                )
                tags_edit = st.text_area(
                    "Tags (comma-separated)",
                    value=", ".join(proj.get("tags",[])),
                    key=f"tags_{idx}"
                )

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Save", key=f"save_{idx}"):
                        # Update project in JSON
                        projects[idx] = {
                            "domain": domain_edit.strip(),
                            "role": role_edit.strip(),
                            "description": description_edit.strip(),
                            "responsibilities": responsibilities_edit.strip(),
                            "related_skills": [s.strip() for s in related_skills_edit.split(",") if s.strip()],
                            "tags": [t.strip() for t in tags_edit.split(",") if t.strip()]
                        }
                        data["projects"] = projects
                        save_data(data)
                        st.success("✅ Project updated successfully!")
                        # Clear add-project form fields safely
                        st.session_state.clear_add_project_form = True
                        st.rerun()

                with col2:
                    if st.button("❌ Delete Project", key=f"del_{idx}"):
                        projects.pop(idx)
                        data["projects"] = projects
                        save_data(data)
                        st.warning("Project deleted successfully!")
                        st.rerun()
