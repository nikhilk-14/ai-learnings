"""
Simple Lightweight Agent - Minimal Agentic AI for v2
Just adds basic planning and memory to existing v1 functionality
"""
import json
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Message:
    """Simple message for conversation history"""
    role: str
    content: str
    timestamp: str


class Agent:
    """
    Lightweight agent that adds basic planning and memory to v1
    No complex frameworks, just simple planning logic
    """
    
    def __init__(self, llm_client, data_loader, vector_db=None):
        self.llm_client = llm_client
        self.data_loader = data_loader
        self.vector_db = vector_db
        self.conversation_history: List[Message] = []
        self.max_history = 20
    
    def _add_to_history(self, role: str, content: str):
        """Add message to conversation history"""
        message = Message(
            role=role,
            content=content,
            timestamp=datetime.now().isoformat()
        )
        self.conversation_history.append(message)
        
        # Keep only recent messages
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
    
    def _create_simple_plan(self, question: str) -> List[str]:
        """
        Create a simple plan for answering the question
        No complex planning framework, just basic logic
        """
        question_lower = question.lower()
        
        # Simple keyword-based planning
        plan_steps = []
        
        # Always start with understanding the question
        plan_steps.append("understand_question")
        
        # Check if we need to search data
        search_keywords = ['project', 'skill', 'experience', 'work', 'activity', 'what', 'when', 'how', 'list', 'show']
        if any(keyword in question_lower for keyword in search_keywords):
            plan_steps.append("search_knowledge")
        
        # Check if we need analysis
        analysis_keywords = ['analyze', 'compare', 'recommend', 'suggest', 'best', 'improve', 'insight']
        if any(keyword in question_lower for keyword in analysis_keywords):
            plan_steps.append("analyze_data")
        
        # Always end with generating response
        plan_steps.append("generate_response")
        
        return plan_steps
    
    def _execute_step(self, step: str, question: str, context: Dict = None) -> Dict:
        """Execute a single plan step"""
        if context is None:
            context = {}
        
        if step == "understand_question":
            return {"understanding": f"Processing question: {question}"}
        
        elif step == "search_knowledge":
            # Enhanced RAG-based search
            try:
                relevant_data = []
                
                # Primary: Vector search (semantic similarity)
                if self.vector_db:
                    vector_results = self.vector_db.search(question, top_k=5)
                    for result in vector_results:
                        relevant_data.append({
                            "type": "vector_search",
                            "text": result["text"],
                            "metadata": result["metadata"],
                            "score": result["score"]
                        })
                
                # Secondary: Keyword search as fallback
                data = self.data_loader()
                question_words = question.lower().split()
                
                # Search in different data sections
                for section, items in data.items():
                    if isinstance(items, list):
                        for item in items:
                            item_text = json.dumps(item).lower()
                            if any(word in item_text for word in question_words):
                                relevant_data.append({
                                    "type": "keyword_search",
                                    "section": section, 
                                    "item": item,
                                    "score": 0.5  # Lower score for keyword matches
                                })
                
                # Sort by score (vector results first)
                relevant_data.sort(key=lambda x: x.get("score", 0), reverse=True)
                
                return {"search_results": relevant_data[:8]}  # Limit results
            except Exception as e:
                return {"search_results": [], "error": str(e)}
        
        elif step == "analyze_data":
            search_results = context.get("search_results", [])
            if search_results:
                return {"analysis": f"Found {len(search_results)} relevant items for analysis"}
            else:
                return {"analysis": "No data found for analysis"}
        
        elif step == "generate_response":
            return {"ready_to_respond": True}
        
        return {"step_result": f"Completed {step}"}
    
    def ask_question(self, question: str) -> Dict[str, Any]:
        """
        Main method to ask a question with simple agentic behavior
        """
        start_time = time.time()
        
        # Add user question to history
        self._add_to_history("user", question)
        
        try:
            # Step 1: Create simple plan
            plan = self._create_simple_plan(question)
            
            # Step 2: Execute plan steps
            execution_context = {}
            for step in plan:
                step_result = self._execute_step(step, question, execution_context)
                execution_context.update(step_result)
            
            # Step 3: Generate final response using LLM
            response = self._generate_llm_response(question, execution_context)
            
            # Add response to history
            self._add_to_history("assistant", response)
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "response": response,
                "plan": plan,
                "execution_time": f"{execution_time:.2f}s",
                "context_used": len(execution_context.get("search_results", []))
            }
        
        except Exception as e:
            error_response = f"Sorry, I encountered an error: {str(e)}"
            self._add_to_history("assistant", error_response)
            
            return {
                "success": False,
                "response": error_response,
                "error": str(e)
            }
    
    def _generate_llm_response(self, question: str, context: Dict) -> str:
        """Generate response using LLM with context"""
        
        # Build enhanced context for LLM using RAG results
        context_text = ""
        search_results = context.get("search_results", [])
        
        if search_results:
            context_text = "Relevant information from your profile:\n"
            for i, result in enumerate(search_results[:5], 1):
                if result.get("type") == "vector_search":
                    score = result.get("score", 0)
                    context_text += f"{i}. [Vector Match {score:.2f}] {result['text']}\n"
                elif result.get("type") == "keyword_search" and "item" in result:
                    context_text += f"{i}. [Keyword Match] {json.dumps(result['item'], indent=2)}\n"
                else:
                    context_text += f"{i}. {str(result)}\n"
        
        # Build conversation history context
        history_text = ""
        if len(self.conversation_history) > 1:  # More than just current question
            history_text = "\nRecent conversation:\n"
            for msg in self.conversation_history[-6:-1]:  # Last 5 messages, excluding current
                history_text += f"{msg.role}: {msg.content}\n"
        
        # Create prompt for LLM
        prompt = f"""You are a helpful personal assistant. Answer the user's question based on their profile data.

{context_text}
{history_text}

User Question: {question}

Provide a helpful, personalized response based on the information available."""
        
        try:
            # Call LLM (same as v1 approach)
            response = self.llm_client.chat.completions.create(
                model="lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            return f"I'm having trouble connecting to the AI service: {str(e)}"
    
    def get_conversation_history(self) -> List[Dict]:
        """Get recent conversation history"""
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp
            }
            for msg in self.conversation_history
        ]
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def rebuild_knowledge_base(self) -> Dict[str, Any]:
        """Rebuild the vector database from current data"""
        try:
            if not self.vector_db:
                return {"success": False, "error": "No vector database available"}
            
            data = self.data_loader()
            documents_added = self.vector_db.rebuild_from_data(data)
            
            return {
                "success": True,
                "documents_added": documents_added,
                "message": f"Rebuilt knowledge base with {documents_added} documents"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get simple agent statistics"""
        stats = {
            "conversation_length": len(self.conversation_history),
            "last_activity": self.conversation_history[-1].timestamp if self.conversation_history else "Never",
            "status": "Ready"
        }
        
        # Add vector DB stats if available
        if self.vector_db:
            vector_stats = self.vector_db.get_stats()
            stats["vector_db"] = vector_stats
        
        return stats