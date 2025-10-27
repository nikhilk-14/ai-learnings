"""
Simple Lightweight Guardrails - Basic safety without heavy frameworks
Just essential input validation and output filtering
"""
import re
import time
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class SafetyViolation:
    """Simple violation record"""
    type: str
    message: str
    severity: str  # "low", "medium", "high"


class Guardrails:
    """
    Lightweight guardrails system with basic safety checks
    No external frameworks, just essential validation
    """
    
    def __init__(self):
        # Rate limiting storage
        self.rate_limit_storage = {}
        self.max_requests_per_minute = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "10"))
        
        # Client privacy protection patterns
        self.client_detection_enabled = os.getenv("CLIENT_PRIVACY_PROTECTION", "true").lower() == "true"
        self._load_client_patterns()
        
        # Basic PII patterns (simplified)
        self.pii_patterns = {
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'phone': re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),
            'ssn': re.compile(r'\b\d{3}-?\d{2}-?\d{4}\b'),
            'credit_card': re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b')
        }
        
        # Basic unsafe content patterns
        self.unsafe_patterns = [
            re.compile(r'\b(password|secret|private key|api key)\s*[:=]\s*\S+', re.IGNORECASE),
            re.compile(r'<script|javascript:|data:text/html', re.IGNORECASE),
        ]
        
        # Blocked topics (simple keyword matching)
        self.blocked_topics = [
            'illegal', 'violence', 'harmful', 'hack', 'exploit', 'malware'
        ]
    
    def _load_client_patterns(self):
        """Load client/company detection patterns"""
        # Common business entity indicators
        self.client_patterns = {
            'company_indicators': re.compile(r'\b(Inc\.?|LLC|Corp\.?|Corporation|Ltd\.?|Limited|Company|Co\.)\b', re.IGNORECASE),
            'business_terms': re.compile(r'\b(client|customer|employer|organization|firm|enterprise|business|vendor|contractor)\s+[A-Z][a-zA-Z\s&]{2,20}\b'),
            'project_codes': re.compile(r'\b[A-Z]{2,4}-\d{3,6}\b'),  # Project codes like ABC-1234
            'confidential_terms': re.compile(r'\b(confidential|proprietary|internal|private|restricted|classified)\b', re.IGNORECASE)
        }
        
        # Load custom client patterns from environment or file
        custom_patterns = os.getenv("CUSTOM_CLIENT_PATTERNS", "")
        if custom_patterns:
            try:
                # Expected format: "pattern1|pattern2|pattern3"
                patterns = [p.strip() for p in custom_patterns.split("|") if p.strip()]
                if patterns:
                    self.client_patterns['custom'] = re.compile('|'.join(patterns), re.IGNORECASE)
            except Exception as e:
                print(f"Warning: Could not load custom client patterns: {e}")
    
    def validate_input(self, user_input: str, user_id: str = "default") -> Tuple[bool, str, List[SafetyViolation]]:
        """
        Validate user input with basic safety checks
        Returns: (is_allowed, cleaned_input, violations)
        """
        violations = []
        cleaned_input = user_input
        
        # Rate limiting check
        if not self._check_rate_limit(user_id):
            violations.append(SafetyViolation(
                type="rate_limit",
                message="Too many requests. Please slow down.",
                severity="high"
            ))
            return False, cleaned_input, violations
        
        # Check for blocked topics
        input_lower = user_input.lower()
        for topic in self.blocked_topics:
            if topic in input_lower:
                violations.append(SafetyViolation(
                    type="blocked_content",
                    message=f"Content related to '{topic}' is not allowed",
                    severity="high"
                ))
        
        # Check for PII and mask it
        for pii_type, pattern in self.pii_patterns.items():
            if pattern.search(cleaned_input):
                violations.append(SafetyViolation(
                    type="pii_detected",
                    message=f"Potential {pii_type} detected and masked",
                    severity="medium"
                ))
                cleaned_input = pattern.sub(f"[MASKED_{pii_type.upper()}]", cleaned_input)
        
        # Check for client/company information if enabled
        if self.client_detection_enabled:
            cleaned_input = self._sanitize_client_info(cleaned_input, violations)
        
        # Check for unsafe patterns
        for pattern in self.unsafe_patterns:
            if pattern.search(cleaned_input):
                violations.append(SafetyViolation(
                    type="unsafe_content",
                    message="Potentially unsafe content detected",
                    severity="high"
                ))
        
        # Determine if request is allowed (block only high severity violations)
        high_severity_violations = [v for v in violations if v.severity == "high"]
        is_allowed = len(high_severity_violations) == 0
        
        return is_allowed, cleaned_input, violations
    
    def filter_response(self, response: str) -> Tuple[str, List[SafetyViolation]]:
        """
        Filter AI response for safety
        Returns: (filtered_response, violations)
        """
        violations = []
        filtered_response = response
        
        # Check for PII in response and mask it
        for pii_type, pattern in self.pii_patterns.items():
            if pattern.search(filtered_response):
                violations.append(SafetyViolation(
                    type="response_pii",
                    message=f"PII ({pii_type}) detected in response and masked",
                    severity="medium"
                ))
                filtered_response = pattern.sub(f"[MASKED_{pii_type.upper()}]", filtered_response)
        
        # Check for unsafe patterns in response
        for pattern in self.unsafe_patterns:
            if pattern.search(filtered_response):
                violations.append(SafetyViolation(
                    type="unsafe_response",
                    message="Unsafe content detected in AI response",
                    severity="high"
                ))
                # Replace with safe message if high severity
                filtered_response = "I cannot provide that information for safety reasons."
                break
        
        return filtered_response, violations
    
    def _check_rate_limit(self, user_id: str) -> bool:
        """Simple rate limiting check"""
        now = datetime.now()
        
        # Clean old entries
        if user_id in self.rate_limit_storage:
            self.rate_limit_storage[user_id] = [
                timestamp for timestamp in self.rate_limit_storage[user_id]
                if now - timestamp < timedelta(minutes=1)
            ]
        else:
            self.rate_limit_storage[user_id] = []
        
        # Check if under limit
        if len(self.rate_limit_storage[user_id]) >= self.max_requests_per_minute:
            return False
        
        # Add current request
        self.rate_limit_storage[user_id].append(now)
        return True
    
    def _sanitize_client_info(self, text: str, violations: List[SafetyViolation]) -> str:
        """Detect and sanitize client/company information"""
        sanitized_text = text
        
        # Check each client pattern
        for pattern_name, pattern in self.client_patterns.items():
            matches = pattern.findall(sanitized_text)
            if matches:
                violations.append(SafetyViolation(
                    type="client_info_detected",
                    message=f"Potential client/business information detected ({pattern_name})",
                    severity="medium"
                ))
                
                # Replace with generic terms
                if pattern_name == 'company_indicators':
                    sanitized_text = pattern.sub('[COMPANY]', sanitized_text)
                elif pattern_name == 'business_terms':
                    sanitized_text = pattern.sub('a business partner', sanitized_text)
                elif pattern_name == 'project_codes':
                    sanitized_text = pattern.sub('[PROJECT-CODE]', sanitized_text)
                elif pattern_name == 'confidential_terms':
                    sanitized_text = pattern.sub('[CONFIDENTIAL]', sanitized_text)
                else:
                    sanitized_text = pattern.sub('[CLIENT-INFO]', sanitized_text)
        
        return sanitized_text
    
    def detect_client_info(self, text: str) -> List[Dict[str, str]]:
        """Public method to detect client info without sanitizing - for form validation"""
        if not self.client_detection_enabled:
            return []
        
        detections = []
        for pattern_name, pattern in self.client_patterns.items():
            matches = pattern.findall(text)
            for match in matches:
                detections.append({
                    'type': pattern_name,
                    'match': match if isinstance(match, str) else ' '.join(match),
                    'suggestion': 'Consider using generic terms like "a client", "the company", or "the organization"'
                })
        return detections
    
    def get_stats(self) -> Dict[str, any]:
        """Get simple guardrails statistics"""
        return {
            "enabled": True,
            "active_users": len(self.rate_limit_storage),
            "max_requests_per_minute": self.max_requests_per_minute,
            "pii_patterns": len(self.pii_patterns),
            "unsafe_patterns": len(self.unsafe_patterns),
            "blocked_topics": len(self.blocked_topics)
        }