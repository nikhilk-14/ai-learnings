"""
Simple Lightweight Agent - Minimal Agentic AI for v2
Just adds basic planning and memory to existing v1 functionality
Enhanced with context optimization for faster LLM responses
"""
import json
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from core.context_optimizer import ContextOptimizer
from utils.prompt_templates import PromptTemplates
from core.response_cache import ResponseCache
from core.progressive_context import ProgressiveContextBuilder
from core.context_validator import ContextValidator


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
        
        # Initialize optimization components
        self.context_optimizer = ContextOptimizer()  # Legacy optimizer for fallback
        self.prompt_templates = PromptTemplates()
        self.response_cache = ResponseCache()
        
        # Initialize enhanced context system (Phase 2A)
        self.progressive_context_builder = ProgressiveContextBuilder()
        self.context_validator = ContextValidator()
        
        # Stats tracking
        self._last_context_stats = {}
    
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
            # Optimized RAG-based search with reduced results
            try:
                # Primary: Vector search (semantic similarity) - reduced from 5 to 3
                if self.vector_db:
                    vector_results = self.vector_db.search(question, top_k=3)
                    # Use context optimizer to optimize search results
                    optimized_results = self.context_optimizer.optimize_search_results(vector_results, max_results=3)
                    return {"search_results": optimized_results}
                
                # Fallback: Use optimized profile context if no vector search
                data = self.data_loader()
                optimized_context = self.context_optimizer.optimize_profile_context(data, question)
                return {"search_results": [f"Profile context: {json.dumps(optimized_context)}"]}
                
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
        Main method to ask a question with simple agentic behavior and caching
        """
        start_time = time.time()
        
        # Add user question to history
        self._add_to_history("user", question)
        
        try:
            # Step 1: Detect query type for optimization
            query_type = self.prompt_templates.detect_query_type(question)
            
            # Step 2: Check cache first for eligible queries
            data = self.data_loader()
            # Use lightweight context for cache key generation
            quick_context = self.context_optimizer.optimize_profile_context(data, question)
            context_summary = self.response_cache._generate_context_summary(quick_context)
            
            cached_response = self.response_cache.get_cached_response(question, query_type, context_summary)
            if cached_response:
                # Add cached response to history
                self._add_to_history("assistant", cached_response)
                
                execution_time = time.time() - start_time
                return {
                    "success": True,
                    "response": cached_response,
                    "plan": ["cache_hit"],
                    "execution_time": f"{execution_time:.2f}s",
                    "context_used": 0,
                    "cached": True,
                    "context_quality": "cached"
                }
            
            # Step 3: Create simple plan (if not cached)
            plan = self._create_simple_plan(question)
            
            # Step 4: Execute plan steps
            execution_context = {}
            for step in plan:
                step_result = self._execute_step(step, question, execution_context)
                execution_context.update(step_result)
            
            # Step 5: Generate final response using LLM
            response = self._generate_llm_response(question, execution_context)
            
            # Step 6: Cache the response if eligible
            self.response_cache.cache_response(question, query_type, response, context_summary)
            
            # Add response to history
            self._add_to_history("assistant", response)
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "response": response,
                "plan": plan,
                "execution_time": f"{execution_time:.2f}s",
                "context_used": len(execution_context.get("search_results", [])),
                "cached": False,
                "context_quality": self._last_context_stats.get('validation_quality', 0.8),
                "context_level": self._last_context_stats.get('context_level', 'standard'),
                "query_type": self._last_context_stats.get('query_type', 'general')
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
        """Generate enhanced response with progressive context and validation"""
        
        try:
            # Get profile data
            data = self.data_loader()
            
            # Use enhanced progressive context builder
            context_build_result = self.progressive_context_builder.build_context(data, question)
            enhanced_context = context_build_result['context']
            
            # Handle search results if available from vector search
            search_results = context.get("search_results", [])
            if search_results and isinstance(search_results[0], str):
                enhanced_context["search_results"] = search_results
            
            # Validate context quality and fix critical issues
            validation_report = self.context_validator.validate_context(
                enhanced_context, data, question
            )
            
            # Fix critical context issues if needed
            if any(issue.severity == 'critical' for issue in validation_report['issues']):
                enhanced_context = self.context_validator.fix_context_issues(
                    enhanced_context, validation_report, data
                )
            
            # Detect query type for appropriate template
            query_type = self.prompt_templates.detect_query_type(question)
            
            # Get enhanced prompt based on query type and context quality
            if search_results and 'general' in query_type:
                prompt = self.prompt_templates.get_template_for_query_type('search_response', enhanced_context, question)
            else:
                prompt = self.prompt_templates.get_template_for_query_type(query_type, enhanced_context, question)
            
            # Get optimized LLM parameters for this query type
            llm_params = self.prompt_templates.get_llm_parameters_for_type(query_type)
            
            # Adjust parameters based on context quality
            if validation_report['quality_score'] < 0.6:
                # Lower temperature for more conservative responses when context quality is poor
                llm_params['temperature'] *= 0.8
                llm_params['max_tokens'] = min(llm_params['max_tokens'], 150)
            
            # Call LLM with enhanced parameters
            response = self.llm_client.chat.completions.create(
                model=llm_params["model"],
                messages=[{"role": "user", "content": prompt}],
                temperature=llm_params["temperature"],
                max_tokens=llm_params["max_tokens"]
            )
            
            generated_response = response.choices[0].message.content.strip()
            
            # Store context build metadata for debugging/stats
            self._last_context_stats = {
                'context_level': context_build_result['context_level'],
                'items_used': context_build_result['items_used'],
                'validation_quality': validation_report['quality_score'],
                'query_type': query_type
            }
            
            return generated_response
        
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
    
    def clear_cache(self):
        """Clear response cache (useful when profile data changes)"""
        self.response_cache.invalidate_cache()
    
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
        """Get comprehensive agent statistics including optimization metrics"""
        stats = {
            "conversation_length": len(self.conversation_history),
            "last_activity": self.conversation_history[-1].timestamp if self.conversation_history else "Never",
            "status": "Ready"
        }
        
        # Add vector DB stats if available
        if self.vector_db:
            vector_stats = self.vector_db.get_stats()
            stats["vector_db"] = vector_stats
        
        # Add cache stats
        cache_stats = self.response_cache.get_cache_stats()
        stats["cache"] = cache_stats
        
        return stats