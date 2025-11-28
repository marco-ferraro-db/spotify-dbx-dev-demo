"""
Tab: AI Chat Assistant
Provides an AI-powered chatbot to answer questions about the Spotify data
"""

import streamlit as st
from databricks.sdk.service.serving import ChatMessage, ChatMessageRole

from config import CATALOG, SCHEMA, DEFAULT_MODEL_ENDPOINT
from utils import get_workspace_client


def render_chatbot_tab():
    """Render the AI Chat Assistant tab"""
    st.markdown("## 💬 AI Chat Assistant")
    st.markdown("##### Ask questions about your Spotify data using AI powered by Llama")
    st.markdown("")
    
    # Configuration
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("### ⚙️ Configuration")
        st.markdown("")
        
        # Endpoint configuration
        endpoint_name = st.text_input(
            "🤖 Model Serving Endpoint",
            value=DEFAULT_MODEL_ENDPOINT,
            help="Enter your Databricks Model Serving endpoint name"
        )
        
        st.markdown("")
        
        # System context about the data
        st.markdown("### 📊 Data Context")
        st.info(f"""
        **Catalog:** `{CATALOG}`  
        **Schema:** `{SCHEMA}`
        
        **Available Tables:**
        - 📅 `daily_chart_positions`  
          Daily chart data
        - 📊 `monthly_artist_performance`  
          Monthly aggregated metrics
        - 🏆 `monthly_top_100_artists`  
          Top 100 artists per region
        """)
        
        st.markdown("")
        
        if st.button("🗑️ Clear Chat History"):
            st.session_state['chat_messages'] = []
            st.rerun()
    
    with col2:
        # Initialize chat history
        if 'chat_messages' not in st.session_state:
            st.session_state['chat_messages'] = []
        
        # Display chat messages
        for message in st.session_state['chat_messages']:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask me about Spotify data..."):
            # Add user message to chat history
            st.session_state['chat_messages'].append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        # Build context about the data
                        system_context = f"""You are a helpful AI assistant for Spotify Charts Analytics. 
                        
You have access to the following data:
- Catalog: {CATALOG}, Schema: {SCHEMA}
- Tables:
  1. daily_chart_positions: Contains daily chart positions with columns like chart_date, title, artist, rank, region, streams, trend
  2. monthly_artist_performance: Monthly aggregated metrics with columns like artist, region, year, month, total_streams, avg_rank, best_rank, chart_appearances, unique_songs
  3. monthly_top_100_artists: Top 100 artists per region per month

When users ask about the data, provide helpful insights. If they ask for specific data queries, explain what SQL query would be needed. Be conversational and helpful."""

                        # Build messages for the API
                        messages = [
                            {"role": "system", "content": system_context}
                        ]
                        
                        # Add recent chat history (last 10 messages)
                        recent_messages = st.session_state['chat_messages'][-10:]
                        for msg in recent_messages:
                            messages.append({"role": msg["role"], "content": msg["content"]})
                        
                        # Use the workspace client directly - it handles auth automatically
                        w = get_workspace_client()
                        
                        # Convert messages to SDK format
                        sdk_messages = []
                        for msg in messages:
                            role = ChatMessageRole.SYSTEM if msg["role"] == "system" else (
                                ChatMessageRole.USER if msg["role"] == "user" else ChatMessageRole.ASSISTANT
                            )
                            sdk_messages.append(ChatMessage(role=role, content=msg["content"]))
                        
                        # Query the endpoint using SDK (handles auth automatically)
                        response = w.serving_endpoints.query(
                            name=endpoint_name,
                            messages=sdk_messages,
                            max_tokens=1000,
                            temperature=0.7
                        )
                        
                        # Extract response
                        assistant_message = None
                        
                        if hasattr(response, 'choices') and response.choices and len(response.choices) > 0:
                            assistant_message = response.choices[0].message.content
                        elif hasattr(response, 'predictions'):
                            # Handle dataframe response format
                            if response.predictions and len(response.predictions) > 0:
                                pred = response.predictions[0]
                                if hasattr(pred, 'choices') and pred.choices:
                                    assistant_message = pred.choices[0].message.content
                        
                        if not assistant_message:
                            # Try dict access
                            try:
                                if isinstance(response, dict):
                                    if 'choices' in response:
                                        assistant_message = response['choices'][0]['message']['content']
                            except:
                                pass
                        
                        if not assistant_message:
                            assistant_message = f"Received response but couldn't extract message. Please check the endpoint format."
                        
                        # Display and save response
                        st.markdown(assistant_message)
                        st.session_state['chat_messages'].append({
                            "role": "assistant", 
                            "content": assistant_message
                        })
                        
                    except Exception as e:
                        error_message = f"❌ Error: {str(e)}\n\n**Troubleshooting:**\n- Make sure endpoint '{endpoint_name}' exists\n- Check if the endpoint is in 'Ready' state\n- Verify you have access to the endpoint"
                        st.error(error_message)
                        st.session_state['chat_messages'].append({
                            "role": "assistant", 
                            "content": error_message
                        })
        
        # Suggestions
        if len(st.session_state['chat_messages']) == 0:
            st.markdown("### 💡 Try asking:")
            suggestions = [
                "What data is available in the Spotify charts?",
                "How can I find the top artists for 2017?",
                "What insights can I get from the monthly performance table?",
                "Explain the difference between the daily and monthly tables",
                "What questions can I ask about this data?"
            ]
            for suggestion in suggestions:
                if st.button(suggestion, key=f"suggest_{suggestion[:20]}"):
                    st.session_state['chat_messages'].append({"role": "user", "content": suggestion})
                    st.rerun()

