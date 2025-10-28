"""
Context Validator - Ensure critical technical information isn't lost
Validates context quality and prevents technical inaccuracies.
"""
from typing import Dict, List, Any, Set, Tuple
import re
from dataclasses import dataclass


@dataclass
class ValidationIssue:
    """Represents a context validation issue"""
    severity: str  # 'critical', 'warning', 'info'
    category: str  # 'technical_accuracy', 'missing_context', 'consistency'
    message: str
    suggestion: str


class ContextValidator:
    """
    Validates context to ensure technical accuracy and completeness.
    Prevents information loss that could lead to incorrect responses.
    """
    
    def __init__(self):
        # Critical technical relationships that must be preserved
        self.critical_tech_pairs = {
            ('angular', 'typescript'): 'Angular projects typically use TypeScript',
            ('.net', 'c#'): '.NET development uses C# programming language',
            ('react', 'javascript'): 'React development uses JavaScript/TypeScript',
            ('sql server', '.net'): 'SQL Server commonly used with .NET applications',
            ('azure', '.net'): 'Azure cloud platform integrates well with .NET',
            ('mongodb', 'nodejs'): 'MongoDB commonly used with Node.js applications',
            ('docker', 'containerization'): 'Docker is a containerization technology'
        }
        
        # Technical terms that should not be isolated from their context
        self.context_dependent_terms = {
            'api': ['rest', 'graphql', 'soap', 'microservices'],
            'database': ['sql', 'nosql', 'mongodb', 'sql server', 'postgresql'],
            'cloud': ['azure', 'aws', 'gcp', 'saas', 'paas', 'iaas'],
            'frontend': ['angular', 'react', 'vue', 'javascript', 'typescript'],
            'backend': ['.net', 'nodejs', 'python', 'java', 'spring'],
            'devops': ['docker', 'kubernetes', 'ci/cd', 'azure devops', 'jenkins']
        }
        
        # Experience indicators that should be preserved with technical skills
        self.experience_indicators = [
            r'\d+\s*\+?\s*years?',
            r'expert',
            r'proficient',
            r'experienced',
            r'skilled',
            r'advanced',
            r'intermediate',
            r'beginner',
            r'senior',
            r'lead',
            r'architect'
        ]
        
        # Project role indicators that provide important context
        self.role_indicators = [
            'led', 'managed', 'designed', 'architected', 'developed',
            'implemented', 'created', 'built', 'delivered', 'deployed',
            'maintained', 'optimized', 'integrated', 'collaborated'
        ]
    
    def validate_context(self, formatted_context: Dict[str, str], 
                        original_data: Dict[str, Any], 
                        query: str) -> Dict[str, Any]:
        """
        Comprehensive context validation
        
        Returns validation report with issues and suggestions
        """
        validation_report = {
            'overall_quality': 'good',  # 'excellent', 'good', 'fair', 'poor'
            'quality_score': 0.8,
            'issues': [],
            'suggestions': [],
            'technical_accuracy_score': 0.8,
            'completeness_score': 0.8,
            'consistency_score': 0.8
        }
        
        # Run all validation checks
        tech_issues = self._validate_technical_accuracy(formatted_context, original_data, query)
        completeness_issues = self._validate_completeness(formatted_context, original_data, query)
        consistency_issues = self._validate_consistency(formatted_context)
        experience_issues = self._validate_experience_context(formatted_context, original_data, query)
        project_issues = self._validate_project_context(formatted_context, original_data, query)
        
        # Combine all issues
        all_issues = tech_issues + completeness_issues + consistency_issues + experience_issues + project_issues
        validation_report['issues'] = all_issues
        
        # Calculate scores
        validation_report['technical_accuracy_score'] = self._calculate_technical_score(tech_issues)
        validation_report['completeness_score'] = self._calculate_completeness_score(completeness_issues)
        validation_report['consistency_score'] = self._calculate_consistency_score(consistency_issues)
        
        # Calculate overall quality
        avg_score = (
            validation_report['technical_accuracy_score'] + 
            validation_report['completeness_score'] + 
            validation_report['consistency_score']
        ) / 3
        
        validation_report['quality_score'] = avg_score
        validation_report['overall_quality'] = self._determine_quality_level(avg_score)
        
        # Generate suggestions
        validation_report['suggestions'] = self._generate_suggestions(all_issues, formatted_context, query)
        
        return validation_report
    
    def _validate_technical_accuracy(self, context: Dict[str, str], 
                                   original_data: Dict[str, Any], 
                                   query: str) -> List[ValidationIssue]:
        """Validate technical accuracy and relationships"""
        issues = []
        query_lower = query.lower()
        
        # Check for broken technical relationships
        for (tech1, tech2), relationship_desc in self.critical_tech_pairs.items():
            if tech1 in query_lower or tech2 in query_lower:
                context_text = ' '.join(context.values()).lower()
                
                # If one tech is mentioned in query, related tech should be in context
                if tech1 in query_lower and tech1 in context_text:
                    if tech2 not in context_text:
                        issues.append(ValidationIssue(
                            severity='warning',
                            category='technical_accuracy',
                            message=f"Query mentions {tech1} but related {tech2} context is missing",
                            suggestion=f"Include {tech2} context because {relationship_desc}"
                        ))
        
        # Check for isolated technical terms
        skills_context = context.get('skills', '')
        for parent_term, related_terms in self.context_dependent_terms.items():
            if parent_term in query_lower:
                context_text = skills_context.lower()
                if parent_term in context_text:
                    related_found = any(term in context_text for term in related_terms)
                    if not related_found:
                        issues.append(ValidationIssue(
                            severity='info',
                            category='technical_accuracy',
                            message=f"{parent_term.title()} mentioned without specific technologies",
                            suggestion=f"Include specific {parent_term} technologies: {', '.join(related_terms[:3])}"
                        ))
        
        return issues
    
    def _validate_completeness(self, context: Dict[str, str], 
                             original_data: Dict[str, Any], 
                             query: str) -> List[ValidationIssue]:
        """Validate context completeness"""
        issues = []
        query_lower = query.lower()
        
        # Check if query asks for specific information that might be missing
        if 'project' in query_lower:
            if 'projects' not in context or not context['projects'].strip():
                issues.append(ValidationIssue(
                    severity='critical',
                    category='missing_context',
                    message="Query asks about projects but no project context provided",
                    suggestion="Include relevant project information"
                ))
        
        if any(word in query_lower for word in ['skill', 'technology', 'tech']):
            if 'skills' not in context or not context['skills'].strip():
                issues.append(ValidationIssue(
                    severity='critical',
                    category='missing_context',
                    message="Query asks about skills but no skills context provided",
                    suggestion="Include relevant technical skills information"
                ))
        
        if any(word in query_lower for word in ['experience', 'background', 'profile']):
            if 'profile' not in context or not context['profile'].strip():
                issues.append(ValidationIssue(
                    severity='warning',
                    category='missing_context',
                    message="Query asks about experience but limited profile context provided",
                    suggestion="Include more comprehensive profile information"
                ))
        
        # Check for very sparse context
        total_context_length = sum(len(text) for text in context.values())
        if total_context_length < 100:
            issues.append(ValidationIssue(
                severity='warning',
                category='missing_context',
                message="Context seems too brief for accurate response",
                suggestion="Include more detailed context information"
            ))
        
        return issues
    
    def _validate_consistency(self, context: Dict[str, str]) -> List[ValidationIssue]:
        """Validate internal consistency of context"""
        issues = []
        
        # Check for contradictory information
        # This is a simplified check - could be expanded with more sophisticated logic
        
        # Check if skills mentioned in projects are also in skills section
        if 'projects' in context and 'skills' in context:
            projects_text = context['projects'].lower()
            skills_text = context['skills'].lower()
            
            # Extract potential technology mentions from projects
            project_techs = re.findall(r'\b(?:angular|react|vue|\.net|c#|javascript|typescript|python|java|sql|mongodb|azure|aws)\b', projects_text)
            
            missing_in_skills = []
            for tech in set(project_techs):
                if tech not in skills_text:
                    missing_in_skills.append(tech)
            
            if missing_in_skills and len(missing_in_skills) <= 3:  # Only flag if reasonable number
                issues.append(ValidationIssue(
                    severity='info',
                    category='consistency',
                    message=f"Technologies mentioned in projects but not in skills: {', '.join(missing_in_skills)}",
                    suggestion="Ensure project technologies are reflected in skills section"
                ))
        
        return issues
    
    def _validate_experience_context(self, context: Dict[str, str], 
                                   original_data: Dict[str, Any], 
                                   query: str) -> List[ValidationIssue]:
        """Validate experience-related context"""
        issues = []
        query_lower = query.lower()
        
        # If query asks about experience levels, check if that info is preserved
        if any(word in query_lower for word in ['experience', 'years', 'how long', 'level']):
            context_text = ' '.join(context.values())
            
            # Check if experience indicators are present
            experience_found = any(
                re.search(pattern, context_text, re.IGNORECASE) 
                for pattern in self.experience_indicators
            )
            
            if not experience_found:
                issues.append(ValidationIssue(
                    severity='warning',
                    category='missing_context',
                    message="Query asks about experience but no experience indicators found in context",
                    suggestion="Include experience levels or years of experience"
                ))
        
        return issues
    
    def _validate_project_context(self, context: Dict[str, str], 
                                original_data: Dict[str, Any], 
                                query: str) -> List[ValidationIssue]:
        """Validate project-specific context"""
        issues = []
        query_lower = query.lower()
        
        # If query asks about specific project aspects, validate they're included
        if 'projects' in context:
            projects_text = context['projects']
            
            # Check for role information if query asks about roles/responsibilities
            if any(word in query_lower for word in ['role', 'responsibility', 'did', 'led', 'managed']):
                role_found = any(
                    role_indicator in projects_text.lower()
                    for role_indicator in self.role_indicators
                )
                
                if not role_found:
                    issues.append(ValidationIssue(
                        severity='info',
                        category='missing_context',
                        message="Query asks about roles but project context lacks role information",
                        suggestion="Include specific roles and responsibilities in project context"
                    ))
            
            # Check for technology stack if query asks about technical aspects
            if any(word in query_lower for word in ['technology', 'tech', 'stack', 'used', 'built with']):
                # Check if technologies are mentioned in project context
                tech_keywords = ['technologies:', 'tech:', 'built with', 'using', 'stack:']
                tech_mentioned = any(keyword in projects_text.lower() for keyword in tech_keywords)
                
                if not tech_mentioned:
                    issues.append(ValidationIssue(
                        severity='info',
                        category='missing_context',
                        message="Query asks about technologies but project context lacks technical details",
                        suggestion="Include technology stack and tools used in projects"
                    ))
        
        return issues
    
    def _calculate_technical_score(self, tech_issues: List[ValidationIssue]) -> float:
        """Calculate technical accuracy score"""
        if not tech_issues:
            return 1.0
        
        score = 1.0
        for issue in tech_issues:
            if issue.severity == 'critical':
                score -= 0.3
            elif issue.severity == 'warning':
                score -= 0.2
            elif issue.severity == 'info':
                score -= 0.1
        
        return max(score, 0.0)
    
    def _calculate_completeness_score(self, completeness_issues: List[ValidationIssue]) -> float:
        """Calculate completeness score"""
        if not completeness_issues:
            return 1.0
        
        score = 1.0
        for issue in completeness_issues:
            if issue.severity == 'critical':
                score -= 0.4
            elif issue.severity == 'warning':
                score -= 0.2
            elif issue.severity == 'info':
                score -= 0.1
        
        return max(score, 0.0)
    
    def _calculate_consistency_score(self, consistency_issues: List[ValidationIssue]) -> float:
        """Calculate consistency score"""
        if not consistency_issues:
            return 1.0
        
        score = 1.0
        for issue in consistency_issues:
            if issue.severity == 'critical':
                score -= 0.3
            elif issue.severity == 'warning':
                score -= 0.2
            elif issue.severity == 'info':
                score -= 0.1
        
        return max(score, 0.0)
    
    def _determine_quality_level(self, score: float) -> str:
        """Determine overall quality level from score"""
        if score >= 0.9:
            return 'excellent'
        elif score >= 0.7:
            return 'good'
        elif score >= 0.5:
            return 'fair'
        else:
            return 'poor'
    
    def _generate_suggestions(self, issues: List[ValidationIssue], 
                            context: Dict[str, str], 
                            query: str) -> List[str]:
        """Generate actionable suggestions based on validation issues"""
        suggestions = []
        
        # Extract unique suggestions from issues
        issue_suggestions = {issue.suggestion for issue in issues if issue.suggestion}
        suggestions.extend(list(issue_suggestions))
        
        # Add general suggestions based on context analysis
        context_text = ' '.join(context.values()).lower()
        query_lower = query.lower()
        
        # Suggest more technical detail if query is technical but context is sparse
        tech_terms = ['programming', 'language', 'framework', 'technology', 'skill']
        if any(term in query_lower for term in tech_terms) and len(context_text) < 200:
            suggestions.append("Consider including more detailed technical information")
        
        # Suggest project details if project query but sparse project context
        if 'project' in query_lower and 'projects' in context and len(context['projects']) < 100:
            suggestions.append("Include more comprehensive project details including role and technologies")
        
        return suggestions[:5]  # Limit to top 5 suggestions
    
    def fix_context_issues(self, context: Dict[str, str], 
                          validation_report: Dict[str, Any], 
                          original_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Attempt to fix critical context issues by adding missing information
        
        Returns improved context dictionary
        """
        fixed_context = context.copy()
        
        critical_issues = [
            issue for issue in validation_report['issues'] 
            if issue.severity == 'critical'
        ]
        
        for issue in critical_issues:
            if issue.category == 'missing_context':
                # Try to add missing context from original data
                if 'project' in issue.message.lower() and original_data.get('projects'):
                    # Add basic project info
                    if 'projects' not in fixed_context or not fixed_context['projects']:
                        project = original_data['projects'][0]  # Take first project
                        project_name = project.get('domain', '') or project.get('name', '')
                        technologies = project.get('technologies', []) or project.get('related_skills', [])
                        
                        if isinstance(technologies, list):
                            tech_str = ', '.join(technologies[:3])  # Limit to first 3
                        else:
                            tech_str = str(technologies)
                        
                        fixed_context['projects'] = f"Project: {project_name} - Technologies: {tech_str}"
                
                elif 'skill' in issue.message.lower() and original_data.get('technical_skills'):
                    # Add basic skills info
                    if 'skills' not in fixed_context or not fixed_context['skills']:
                        skills = original_data['technical_skills']
                        if isinstance(skills, dict):
                            # Take first category with skills
                            for category, skill_list in skills.items():
                                if isinstance(skill_list, list) and skill_list:
                                    top_skills = skill_list[:3]  # First 3 skills
                                    fixed_context['skills'] = f"{category}: {', '.join(top_skills)}"
                                    break
        
        return fixed_context