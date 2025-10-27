# other_activities.py
import streamlit as st
import os
import uuid
from utils.data_store import save_data
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

UPLOAD_DIR = os.getenv("OTHER_ACTIVITIES_ATTACHMENTS_DIR", "data/attachments/other_activities")

def ensure_other_activities_structure(data):
    if "other_activities" not in data:
        data["other_activities"] = []
    return data

def show(data):
    st.subheader("🎯 Other Activities")
    data = ensure_other_activities_structure(data)
    activities = data["other_activities"]

    # Assign stable UID for all activities
    for act in activities:
        if "uid" not in act:
            act["uid"] = str(uuid.uuid4())

    # --- Add New Activity Form ---
    st.markdown("### ➕ Add New Activity")
    if "clear_activity_form" not in st.session_state:
        st.session_state.clear_activity_form = False

    if st.session_state.clear_activity_form:
        for key in ["act_title","act_description","act_skills","act_tags"]:
            st.session_state[key] = ""
        st.session_state.clear_activity_form = False

    title = st.text_input("Title", key="act_title")
    description = st.text_area("Description", key="act_description", height=100)
    related_skills = st.text_input("Related Skills (comma-separated)", key="act_skills")
    tags = st.text_input("Tags (comma-separated)", key="act_tags")

    if st.button("💾 Add Activity", key="add_activity_button"):
        if not title.strip():
            st.warning("Please enter activity title.")
        else:
            new_activity = {
                "uid": str(uuid.uuid4()),
                "title": title.strip(),
                "description": description.strip(),
                "related_skills": [s.strip() for s in related_skills.split(",") if s.strip()],
                "attachments": [],
                "urls": [],
                "tags": [t.strip() for t in tags.split(",") if t.strip()]
            }
            activities.append(new_activity)
            data["other_activities"] = activities
            save_data(data)
            st.success("✅ Activity added successfully!")
            st.session_state.clear_activity_form = True

    st.divider()
    st.markdown("### 📋 Existing Activities")

    if not activities:
        st.info("No activities added yet.")
        return

    for act in activities:
        uid = act["uid"]
        with st.expander(f"🔹 {act.get('title','Untitled Activity')}", expanded=False):
            # Editable fields
            title_edit = st.text_input("Title", value=act.get("title",""), key=f"title_{uid}")
            description_edit = st.text_area("Description", value=act.get("description",""), key=f"description_{uid}", height=100)
            skills_edit = st.text_input("Related Skills (comma-separated)", value=", ".join(act.get("related_skills",[])), key=f"skills_{uid}")
            tags_edit = st.text_input("Tags (comma-separated)", value=", ".join(act.get("tags",[])), key=f"tags_{uid}")

            # Save / Delete activity
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Save", key=f"save_{uid}"):
                    act["title"] = title_edit.strip()
                    act["description"] = description_edit.strip()
                    act["related_skills"] = [s.strip() for s in skills_edit.split(",") if s.strip()]
                    act["tags"] = [t.strip() for t in tags_edit.split(",") if t.strip()]
                    data["other_activities"] = activities
                    save_data(data)
                    st.success("✅ Activity updated successfully!")

            with col2:
                if st.button("❌ Delete Activity", key=f"del_act_{uid}"):
                    activities.remove(act)
                    data["other_activities"] = activities
                    save_data(data)
                    st.warning("Activity deleted successfully!")

            # --- Attachments Section ---
            st.markdown("#### 📎 Attachments")
            uploaded_files = st.file_uploader(
                "Upload attachments",
                accept_multiple_files=True,
                type=["pdf","docx","txt","png","jpg"],
                key=f"uploads_{uid}"
            )
            if uploaded_files:
                os.makedirs(UPLOAD_DIR, exist_ok=True)
                for f in uploaded_files:
                    if f.name not in act["attachments"]:
                        act["attachments"].append(f.name)
                        with open(os.path.join(UPLOAD_DIR, f.name), "wb") as out_file:
                            out_file.write(f.getbuffer())
                data["other_activities"] = activities
                save_data(data)
                st.success("✅ Attachments uploaded successfully!")

            # Show attachments with remove & download
            attachments_list = act.get("attachments", [])
            for att_idx, att in enumerate(attachments_list.copy()):
                col1, col2 = st.columns([8,1])
                with col1:
                    att_path = os.path.join(UPLOAD_DIR, att)
                    if os.path.exists(att_path):
                        with open(att_path, "rb") as file:
                            st.download_button("⬇️ " + att, file, file_name=att, key=f"dl_{att}")
                with col2:
                    if st.button("❌", key=f"del_att_{uid}_{att_idx}"):
                        attachments_list.pop(att_idx)
                        act["attachments"] = attachments_list
                        att_path = os.path.join(UPLOAD_DIR, att)
                        if os.path.exists(att_path):
                            os.remove(att_path)
                        data["other_activities"] = activities
                        save_data(data)
                        st.success(f"Removed attachment '{att}'")

            # --- URLs Section ---
            st.markdown("#### 🔗 URLs")
            if f"urls_input_{uid}" not in st.session_state:
                st.session_state[f"urls_input_{uid}"] = ""
            new_url = st.text_input("Add new URL", value=st.session_state[f"urls_input_{uid}"], key=f"url_input_{uid}")
            if st.button("➕ Add URL", key=f"add_url_{uid}"):
                if new_url.strip():
                    act["urls"].append(new_url.strip())
                    st.session_state[f"urls_input_{uid}"] = ""
                    data["other_activities"] = activities
                    save_data(data)
                    st.success(f"Added URL '{new_url.strip()}'")
                else:
                    st.warning("Enter a valid URL.")

            # Show URLs with remove
            urls_list = act.get("urls", [])
            for u_idx, u in enumerate(urls_list.copy()):
                col1, col2 = st.columns([8,1])
                with col1:
                    st.markdown(f"- [{u}]({u})", unsafe_allow_html=True)
                with col2:
                    if st.button("❌", key=f"del_url_{uid}_{u_idx}"):
                        urls_list.pop(u_idx)
                        act["urls"] = urls_list
                        data["other_activities"] = activities
                        save_data(data)
                        st.success(f"Removed URL '{u}'")
