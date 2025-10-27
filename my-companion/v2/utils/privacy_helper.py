"""
Privacy Helper Utilities
Provides guidance and validation for maintaining client confidentiality
"""
import streamlit as st
from core.guardrails import Guardrails

def show_privacy_guidelines():
    """Show privacy guidelines for professional information"""
    with st.expander("🔒 Privacy Guidelines", expanded=False):
        st.write("""
        **Maintaining Client Confidentiality:**
        
        ✅ **Good Examples:**
        - "A Fortune 500 financial services company"
        - "Major e-commerce platform"
        - "Leading healthcare organization" 
        - "Technology startup in fintech domain"
        
        ❌ **Avoid Specific Names:**
        - Company names (ABC Corp, XYZ Inc)
        - Client names or project codes
        - Proprietary system names
        - Internal confidential terms
        
        💡 **Tips:**
        - Focus on domain/industry instead of specific companies
        - Describe technology and your role, not client details
        - Use generic terms like "client", "organization", "business partner"
        """)

def validate_client_privacy(text: str, field_name: str = "input") -> bool:
    """
    Validate text for client privacy and show warnings if needed
    Returns True if validation passes, False if concerns detected
    """
    guardrails = Guardrails()
    
    # Check for client information
    detections = guardrails.detect_client_info(text)
    
    if detections:
        st.warning(f"⚠️ Potential client information detected in {field_name}:")
        
        for detection in detections:
            st.write(f"- **{detection['type']}**: `{detection['match']}`")
            st.caption(f"💡 {detection['suggestion']}")
        
        st.info("Consider revising to use generic terms that maintain confidentiality while describing your experience.")
        return False
    
    return True

def get_privacy_safe_placeholder(field_type: str) -> str:
    """Get privacy-safe placeholder text for different field types"""
    placeholders = {
        'project_description': 'Led architecture for a financial services platform using microservices and cloud technologies...',
        'company_description': 'A leading technology company in the healthcare domain...',
        'client_work': 'Collaborated with stakeholders at a Fortune 500 retail organization...',
        'project_name': 'E-commerce Platform Modernization',
        'responsibilities': 'Designed and implemented solutions for business requirements, led team coordination...'
    }
    
    return placeholders.get(field_type, 'Enter your professional experience using generic terms...')

def suggest_generic_alternatives():
    """Show common generic alternatives for client descriptions"""
    with st.expander("📝 Generic Term Suggestions", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Company Types:**")
            st.write("- Fortune 500 company")
            st.write("- Technology startup") 
            st.write("- Healthcare organization")
            st.write("- Financial services firm")
            st.write("- E-commerce platform")
            st.write("- Manufacturing company")
            
        with col2:
            st.write("**Generic References:**")
            st.write("- The client")
            st.write("- The organization") 
            st.write("- Business stakeholders")
            st.write("- Project team")
            st.write("- End users")
            st.write("- The business")