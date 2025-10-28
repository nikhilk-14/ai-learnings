"""
Optimized Prompt Templates for Local LLM (meta-llama-3.1-8b-instruct)
Designed for speed and efficiency with shorter, more direct prompts.
"""
from typing import Dict, Any


class PromptTemplates:
    """
    Optimized prompt templates for different query types.
    Focus: Speed, simplicity, and structured responses for local LLM.
    """
    
    @staticmethod
    def profile_analysis(context: Dict[str, str]) -> str:
        """Technical-aware profile analysis prompt"""
        profile_info = context.get('profile', 'N/A')
        skills_info = context.get('skills', 'N/A')
        projects_info = context.get('projects', '')
        
        # Build enhanced context with technical focus
        enhanced_context = f"Profile: {profile_info}\nSkills: {skills_info}"
        if projects_info:
            enhanced_context += f"\nKey Projects: {projects_info}"
        
        return f"""{enhanced_context}

Task: Analyze technical strengths and professional positioning. Focus on:
1. Core technical expertise areas
2. Technology stack proficiency  
3. Professional experience level
Be specific about technologies and provide actionable insights."""
    
    @staticmethod
    def career_suggestions(context: Dict[str, str]) -> str:
        """Career suggestions prompt - fast and focused"""
        return f"""Current: {context.get('profile', 'N/A')}
Skills: {context.get('skills', 'N/A')}

Task: Suggest 3 career paths. Format: "1. Role - why it fits". Keep brief."""
    
    @staticmethod
    def project_ideas(context: Dict[str, str]) -> str:
        """Technical project ideas prompt with domain knowledge"""
        skills_info = context.get('skills', 'N/A')
        projects_info = context.get('projects', 'N/A')
        
        return f"""Current Skills: {skills_info}
Existing Projects: {projects_info}

Task: Suggest 2 technically relevant project ideas that:
1. Build upon existing skills and experience
2. Include specific technology stack recommendations
3. Provide clear learning/portfolio value

Format: "Project Name - Technologies: [specific stack] - Purpose: [career benefit]"
Focus on realistic, implementable projects using complementary technologies."""
    
    @staticmethod
    def skill_analysis(context: Dict[str, str]) -> str:
        """Skill analysis prompt - fast gap analysis"""
        return f"""Skills: {context.get('skills', 'N/A')}

Task: Identify 1 key strength and 1 skill gap. Format: "Strength: X. Gap: Y. Learn: Z". 2 sentences max."""
    
    @staticmethod
    def general_question(context: Dict[str, str], question: str) -> str:
        """Technical-aware general question prompt"""
        relevant_info = []
        question_lower = question.lower()
        
        # Enhanced keyword matching with technical focus
        if any(word in question_lower for word in ['skill', 'technology', 'tech', 'programming', 'language', 'framework', 'tool']):
            if context.get('skills'):
                relevant_info.append(f"Technical Skills: {context['skills']}")
            if context.get('projects'):
                relevant_info.append(f"Project Experience: {context['projects']}")
        
        elif any(word in question_lower for word in ['project', 'work', 'experience', 'built', 'developed', 'portfolio']):
            if context.get('projects'):
                relevant_info.append(f"Projects: {context['projects']}")
            if context.get('skills'):
                relevant_info.append(f"Related Skills: {context['skills']}")
        
        elif any(word in question_lower for word in ['profile', 'background', 'about', 'who', 'role', 'experience']):
            if context.get('profile'):
                relevant_info.append(f"Profile: {context['profile']}")
            if context.get('skills'):
                relevant_info.append(f"Key Skills: {context['skills']}")
        
        elif any(word in question_lower for word in ['activity', 'other', 'additional', 'hobby']):
            if context.get('activities'):
                relevant_info.append(f"Activities: {context['activities']}")
        
        # Default fallback with comprehensive context
        if not relevant_info:
            if context.get('profile'):
                relevant_info.append(f"Profile: {context['profile']}")
            if context.get('skills'):
                relevant_info.append(f"Skills: {context['skills']}")
        
        context_str = " | ".join(relevant_info) if relevant_info else "No relevant information available."
        
        return f"""{context_str}

Question: {question}

Task: Provide accurate, specific answer based on the profile information above. 
Be precise about technical details and avoid generalizations. If information is not available, state so clearly."""
    
    @staticmethod
    def search_response(search_results: list, question: str) -> str:
        """Enhanced search-based response with technical accuracy focus"""
        if not search_results:
            return f"""Question: {question}

No specific information found in your profile. 

Task: Respond: "I don't have specific information about that in your profile. Could you provide more context or rephrase your question?" """
        
        results_str = " | ".join(search_results)
        
        return f"""Relevant Profile Information: {results_str}

Question: {question}

Task: Answer using ONLY the specific information provided above. 
- Be factual and precise about technical details
- Don't make assumptions beyond what's stated
- If the information doesn't fully answer the question, say so
- Cite specific technologies, projects, or experience mentioned
- Keep response focused and accurate"""
    
    @staticmethod
    def get_template_for_query_type(query_type: str, context: Dict[str, str], question: str = "") -> str:
        """
        Get appropriate template based on query type
        
        Args:
            query_type: One of 'profile_analysis', 'career_suggestions', 'project_ideas', 
                       'skill_analysis', 'general_question', 'search_response'
            context: Optimized context dictionary
            question: Original question (for general_question type)
        """
        templates = {
            'profile_analysis': PromptTemplates.profile_analysis,
            'career_suggestions': PromptTemplates.career_suggestions,
            'project_ideas': PromptTemplates.project_ideas,
            'skill_analysis': PromptTemplates.skill_analysis,
            'general_question': PromptTemplates.general_question,
            'search_response': PromptTemplates.search_response,
            'technical_question': PromptTemplates.technical_question,
            'project_specific_question': PromptTemplates.project_specific_question
        }
        
        template_func = templates.get(query_type, PromptTemplates.general_question)
        
        if query_type in ['general_question', 'technical_question', 'project_specific_question']:
            return template_func(context, question)
        elif query_type == 'search_response':
            return template_func(context.get('search_results', []), question)
        else:
            return template_func(context)
    
    @staticmethod
    def detect_query_type(question: str) -> str:
        """
        Enhanced query type detection with technical and project focus
        """
        question_lower = question.lower()
        
        # Technical question keywords (high priority for accuracy)
        if any(word in question_lower for word in [
            'what programming', 'what language', 'what framework', 'what technology',
            'which tech', 'do i know', 'experience with', 'familiar with',
            'what skills', 'proficient in', 'worked with'
        ]):
            return 'technical_question'
        
        # Project-specific question keywords (high priority for accuracy)
        if any(word in question_lower for word in [
            'what project', 'which project', 'project where', 'project that',
            'built using', 'developed with', 'worked on project', 'project experience'
        ]):
            return 'project_specific_question'
        
        # Profile analysis keywords
        if any(word in question_lower for word in [
            'analyze', 'analysis', 'strengths', 'weakness', 'assess', 'evaluate', 'profile'
        ]):
            return 'profile_analysis'
        
        # Career suggestions keywords
        if any(word in question_lower for word in [
            'career', 'job', 'role', 'position', 'opportunity', 'suggest', 'recommend', 'next step'
        ]):
            return 'career_suggestions'
        
        # Project ideas keywords (different from project-specific questions)
        if any(word in question_lower for word in [
            'project idea', 'build next', 'create project', 'develop something', 'portfolio project'
        ]):
            return 'project_ideas'
        
        # Skill analysis keywords
        if any(word in question_lower for word in [
            'skill gap', 'skills missing', 'learn next', 'improve skills', 'skill analysis'
        ]):
            return 'skill_analysis'
        
        # Default to general question
        return 'general_question'
    
    @staticmethod
    def technical_question(context: Dict[str, str], question: str) -> str:
        """Specialized prompt for technical questions requiring accuracy"""
        skills_info = context.get('skills', 'N/A')
        projects_info = context.get('projects', '')
        profile_info = context.get('profile', '')
        
        # Build technical context
        tech_context = f"Technical Skills: {skills_info}"
        if projects_info:
            tech_context += f"\nProject Experience: {projects_info}"
        if 'experience' in profile_info.lower() or 'years' in profile_info.lower():
            tech_context += f"\nExperience Context: {profile_info}"
        
        return f"""{tech_context}

Technical Question: {question}

Task: Provide technically accurate answer based on the specific skills and experience above.
- Reference exact technologies mentioned
- Be precise about experience levels and project context
- If specific technical information isn't available, state clearly
- Avoid technical assumptions not supported by the profile"""
    
    @staticmethod
    def project_specific_question(context: Dict[str, str], question: str) -> str:
        """Specialized prompt for project-specific questions"""
        projects_info = context.get('projects', 'N/A')
        skills_info = context.get('skills', '')
        
        project_context = f"Project Details: {projects_info}"
        if skills_info:
            project_context += f"\nRelevant Skills: {skills_info}"
        
        return f"""{project_context}

Project Question: {question}

Task: Answer based on specific project information above.
- Reference actual project names, roles, and technologies
- Be specific about contributions and responsibilities
- Connect project experience to relevant skills
- If project details are limited, acknowledge this"""

    @staticmethod
    def get_llm_parameters_for_type(query_type: str) -> Dict[str, Any]:
        """
        Get optimized LLM parameters based on query type with accuracy focus
        """
        base_params = {
            "temperature": 0.5,  # Lower default for better accuracy
            "max_tokens": 200,   # Increased slightly for better technical detail
            "model": "lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF"
        }
        
        # Adjust parameters based on query type
        type_adjustments = {
            'profile_analysis': {"temperature": 0.4, "max_tokens": 250},  # More detail for analysis
            'career_suggestions': {"temperature": 0.6, "max_tokens": 220},
            'project_ideas': {"temperature": 0.7, "max_tokens": 250},
            'skill_analysis': {"temperature": 0.3, "max_tokens": 180},  # Very precise for skills
            'general_question': {"temperature": 0.5, "max_tokens": 200},
            'search_response': {"temperature": 0.2, "max_tokens": 150},  # Most precise
            'technical_question': {"temperature": 0.3, "max_tokens": 200},  # High accuracy
            'project_specific_question': {"temperature": 0.4, "max_tokens": 220}
        }
        
        adjustments = type_adjustments.get(query_type, {})
        base_params.update(adjustments)
        
        return base_params