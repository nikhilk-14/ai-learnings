"""
Context Scorer - Smart relevance scoring for technical accuracy
Focuses on technical information and project-specific details to prevent incorrect responses.
"""
import re
import json
from typing import Dict, List, Any, Tuple, Set
from dataclasses import dataclass


@dataclass
class ContextItem:
    """Represents a piece of context with metadata"""
    content: str
    source: str  # 'skills', 'projects', 'profile', 'activities'
    item_type: str  # 'technical_skill', 'project', 'profile_info', 'activity'
    metadata: Dict[str, Any]
    relevance_score: float = 0.0
    technical_score: float = 0.0
    project_score: float = 0.0


class ContextScorer:
    """
    Smart context scoring system with focus on technical accuracy and project details.
    Prevents information loss that leads to incorrect technical responses.
    """
    
    def __init__(self):
        # Technical terms and their relationships
        self.tech_relationships = {
            # Frontend Technologies
            'angular': ['typescript', 'rxjs', 'ngrx', 'material', 'primeng', 'nodejs'],
            'react': ['javascript', 'typescript', 'jsx', 'redux', 'nodejs'],
            'vue': ['javascript', 'typescript', 'vuex', 'nodejs'],
            'typescript': ['javascript', 'angular', 'react', 'nodejs'],
            'javascript': ['html', 'css', 'nodejs', 'react', 'vue'],
            
            # Backend Technologies
            '.net': ['c#', 'asp.net', 'entity framework', 'sql server', 'azure'],
            '.net core': ['c#', 'asp.net core', 'entity framework', 'sql server', 'azure'],
            'c#': ['.net', '.net core', 'asp.net', 'entity framework', 'sql server'],
            'nodejs': ['javascript', 'typescript', 'express', 'mongodb', 'npm'],
            'python': ['django', 'flask', 'fastapi', 'pandas', 'postgresql'],
            
            # Databases
            'sql server': ['c#', '.net', 'azure', 'ssms', 't-sql'],
            'mongodb': ['nodejs', 'javascript', 'express', 'mongoose'],
            'postgresql': ['python', 'django', 'sql'],
            'cosmosdb': ['azure', '.net', 'nosql', 'mongodb'],
            
            # Cloud Platforms
            'azure': ['.net', 'c#', 'sql server', 'cosmosdb', 'functions', 'app service'],
            'aws': ['lambda', 'ec2', 's3', 'rds', 'dynamodb'],
            'docker': ['containerization', 'kubernetes', 'devops', 'ci/cd'],
            
            # Architectural Patterns
            'microservices': ['api', 'rest', 'docker', 'kubernetes', 'cloud'],
            'rest api': ['http', 'json', 'swagger', 'postman', 'api'],
            'mvc': ['model', 'view', 'controller', 'asp.net', 'architecture'],
        }
        
        # Project-related keywords that indicate important context
        self.project_indicators = {
            'domain', 'role', 'responsibilities', 'technologies', 'skills', 
            'built', 'developed', 'implemented', 'designed', 'created',
            'led', 'managed', 'collaborated', 'delivered', 'deployed'
        }
        
        # Technical skill indicators
        self.technical_indicators = {
            'programming', 'language', 'framework', 'library', 'tool',
            'database', 'cloud', 'platform', 'api', 'service',
            'architecture', 'design', 'pattern', 'methodology'
        }
        
        # Experience level indicators
        self.experience_indicators = {
            'years', 'experience', 'expert', 'proficient', 'skilled',
            'beginner', 'intermediate', 'advanced', 'senior', 'lead'
        }
    
    def score_context_items(self, data: Dict[str, Any], query: str) -> List[ContextItem]:
        """
        Score all context items based on relevance to query with technical focus
        """
        context_items = []
        query_lower = query.lower()
        query_words = set(re.findall(r'\b\w+\b', query_lower))
        
        # Extract technical terms from query
        query_tech_terms = self._extract_technical_terms(query_lower)
        
        # Process user profile
        if data.get('user_profile'):
            items = self._score_profile_items(data['user_profile'], query_words, query_tech_terms)
            context_items.extend(items)
        
        # Process technical skills
        if data.get('technical_skills'):
            items = self._score_skill_items(data['technical_skills'], query_words, query_tech_terms)
            context_items.extend(items)
        
        # Process projects (high priority for project-specific queries)
        if data.get('projects'):
            items = self._score_project_items(data['projects'], query_words, query_tech_terms)
            context_items.extend(items)
        
        # Process activities
        if data.get('other_activities'):
            items = self._score_activity_items(data['other_activities'], query_words, query_tech_terms)
            context_items.extend(items)
        
        # Sort by relevance score (highest first)
        context_items.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return context_items
    
    def _extract_technical_terms(self, text: str) -> Set[str]:
        """Extract technical terms from query text"""
        tech_terms = set()
        
        # Check for exact matches in our tech relationships
        for tech in self.tech_relationships.keys():
            if tech.lower() in text:
                tech_terms.add(tech.lower())
        
        # Check for common technical patterns
        tech_patterns = [
            r'\b\w+\.js\b',  # JavaScript libraries
            r'\b\w+\.net\b',  # .NET variations
            r'\b\w+sql\b',   # SQL variations
            r'\b\w+db\b',    # Database variations
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            tech_terms.update(match.lower() for match in matches)
        
        return tech_terms
    
    def _score_profile_items(self, profile: Dict, query_words: Set[str], tech_terms: Set[str]) -> List[ContextItem]:
        """Score user profile items"""
        items = []
        
        for key, value in profile.items():
            if key in ['attachments', 'urls'] or not value:
                continue
                
            if isinstance(value, str):
                content = f"{key}: {value}"
                score = self._calculate_relevance_score(content, query_words, tech_terms)
                
                # Boost score for profile summary as it contains comprehensive info
                if key == 'profile_summary':
                    score *= 1.5
                
                item = ContextItem(
                    content=content,
                    source='profile',
                    item_type='profile_info',
                    metadata={'key': key},
                    relevance_score=score,
                    technical_score=self._calculate_technical_score(content, tech_terms),
                    project_score=0.0
                )
                items.append(item)
        
        return items
    
    def _score_skill_items(self, skills: Dict, query_words: Set[str], tech_terms: Set[str]) -> List[ContextItem]:
        """Score technical skill items with enhanced technical accuracy"""
        items = []
        
        if isinstance(skills, dict):
            for category, skill_list in skills.items():
                if isinstance(skill_list, list):
                    for skill in skill_list:
                        content = f"Technical Skill ({category}): {skill}"
                        
                        # Calculate base relevance
                        base_score = self._calculate_relevance_score(content, query_words, tech_terms)
                        
                        # Boost score for exact technical matches
                        skill_lower = skill.lower()
                        if skill_lower in tech_terms:
                            base_score *= 2.0
                        
                        # Boost score for related technologies
                        related_boost = self._calculate_related_tech_boost(skill_lower, tech_terms)
                        base_score *= (1.0 + related_boost)
                        
                        item = ContextItem(
                            content=content,
                            source='skills',
                            item_type='technical_skill',
                            metadata={
                                'skill': skill,
                                'category': category,
                                'related_technologies': self.tech_relationships.get(skill_lower, [])
                            },
                            relevance_score=base_score,
                            technical_score=self._calculate_technical_score(content, tech_terms),
                            project_score=0.0
                        )
                        items.append(item)
        
        return items
    
    def _score_project_items(self, projects: List[Dict], query_words: Set[str], tech_terms: Set[str]) -> List[ContextItem]:
        """Score project items with high priority for project-specific queries"""
        items = []
        
        for project in projects:
            project_name = project.get('domain', '') or project.get('name', '')
            description = project.get('description', '')
            technologies = project.get('technologies', []) or project.get('related_skills', [])
            role = project.get('role', '')
            
            # Create comprehensive project content
            content_parts = []
            if project_name:
                content_parts.append(f"Project: {project_name}")
            if role:
                content_parts.append(f"Role: {role}")
            if description:
                content_parts.append(f"Description: {description}")
            if technologies:
                if isinstance(technologies, list):
                    tech_str = ', '.join(technologies)
                else:
                    tech_str = str(technologies)
                content_parts.append(f"Technologies: {tech_str}")
            
            content = " | ".join(content_parts)
            
            # Calculate relevance with project-specific boosting
            base_score = self._calculate_relevance_score(content, query_words, tech_terms)
            
            # Major boost for project-related queries
            project_keywords = {'project', 'built', 'developed', 'worked', 'experience', 'portfolio'}
            if any(word in query_words for word in project_keywords):
                base_score *= 2.5
            
            # Technical technology matching
            if isinstance(technologies, list):
                for tech in technologies:
                    if tech.lower() in tech_terms:
                        base_score *= 1.8
                    elif tech.lower() in query_words:
                        base_score *= 1.5
            
            item = ContextItem(
                content=content,
                source='projects',
                item_type='project',
                metadata={
                    'name': project_name,
                    'technologies': technologies,
                    'role': role
                },
                relevance_score=base_score,
                technical_score=self._calculate_technical_score(content, tech_terms),
                project_score=base_score * 0.8  # Projects always have high project relevance
            )
            items.append(item)
        
        return items
    
    def _score_activity_items(self, activities: List[Dict], query_words: Set[str], tech_terms: Set[str]) -> List[ContextItem]:
        """Score activity items"""
        items = []
        
        for activity in activities:
            name = activity.get('name', '') or activity.get('title', '')
            description = activity.get('description', '')
            
            content = f"Activity: {name} - {description}" if name and description else f"Activity: {name or description}"
            score = self._calculate_relevance_score(content, query_words, tech_terms)
            
            item = ContextItem(
                content=content,
                source='activities',
                item_type='activity',
                metadata={'name': name},
                relevance_score=score,
                technical_score=self._calculate_technical_score(content, tech_terms),
                project_score=0.2  # Activities might have some project relevance
            )
            items.append(item)
        
        return items
    
    def _calculate_relevance_score(self, content: str, query_words: Set[str], tech_terms: Set[str]) -> float:
        """Calculate relevance score for content"""
        content_lower = content.lower()
        content_words = set(re.findall(r'\b\w+\b', content_lower))
        
        # Base word matching score
        word_matches = len(query_words.intersection(content_words))
        total_query_words = len(query_words)
        word_score = (word_matches / total_query_words) if total_query_words > 0 else 0
        
        # Technical term matching bonus
        tech_matches = len(tech_terms.intersection(content_words))
        total_tech_terms = len(tech_terms)
        tech_score = (tech_matches / total_tech_terms) if total_tech_terms > 0 else 0
        
        # Content quality indicators
        quality_boost = 0.0
        if len(content) > 50:  # Longer content might be more informative
            quality_boost += 0.1
        
        # Technical content indicators
        if any(indicator in content_lower for indicator in self.technical_indicators):
            quality_boost += 0.2
        
        # Project content indicators
        if any(indicator in content_lower for indicator in self.project_indicators):
            quality_boost += 0.15
        
        # Experience indicators
        if any(indicator in content_lower for indicator in self.experience_indicators):
            quality_boost += 0.1
        
        # Combine scores
        final_score = (word_score * 0.4) + (tech_score * 0.5) + quality_boost + 0.1
        
        return min(final_score, 1.0)  # Cap at 1.0
    
    def _calculate_technical_score(self, content: str, tech_terms: Set[str]) -> float:
        """Calculate how technical/relevant the content is"""
        content_lower = content.lower()
        
        # Count technical terms
        tech_count = sum(1 for term in tech_terms if term in content_lower)
        
        # Count technical indicators
        tech_indicators_count = sum(1 for indicator in self.technical_indicators if indicator in content_lower)
        
        # Calculate score
        tech_score = (tech_count * 0.3) + (tech_indicators_count * 0.2)
        
        return min(tech_score, 1.0)
    
    def _calculate_related_tech_boost(self, skill: str, tech_terms: Set[str]) -> float:
        """Calculate boost for related technologies"""
        if skill not in self.tech_relationships:
            return 0.0
        
        related_techs = self.tech_relationships[skill]
        related_matches = sum(1 for tech in related_techs if tech in tech_terms)
        
        return related_matches * 0.1  # 10% boost per related technology
    
    def get_top_context_items(self, context_items: List[ContextItem], max_items: int = 8) -> List[ContextItem]:
        """Get top context items with smart selection"""
        if len(context_items) <= max_items:
            return context_items
        
        # Ensure we have diverse sources in top results
        selected_items = []
        source_counts = {}
        
        for item in context_items:
            source = item.source
            
            # Prioritize high-scoring items but maintain source diversity
            if (len(selected_items) < max_items and 
                (source_counts.get(source, 0) < 3 or item.relevance_score > 0.7)):
                
                selected_items.append(item)
                source_counts[source] = source_counts.get(source, 0) + 1
        
        return selected_items
    
    def validate_critical_context(self, context_items: List[ContextItem], query: str) -> Dict[str, Any]:
        """Validate that critical context isn't missing"""
        query_lower = query.lower()
        validation_result = {
            'has_technical_context': False,
            'has_project_context': False,
            'has_experience_context': False,
            'missing_critical_info': [],
            'recommendations': []
        }
        
        # Check for technical context
        if any(item.technical_score > 0.3 for item in context_items):
            validation_result['has_technical_context'] = True
        
        # Check for project context
        if any(item.project_score > 0.3 for item in context_items):
            validation_result['has_project_context'] = True
        
        # Check for experience context
        if any('experience' in item.content.lower() or 'years' in item.content.lower() 
               for item in context_items):
            validation_result['has_experience_context'] = True
        
        # Identify missing critical information
        if 'project' in query_lower and not validation_result['has_project_context']:
            validation_result['missing_critical_info'].append('project_details')
            validation_result['recommendations'].append('Include more project-specific context')
        
        if any(tech in query_lower for tech in self.tech_relationships.keys()) and not validation_result['has_technical_context']:
            validation_result['missing_critical_info'].append('technical_details')
            validation_result['recommendations'].append('Include more technical skill context')
        
        return validation_result