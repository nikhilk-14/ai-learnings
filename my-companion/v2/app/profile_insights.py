"""
Profile Insights Module
Provides AI-powered insights and analysis for profile data including career suggestions,
project ideas, skill analysis, and profile analysis.
"""
import streamlit as st


def show(data, agent):
    """Display AI insights interface with various analysis options"""
    st.subheader("💡 AI Insights")
    st.write("Get AI-powered insights about your profile, skills, and career opportunities")
    
    # Insights interface with caching
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎯 Analyze Profile", type="primary"):
            with st.spinner("Analyzing your profile..."):
                try:
                    prompt = """Analyze this professional profile and provide insights on:
                    1. Key strengths and expertise areas
                    2. Profile completeness and suggestions for improvement
                    3. Professional positioning and value proposition
                    4. Areas that could use more detail or examples
                    
                    Please be specific and actionable in your recommendations."""
                    
                    result = agent.ask_question(prompt)
                    if result["success"]:
                        st.success("✅ Profile Analysis Complete!")
                        st.write(result["response"])
                    else:
                        st.error(f"Analysis failed: {result.get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Error during analysis: {str(e)}")
        
        if st.button("📈 Career Suggestions"):
            with st.spinner("Generating career suggestions..."):
                try:
                    prompt = """Based on this professional profile, suggest:
                    1. Potential career advancement opportunities
                    2. Related roles that would be a good fit
                    3. Industries or companies that would value this skillset
                    4. Next steps for career growth
                    
                    Focus on realistic and achievable suggestions."""
                    
                    result = agent.ask_question(prompt)
                    if result["success"]:
                        st.success("✅ Career Suggestions Ready!")
                        st.write(result["response"])
                    else:
                        st.error(f"Suggestion failed: {result.get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Error generating suggestions: {str(e)}")
    
    with col2:
        if st.button("🚀 Project Ideas"):
            with st.spinner("Brainstorming project ideas..."):
                try:
                    prompt = """Suggest project ideas based on this professional profile:
                    1. Projects that would showcase current skills
                    2. Projects to learn new technologies
                    3. Open source contribution opportunities
                    4. Portfolio projects for career advancement
                    
                    Make suggestions specific and actionable with clear next steps."""
                    
                    result = agent.ask_question(prompt)
                    if result["success"]:
                        st.success("✅ Project Ideas Generated!")
                        st.write(result["response"])
                    else:
                        st.error(f"Project generation failed: {result.get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Error generating projects: {str(e)}")
        
        if st.button("📊 Skill Analysis"):
            with st.spinner("Analyzing skills and gaps..."):
                try:
                    prompt = """Analyze the technical skills in this profile:
                    1. Skill strengths and areas of expertise
                    2. Potential skill gaps for current role/goals
                    3. Emerging technologies to consider learning
                    4. Skill combinations that create unique value
                    
                    Provide specific learning recommendations and resources when possible."""
                    
                    result = agent.ask_question(prompt)
                    if result["success"]:
                        st.success("✅ Skill Analysis Complete!")
                        st.write(result["response"])
                    else:
                        st.error(f"Skill analysis failed: {result.get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Error during skill analysis: {str(e)}")
    
    # Cache info
    st.divider()
    st.info("💡 **Tip:** AI insights are generated in real-time based on your current profile data. Update your profile and regenerate insights to see new recommendations.")