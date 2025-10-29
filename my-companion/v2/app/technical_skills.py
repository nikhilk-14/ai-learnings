# technical_skills.py
import streamlit as st
from utils.data_store import save_data

DEFAULT_CATEGORIES = [
    "Programming Languages",
    "Frontend Technologies",
    "Backend Technologies",
    "Frameworks & Libraries",
    "Databases",
    "DevOps Tools",
    "Cloud Platforms",
    "Other"
]

def ensure_skills_structure(data):
    if "technical_skills" not in data:
        data["technical_skills"] = {}
    return data


def show(data):
    """
    Technical Skills UI
    - Choose existing or default category
    - Add new category dynamically
    - Add comma-separated skills
    - Remove skills
    """
    st.subheader("🧠 Technical Skills")

    data = ensure_skills_structure(data)
    skills_data = data["technical_skills"]

    # --- Session flags for safe clearing ---
    if "clear_skills_input" not in st.session_state:
        st.session_state.clear_skills_input = False

    if st.session_state.clear_skills_input:
        st.session_state["skills_input"] = ""
        st.session_state.clear_skills_input = False

    # --- Category selectbox ---
    # Safe check: ensure skills_data is a dictionary
    if not isinstance(skills_data, dict):
        skills_data = {}
        data["technical_skills"] = skills_data
        save_data(data)
    
    existing_categories = [c for c in skills_data.keys() if c not in DEFAULT_CATEGORIES]
    category_options = DEFAULT_CATEGORIES + existing_categories + ["➕ Add New Category"]

    category = st.selectbox("Select or add category", options=category_options, key="category_select")

    # --- Handle new category creation ---
    if category == "➕ Add New Category":
        new_cat = st.text_input("Enter new category name", key="new_category_name")
        if st.button("✅ Add Category"):
            new_cat = new_cat.strip()
            if not new_cat:
                st.warning("Please enter a valid category name.")
            elif new_cat in skills_data or new_cat in DEFAULT_CATEGORIES:
                st.warning(f"'{new_cat}' already exists.")
            else:
                # Add new category to JSON
                skills_data[new_cat] = []
                data["technical_skills"] = skills_data
                save_data(data)
                st.success(f"Added new category '{new_cat}'")
                st.rerun()  # page rerun to refresh selectbox
        st.stop()  # stop here so skills input is not shown prematurely

    # --- Add skills input ---
    skills_text = st.text_input(
        f"Enter skills for '{category}' (comma separated)",
        value=st.session_state.get("skills_input", ""),
        key="skills_input"
    )

    if st.button("➕ Add Skills"):
        text = skills_text.strip()
        if not text:
            st.warning("Please enter at least one skill.")
        else:
            new_skills = [s.strip() for s in text.split(",") if s.strip()]
            if new_skills:
                if category not in skills_data:
                    skills_data[category] = []
                # Deduplicate (case-insensitive)
                existing_lower = {s.lower(): s for s in skills_data[category]}
                for ns in new_skills:
                    if ns.lower() not in existing_lower:
                        skills_data[category].append(ns)
                data["technical_skills"] = skills_data
                save_data(data)
                st.success(f"Added {len(new_skills)} skill(s) to '{category}'")
                # Clear input safely
                st.session_state.clear_skills_input = True
                st.rerun()

    st.markdown("---")

    # --- Display categories and skills ---
    if skills_data:
        for cat in list(skills_data.keys()):
            skills = skills_data.get(cat, [])
            with st.expander(f"📂 {cat} ({len(skills)})", expanded=False):
                if not skills:
                    st.info("No skills yet in this category.")
                for idx, skill in enumerate(list(skills)):
                    col1, col2 = st.columns([9, 1])
                    with col1:
                        st.write(f"- {skill}")
                    with col2:
                        if st.button("❌", key=f"remove__{cat}__{skill}"):
                            skills.remove(skill)
                            if not skills:
                                del skills_data[cat]
                            data["technical_skills"] = skills_data
                            save_data(data)
                            st.success(f"Removed '{skill}' from '{cat}'")
                            st.rerun()
    else:
        st.info("No technical skills added yet.")
