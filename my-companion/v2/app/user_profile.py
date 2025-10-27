import streamlit as st
import os
import json
from utils.data_store import save_data
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ATTACHMENTS_DIR = os.getenv("BASIC_INFO_ATTACHMENTS_DIR", "data/attachments/basic_info")

def ensure_data_structure(data):
    if "user_profile" not in data or not isinstance(data["user_profile"], dict):
        data["user_profile"] = {
            "name": "",
            "current_role": "",
            "profile_summary": "",
            "attachments": [],
            "urls": []
        }
    return data


def show(data):
    """Basic Info + Additional Details (editable-only view)"""
    st.subheader("👤 Basic Info")

    data = ensure_data_structure(data)
    profile = data["user_profile"]

    # --- Basic Details ---
    profile["name"] = st.text_input("Full Name", profile.get("name", ""))
    profile["current_role"] = st.text_input("Current Role", profile.get("current_role", ""))
    profile["profile_summary"] = st.text_area("Profile Summary", profile.get("profile_summary", ""), height=150)

    if st.button("💾 Save Basic Info"):
        data["user_profile"] = profile
        save_data(data)
        st.success("✅ Basic info saved successfully!")
        st.rerun()

    st.markdown("---")
    st.subheader("📎 Additional Details")

    # === Attachments ===
    st.markdown("#### Attachments")

    os.makedirs(ATTACHMENTS_DIR, exist_ok=True)
    attachments = profile.get("attachments", [])

    uploaded_files = st.file_uploader("Upload files", accept_multiple_files=True, key="upload_key")
    if uploaded_files:
        for f in uploaded_files:
            save_path = os.path.join(ATTACHMENTS_DIR, f.name)
            with open(save_path, "wb") as out:
                out.write(f.getbuffer())
            if f.name not in attachments:
                attachments.append(f.name)

        profile["attachments"] = attachments
        data["user_profile"] = profile
        save_data(data)
        st.success("✅ Uploaded successfully!")
        st.rerun()

    if attachments:
        for att in attachments:
            col1, col2 = st.columns([8, 1])
            with col1:
                file_path = os.path.join(ATTACHMENTS_DIR, att)
                if os.path.exists(file_path):
                    with open(file_path, "rb") as file:
                        st.download_button("⬇️ " + att, file, file_name=att, key=f"dl_{att}")
            with col2:
                if st.button("❌", key=f"del_{att}"):
                    try:
                        os.remove(os.path.join(ATTACHMENTS_DIR, att))
                    except FileNotFoundError:
                        pass
                    attachments.remove(att)
                    profile["attachments"] = attachments
                    data["user_profile"] = profile
                    save_data(data)
                    st.success(f"🗑️ Removed {att}")
                    st.rerun()
    else:
        st.info("No attachments uploaded yet.")

    st.markdown("---")

    # === URLs ===
    st.markdown("#### 🔗 URLs")
    urls = profile.get("urls", [])

    # show existing URLs
    if urls:
        for i, url in enumerate(urls):
            col1, col2 = st.columns([8, 1])
            with col1:
                st.markdown(f"[🌐 {url}]({url})", unsafe_allow_html=True)
            with col2:
                if st.button("❌", key=f"del_url_{i}"):
                    urls.pop(i)
                    profile["urls"] = urls
                    data["user_profile"] = profile
                    save_data(data)
                    st.success(f"🗑️ Removed {url}")
                    st.rerun()
    else:
        st.info("No URLs added yet.")

    # input for new URL
    new_url = st.text_input("Add new URL", key="new_url_input_key", placeholder="https://example.com")
    if st.button("➕ Add URL"):
        new_url = new_url.strip()
        if new_url:
            urls.append(new_url)
            profile["urls"] = urls
            data["user_profile"] = profile
            save_data(data)
            st.success(f"✅ Added new URL: {new_url}")
            st.rerun()
        else:
            st.warning("Please enter a valid URL.")
