"""
Progressive Context Builder - Load context incrementally based on query complexity
Prioritizes technical and project details while maintaining speed.
"""
from typing import Dict, List, Any, Tuple
from core.context_scorer import ContextScorer, ContextItem
from dataclasses import dataclass


@dataclass
class ContextLevel:
    """Represents different levels of context depth"""
    name: str
    max_items: int
    min_score_threshold: float
    include_technical: bool = True
    include_projects: bool = True
    include_profile: bool = True
    include_activities: bool = False


class ProgressiveContextBuilder:
    """
    Builds context progressively based on query complexity and needs.
    Ensures technical accuracy while maintaining performance.
    """
    
    def __init__(self):
        self.context_scorer = ContextScorer()
        
        # Define context levels from minimal to comprehensive
        self.context_levels = {
            'minimal': ContextLevel(
                name='minimal',
                max_items=3,
                min_score_threshold=0.6,
                include_activities=False
            ),
            'standard': ContextLevel(
                name='standard', 
                max_items=6,
                min_score_threshold=0.4,
                include_activities=True
            ),
            'comprehensive': ContextLevel(
                name='comprehensive',
                max_items=10,
                min_score_threshold=0.2,
                include_activities=True
            ),
            'technical_deep': ContextLevel(
                name='technical_deep',
                max_items=8,
                min_score_threshold=0.3,
                include_activities=False  # Focus on technical content
            ),
            'project_focused': ContextLevel(
                name='project_focused',
                max_items=7,
                min_score_threshold=0.3,
                include_activities=False  # Focus on projects
            )
        }
    
    def build_context(self, data: Dict[str, Any], query: str) -> Dict[str, Any]:
        """
        Build context progressively based on query analysis
        
        Returns:
            Dict with optimized context and metadata about the build process
        """
        # Step 1: Analyze query to determine context requirements
        context_requirements = self._analyze_query_requirements(query)
        
        # Step 2: Score all available context items
        all_context_items = self.context_scorer.score_context_items(data, query)
        
        # Step 3: Select appropriate context level
        context_level = self._select_context_level(context_requirements, all_context_items)
        
        # Step 4: Build progressive context
        selected_items = self._select_context_items(all_context_items, context_level, context_requirements)
        
        # Step 5: Validate critical context isn't missing
        validation_result = self.context_scorer.validate_critical_context(selected_items, query)
        
        # Step 6: Adjust context if critical information is missing
        if validation_result['missing_critical_info']:
            selected_items = self._add_missing_critical_context(
                all_context_items, selected_items, validation_result, context_level
            )
        
        # Step 7: Format final context
        formatted_context = self._format_context(selected_items, context_requirements)
        
        return {
            'context': formatted_context,
            'context_level': context_level.name,
            'items_used': len(selected_items),
            'validation_result': validation_result,
            'requirements': context_requirements,
            'build_metadata': {
                'total_items_available': len(all_context_items),
                'avg_relevance_score': sum(item.relevance_score for item in selected_items) / len(selected_items) if selected_items else 0,
                'technical_items': sum(1 for item in selected_items if item.technical_score > 0.3),
                'project_items': sum(1 for item in selected_items if item.project_score > 0.3)
            }
        }
    
    def _analyze_query_requirements(self, query: str) -> Dict[str, Any]:
        """Analyze query to understand context requirements"""
        query_lower = query.lower()
        
        requirements = {
            'complexity_level': 'standard',  # minimal, standard, comprehensive
            'needs_technical_detail': False,
            'needs_project_detail': False,
            'needs_experience_detail': False,
            'specific_technologies': [],
            'specific_projects': [],
            'query_type': 'general',
            'expected_response_length': 'medium'  # short, medium, long
        }
        
        # Detect complexity level
        complex_indicators = [
            'analyze', 'compare', 'evaluate', 'assessment', 'detailed',
            'comprehensive', 'in-depth', 'breakdown', 'explain how'
        ]
        
        simple_indicators = [
            'what', 'which', 'do i have', 'list', 'show me', 'quick'
        ]
        
        if any(indicator in query_lower for indicator in complex_indicators):
            requirements['complexity_level'] = 'comprehensive'
            requirements['expected_response_length'] = 'long'
        elif any(indicator in query_lower for indicator in simple_indicators):
            requirements['complexity_level'] = 'minimal'
            requirements['expected_response_length'] = 'short'
        
        # Detect technical detail needs
        tech_keywords = [
            'technology', 'tech', 'skill', 'programming', 'language',
            'framework', 'library', 'tool', 'platform', 'stack'
        ]
        
        if any(keyword in query_lower for keyword in tech_keywords):
            requirements['needs_technical_detail'] = True
            requirements['complexity_level'] = 'technical_deep'
        
        # Detect project detail needs
        project_keywords = [
            'project', 'built', 'developed', 'worked on', 'portfolio',
            'experience with', 'used in'
        ]
        
        if any(keyword in query_lower for keyword in project_keywords):
            requirements['needs_project_detail'] = True
            if requirements['complexity_level'] == 'standard':
                requirements['complexity_level'] = 'project_focused'
        
        # Detect experience level needs
        experience_keywords = [
            'experience', 'years', 'how long', 'proficiency', 'level',
            'expert', 'beginner', 'advanced'
        ]
        
        if any(keyword in query_lower for keyword in experience_keywords):
            requirements['needs_experience_detail'] = True
        
        # Extract specific technologies mentioned
        for tech in self.context_scorer.tech_relationships.keys():
            if tech in query_lower:
                requirements['specific_technologies'].append(tech)
        
        # Determine query type for better context selection
        if any(word in query_lower for word in ['analyze', 'assessment', 'strengths', 'weaknesses']):
            requirements['query_type'] = 'analysis'
        elif any(word in query_lower for word in ['suggest', 'recommend', 'advice', 'should']):
            requirements['query_type'] = 'recommendation'
        elif any(word in query_lower for word in ['what', 'which', 'list', 'show']):
            requirements['query_type'] = 'factual'
        elif any(word in query_lower for word in ['how', 'explain', 'describe']):
            requirements['query_type'] = 'explanatory'
        
        return requirements
    
    def _select_context_level(self, requirements: Dict[str, Any], context_items: List[ContextItem]) -> ContextLevel:
        """Select appropriate context level based on requirements"""
        complexity = requirements['complexity_level']
        
        # Override complexity based on available relevant context
        high_relevance_items = [item for item in context_items if item.relevance_score > 0.7]
        
        if len(high_relevance_items) < 2 and complexity == 'comprehensive':
            # Not enough high-quality context, reduce to standard
            complexity = 'standard'
        elif len(high_relevance_items) > 8 and complexity == 'minimal':
            # Lots of relevant context available, upgrade to standard
            complexity = 'standard'
        
        return self.context_levels.get(complexity, self.context_levels['standard'])
    
    def _select_context_items(self, all_items: List[ContextItem], level: ContextLevel, 
                             requirements: Dict[str, Any]) -> List[ContextItem]:
        """Select context items based on level and requirements"""
        
        # Filter items by score threshold
        filtered_items = [
            item for item in all_items 
            if item.relevance_score >= level.min_score_threshold
        ]
        
        # Apply source filters based on level
        if not level.include_activities:
            filtered_items = [item for item in filtered_items if item.source != 'activities']
        
        # Prioritize items based on requirements
        prioritized_items = []
        
        # First priority: Items that match specific requirements
        if requirements['needs_technical_detail']:
            tech_items = [item for item in filtered_items if item.technical_score > 0.3]
            prioritized_items.extend(tech_items[:level.max_items // 2])
        
        if requirements['needs_project_detail']:
            project_items = [item for item in filtered_items if item.project_score > 0.3]
            prioritized_items.extend(project_items[:level.max_items // 2])
        
        # Remove duplicates while preserving order
        seen_content = set()
        unique_prioritized = []
        for item in prioritized_items:
            if item.content not in seen_content:
                unique_prioritized.append(item)
                seen_content.add(item.content)
        
        # Fill remaining slots with highest scoring items
        remaining_slots = level.max_items - len(unique_prioritized)
        if remaining_slots > 0:
            for item in filtered_items:
                if item.content not in seen_content and len(unique_prioritized) < level.max_items:
                    unique_prioritized.append(item)
                    seen_content.add(item.content)
        
        return unique_prioritized[:level.max_items]
    
    def _add_missing_critical_context(self, all_items: List[ContextItem], 
                                     selected_items: List[ContextItem],
                                     validation_result: Dict[str, Any],
                                     level: ContextLevel) -> List[ContextItem]:
        """Add missing critical context to ensure accuracy"""
        
        missing_info = validation_result['missing_critical_info']
        current_content = {item.content for item in selected_items}
        
        additional_items = []
        
        # Add missing technical details
        if 'technical_details' in missing_info:
            tech_items = [
                item for item in all_items
                if item.technical_score > 0.2 and item.content not in current_content
            ]
            additional_items.extend(tech_items[:2])  # Add top 2 technical items
        
        # Add missing project details
        if 'project_details' in missing_info:
            project_items = [
                item for item in all_items
                if item.project_score > 0.2 and item.content not in current_content
            ]
            additional_items.extend(project_items[:2])  # Add top 2 project items
        
        # Combine with selected items, respecting max limit
        combined_items = selected_items + additional_items
        max_items = min(level.max_items + 2, 12)  # Allow slight overflow for critical context
        
        return combined_items[:max_items]
    
    def _format_context(self, context_items: List[ContextItem], requirements: Dict[str, Any]) -> Dict[str, str]:
        """Format context items into structured context dictionary"""
        
        formatted_context = {}
        
        # Group items by source for better organization
        items_by_source = {}
        for item in context_items:
            if item.source not in items_by_source:
                items_by_source[item.source] = []
            items_by_source[item.source].append(item)
        
        # Format each source section
        if 'profile' in items_by_source:
            profile_items = items_by_source['profile']
            profile_content = []
            for item in profile_items:
                # Extract just the value part for cleaner context
                content = item.content
                if ': ' in content:
                    key, value = content.split(': ', 1)
                    if key.lower() == 'profile_summary':
                        profile_content.append(f"Background: {value}")
                    else:
                        profile_content.append(f"{key}: {value}")
                else:
                    profile_content.append(content)
            
            formatted_context['profile'] = ' | '.join(profile_content)
        
        if 'skills' in items_by_source:
            skill_items = items_by_source['skills']
            skills_by_category = {}
            
            for item in skill_items:
                category = item.metadata.get('category', 'General')
                skill = item.metadata.get('skill', '')
                
                if category not in skills_by_category:
                    skills_by_category[category] = []
                if skill:
                    skills_by_category[category].append(skill)
            
            skill_parts = []
            for category, skills in skills_by_category.items():
                if skills:
                    skill_parts.append(f"{category}: {', '.join(skills)}")
            
            formatted_context['skills'] = ' | '.join(skill_parts)
        
        if 'projects' in items_by_source:
            project_items = items_by_source['projects']
            project_parts = []
            
            for item in project_items:
                # Extract structured project info
                content = item.content
                if 'Project:' in content:
                    project_parts.append(content.replace(' | ', ' - '))
                else:
                    project_parts.append(content)
            
            formatted_context['projects'] = ' | '.join(project_parts)
        
        if 'activities' in items_by_source and items_by_source['activities']:
            activity_items = items_by_source['activities']
            activity_parts = [item.content for item in activity_items]
            formatted_context['activities'] = ' | '.join(activity_parts)
        
        return formatted_context
    
    def get_context_stats(self, build_result: Dict[str, Any]) -> Dict[str, Any]:
        """Get statistics about the context building process"""
        
        metadata = build_result.get('build_metadata', {})
        validation = build_result.get('validation_result', {})
        
        return {
            'context_level_used': build_result.get('context_level', 'unknown'),
            'total_items_used': build_result.get('items_used', 0),
            'total_items_available': metadata.get('total_items_available', 0),
            'average_relevance_score': round(metadata.get('avg_relevance_score', 0), 3),
            'technical_items_included': metadata.get('technical_items', 0),
            'project_items_included': metadata.get('project_items', 0),
            'has_technical_context': validation.get('has_technical_context', False),
            'has_project_context': validation.get('has_project_context', False),
            'missing_critical_info': validation.get('missing_critical_info', []),
            'quality_score': self._calculate_quality_score(build_result)
        }
    
    def _calculate_quality_score(self, build_result: Dict[str, Any]) -> float:
        """Calculate overall quality score for the built context"""
        metadata = build_result.get('build_metadata', {})
        validation = build_result.get('validation_result', {})
        
        # Base score from average relevance
        base_score = metadata.get('avg_relevance_score', 0) * 0.4
        
        # Bonus for having required context types
        context_bonus = 0
        if validation.get('has_technical_context', False):
            context_bonus += 0.2
        if validation.get('has_project_context', False):
            context_bonus += 0.2
        
        # Penalty for missing critical info
        missing_penalty = len(validation.get('missing_critical_info', [])) * 0.1
        
        # Bonus for good item distribution
        tech_items = metadata.get('technical_items', 0)
        project_items = metadata.get('project_items', 0)
        total_items = build_result.get('items_used', 1)
        
        distribution_bonus = 0
        if tech_items > 0 and project_items > 0:
            distribution_bonus = 0.1
        
        final_score = base_score + context_bonus - missing_penalty + distribution_bonus + 0.1
        
        return min(max(final_score, 0.0), 1.0)  # Clamp between 0 and 1