"""
Data Store utilities for V2 - Compatible with V1 schema
Works with existing V1 data structure without modifications
Auto-syncs with vector database for search and AI features
"""
import json
import os
from typing import Dict, Any, Optional

def load_data() -> Dict[str, Any]:
    """Load knowledge base data using existing V1 schema"""
    try:
        with open("data/knowledge_base.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "user_profile": {
                "name": "",
                "current_role": "",
                "profile_summary": "",
                "attachments": [],
                "urls": []
            },
            "technical_skills": {},
            "projects": [],
            "other_activities": []
        }

def save_data(data: Dict[str, Any], auto_sync: bool = True) -> bool:
    """
    Save data to knowledge base and optionally sync with vector database
    
    Args:
        data: Profile data to save
        auto_sync: Whether to automatically rebuild vector database (default: True)
    """
    try:
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Save to JSON file
        with open("data/knowledge_base.json", "w") as f:
            json.dump(data, f, indent=2)
        
        # Auto-sync with vector database if enabled
        # Can be disabled via environment variable for performance
        auto_sync_enabled = os.getenv("AUTO_SYNC_VECTOR_DB", "true").lower() == "true"
        
        if auto_sync and auto_sync_enabled:
            try:
                # Import here to avoid circular imports
                from core.agent import Agent
                from core.vector_db import VectorDB
                from openai import OpenAI
                from dotenv import load_dotenv
                
                load_dotenv()
                
                # Initialize components for vector DB rebuild
                llm_client = OpenAI(
                    base_url=os.getenv("LLM_BASE_URL", "http://localhost:1234/v1"),
                    api_key=os.getenv("LLM_API_KEY", "lm-studio")
                )
                vector_db = VectorDB()
                agent = Agent(llm_client, load_data, vector_db)
                
                # Rebuild vector database with new data
                rebuild_result = agent.rebuild_knowledge_base()
                if rebuild_result.get("success", False):
                    print("✅ Vector database synchronized with profile changes")
                else:
                    print(f"⚠️ Vector DB sync failed: {rebuild_result.get('error', 'Unknown error')}")
                
            except Exception as sync_error:
                print(f"⚠️ Could not sync with vector database: {sync_error}")
                print("💡 Manual rebuild available in sidebar if search seems outdated")
                # Don't fail the save operation if vector sync fails
        
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False

def get_data_stats() -> Dict[str, int]:
    """Get data statistics from V1 schema"""
    data = load_data()
    return {
        "user_profile_fields": len(data.get("user_profile", {})),
        "technical_skills": len(data.get("technical_skills", {})) if isinstance(data.get("technical_skills"), dict) else len(data.get("technical_skills", [])),
        "projects": len(data.get("projects", [])),
        "other_activities": len(data.get("other_activities", []))
    }