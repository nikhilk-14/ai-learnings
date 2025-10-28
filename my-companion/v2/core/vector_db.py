"""
Simple Vector Database using FAISS - Lightweight RAG implementation
"""
import json
import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import pickle


class VectorDB:
    """
    Lightweight vector database using FAISS for RAG implementation
    """
    
    def __init__(self, embedding_model=None, index_path=None):
        # Use environment variables with fallbacks
        self.embedding_model_name = embedding_model or os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        self.embedding_model = SentenceTransformer(self.embedding_model_name)
        self.embedding_dim = 384  # Dimension for all-MiniLM-L6-v2
        self.index_path = index_path or os.getenv("VECTOR_INDEX_PATH", "data/vector_index")
        self.metadata_path = f"{index_path}_metadata.pkl"
        
        # Initialize FAISS index
        self.index = faiss.IndexFlatIP(self.embedding_dim)  # Inner product for cosine similarity
        self.metadata = []  # Store metadata for each vector
        
        # Load existing index if available
        self.load_index()
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """
        Add documents to the vector database
        documents: List of {"text": str, "metadata": dict}
        """
        if not documents:
            return
        
        # Extract texts and embed them
        texts = [doc["text"] for doc in documents]
        embeddings = self.embedding_model.encode(texts, convert_to_tensor=False)
        
        # Normalize embeddings for cosine similarity
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        # Add to FAISS index
        self.index.add(embeddings.astype('float32'))
        
        # Store metadata
        for doc in documents:
            self.metadata.append(doc.get("metadata", {}))
        
        # Save updated index
        self.save_index()
    
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Optimized search for similar documents with quality filtering
        Returns: List of {"text": str, "metadata": dict, "score": float}
        """
        if self.index.ntotal == 0:
            return []
        
        # Embed query
        query_embedding = self.embedding_model.encode([query], convert_to_tensor=False)
        query_embedding = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True)
        
        # Search in FAISS with increased search space for better filtering
        search_k = min(top_k * 2, self.index.ntotal)  # Search more to filter better
        scores, indices = self.index.search(query_embedding.astype('float32'), search_k)
        
        # Prepare results with quality filtering
        results = []
        score_threshold = 0.3  # Only include results with decent similarity
        
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.metadata) and score >= score_threshold:  # Quality filter
                text = self.metadata[idx].get("text", "")
                
                # Truncate long texts for faster processing
                if len(text) > 150:
                    text = text[:147] + "..."
                
                results.append({
                    "text": text,
                    "metadata": self.metadata[idx],
                    "score": float(score)
                })
        
        # Return only top_k results after filtering
        return results[:top_k]
    
    def rebuild_from_data(self, data: Dict[str, Any]) -> int:
        """
        Rebuild vector database from knowledge base data
        Returns: number of documents added
        """
        # Clear existing index
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        self.metadata = []
        
        documents = []
        
        # Process different data sections
        if "basic_info" in data:
            for key, value in data["basic_info"].items():
                documents.append({
                    "text": f"{key}: {value}",
                    "metadata": {
                        "source": "basic_info",
                        "type": "profile",
                        "key": key,
                        "text": f"{key}: {value}"
                    }
                })
        
        # Process user_profile section (V1 format)
        if "user_profile" in data:
            profile = data["user_profile"]
            for key, value in profile.items():
                if key not in ["attachments", "urls"] and value:  # Skip empty and file references
                    if isinstance(value, str):
                        documents.append({
                            "text": f"{key}: {value}",
                            "metadata": {
                                "source": "user_profile",
                                "type": "profile",
                                "key": key,
                                "text": f"{key}: {value}"
                            }
                        })
        
        if "technical_skills" in data:
            skills = data["technical_skills"]
            if isinstance(skills, dict):
                # V1 format: {"category": ["skill1", "skill2"]}
                for category, skill_list in skills.items():
                    if isinstance(skill_list, list):
                        for skill_name in skill_list:
                            text = f"Technical Skill ({category}): {skill_name}"
                            documents.append({
                                "text": text,
                                "metadata": {
                                    "source": "technical_skills",
                                    "type": "skill",
                                    "name": skill_name,
                                    "category": category,
                                    "proficiency": "",
                                    "text": text
                                }
                            })
            elif isinstance(skills, list):
                # V2 format: [{"name": "", "category": "", "proficiency": ""}]
                for skill in skills:
                    text = f"Technical Skill: {skill.get('name', '')} - {skill.get('description', '')}"
                    documents.append({
                        "text": text,
                        "metadata": {
                            "source": "technical_skills",
                            "type": "skill",
                            "name": skill.get("name", ""),
                            "category": skill.get("category", ""),
                            "proficiency": skill.get("proficiency", ""),
                            "text": text
                        }
                    })
        
        if "projects" in data:
            for project in data["projects"]:
                # Handle both V1 (domain) and V2 (name) formats
                project_name = project.get('domain', '') or project.get('name', '')
                text = f"Project: {project_name} - {project.get('description', '')}"
                
                # Handle both technologies and related_skills
                technologies = project.get("technologies", []) or project.get("related_skills", [])
                if technologies:
                    if isinstance(technologies, list):
                        text += f" Technologies: {', '.join(technologies)}"
                    else:
                        text += f" Technologies: {technologies}"
                
                documents.append({
                    "text": text,
                    "metadata": {
                        "source": "projects",
                        "type": "project",
                        "name": project_name,
                        "technologies": technologies,
                        "text": text
                    }
                })
        
        if "other_activities" in data:
            for activity in data["other_activities"]:
                text = f"Activity: {activity.get('name', '')} - {activity.get('description', '')}"
                documents.append({
                    "text": text,
                    "metadata": {
                        "source": "other_activities",
                        "type": "activity",
                        "name": activity.get("name", ""),
                        "activity_type": activity.get("type", ""),
                        "text": text
                    }
                })
        
        # Add all documents to vector DB
        if documents:
            self.add_documents(documents)
        
        return len(documents)
    
    def save_index(self):
        """Save FAISS index and metadata to disk"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            
            # Save FAISS index
            faiss.write_index(self.index, f"{self.index_path}.faiss")
            
            # Save metadata
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(self.metadata, f)
        except Exception as e:
            print(f"Error saving index: {e}")
    
    def load_index(self):
        """Load FAISS index and metadata from disk"""
        try:
            # Load FAISS index
            if os.path.exists(f"{self.index_path}.faiss"):
                self.index = faiss.read_index(f"{self.index_path}.faiss")
            
            # Load metadata
            if os.path.exists(self.metadata_path):
                with open(self.metadata_path, 'rb') as f:
                    self.metadata = pickle.load(f)
        except Exception as e:
            print(f"Error loading index: {e}")
            # Reset to empty state on error
            self.index = faiss.IndexFlatIP(self.embedding_dim)
            self.metadata = []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector database statistics"""
        return {
            "total_documents": self.index.ntotal,
            "embedding_dimension": self.embedding_dim,
            "model": "all-MiniLM-L6-v2",
            "index_type": "FAISS IndexFlatIP"
        }