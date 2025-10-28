"""
Profile Search Module
Provides semantic search functionality across all profile data using vector database.
"""
import streamlit as st


def show(data, vector_db):
    """Display search interface for profile data"""
    st.subheader("🔍 Search Profile")
    st.write("Search through all your profile data using semantic search")
    
    # Search interface
    search_query = st.text_input("Search your profile:", placeholder="e.g., 'angular projects', 'cloud experience', 'leadership skills'")
    
    #max_results = st.number_input("Max results:", min_value=1, max_value=20, value=5)
    max_results = 5  # Fixed to 5 for simplicity

    if st.button("🔍 Search", type="primary"):
        if search_query:
            with st.spinner("Searching..."):
                try:
                    # Use the existing vector database for search (search entire profile)
                    search_results = vector_db.search(search_query, top_k=max_results)
                    
                    if search_results:
                        st.success(f"Found {len(search_results)} results:")
                        
                        for i, result in enumerate(search_results, 1):
                            metadata = result.get('metadata', {})
                            source = metadata.get('source', 'Unknown')
                            result_type = metadata.get('type', 'content')
                            
                            # Create a more descriptive title
                            if source == 'user_profile':
                                title = f"Profile - {metadata.get('key', 'Info')}"
                            elif source == 'technical_skills':
                                title = f"Skill - {metadata.get('category', 'General')}"
                            elif source == 'projects':
                                title = f"Project - {metadata.get('name', 'Unknown')}"
                            elif source == 'other_activities':
                                title = f"Activity - {metadata.get('name', 'Unknown')}"
                            else:
                                title = f"{source.title()} - {result_type}"
                            
                            with st.expander(f"#{i} - {title} (Score: {result['score']:.3f})"):
                                st.write(f"**Content:** {result['text']}")
                                st.write(f"**Source:** {source.replace('_', ' ').title()}")
                                if metadata.get('category'):
                                    st.write(f"**Category:** {metadata['category']}")
                                if metadata.get('name') and source != 'projects':
                                    st.write(f"**Name:** {metadata['name']}")
                    else:
                        st.info("No results found. Try different keywords or check if your profile data is indexed.")
                        
                except Exception as e:
                    st.error(f"Search error: {str(e)}")
                    st.info("💡 Try rebuilding the vector database from the sidebar if search isn't working.")
                    
        else:
            st.warning("Please enter a search term.")