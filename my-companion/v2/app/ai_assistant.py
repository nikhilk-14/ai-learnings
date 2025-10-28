"""
AI Assistant Module
Provides enhanced chat interface with planning, memory, agent processing, and guardrails validation.
"""
import streamlit as st


def show(data, agent, guardrails):
    """Display enhanced AI Assistant chat interface"""
    st.header("💬 Enhanced AI Assistant")
    st.write("Now with planning and memory! Ask me anything about your profile.")
    
    # Simple chat interface (enhanced from v1)
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
            # Show simple metadata if available
            if "metadata" in message and message["metadata"]:
                with st.expander("Details"):
                    if "plan" in message["metadata"]:
                        st.write(f"**Plan:** {' → '.join(message['metadata']['plan'])}")
                    if "execution_time" in message["metadata"]:
                        st.write(f"**Time:** {message['metadata']['execution_time']}")
                    if "context_used" in message["metadata"]:
                        st.write(f"**Context:** {message['metadata']['context_used']} items")
    
    # Chat input
    if prompt := st.chat_input("Ask me about your profile..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.write(prompt)
        
        # Process with agent and guardrails
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Step 1: Validate input with simple guardrails
                    is_allowed, cleaned_prompt, violations = guardrails.validate_input(prompt)
                    
                    if not is_allowed:
                        response = "I can't process that request due to safety restrictions."
                        metadata = {"violations": [v.message for v in violations]}
                    else:
                        # Step 2: Process with agent (now with planning!)
                        result = agent.ask_question(cleaned_prompt)
                        
                        if result["success"]:
                            # Step 3: Filter response
                            filtered_response, response_violations = guardrails.filter_response(result["response"])
                            
                            response = filtered_response
                            metadata = {
                                "plan": result.get("plan", []),
                                "execution_time": result.get("execution_time", "N/A"),
                                "context_used": result.get("context_used", 0),
                                "violations": len(violations + response_violations)
                            }
                        else:
                            response = result.get("response", "Sorry, I encountered an error.")
                            metadata = {"error": result.get("error", "")}
                    
                    st.write(response)
                    
                    # Show metadata
                    if metadata and any(v for v in metadata.values() if v):
                        with st.expander("Response Details"):
                            for key, value in metadata.items():
                                if value:
                                    st.write(f"**{key.replace('_', ' ').title()}:** {value}")
                    
                    # Add to session
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response,
                        "metadata": metadata
                    })
                    
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "metadata": {"error": str(e)}
                    })