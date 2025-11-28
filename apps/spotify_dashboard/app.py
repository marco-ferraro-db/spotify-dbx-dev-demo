"""
Spotify Charts Analytics Dashboard
Main application entry point
"""

import streamlit as st

# Import configuration and styling
from config import PAGE_CONFIG
from styles import CUSTOM_CSS

# Import tab modules
from tabs import (
    render_top_artists_year_tab,
    render_top_songs_day_tab,
    render_top_artists_region_tab,
    render_chatbot_tab
)


def main():
    """Main application function"""
    
    # Page configuration
    st.set_page_config(**PAGE_CONFIG)
    
    # Apply custom CSS
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-title">🎵 Spotify Charts Analytics</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Powered by Databricks Asset Bundles & Delta Live Tables</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎵 Top Artists by Year",
        "🎧 Top Songs by Day", 
        "🌍 Top Artists by Region",
        "💬 AI Chat Assistant"
    ])
    
    # Render each tab
    with tab1:
        render_top_artists_year_tab()
    
    with tab2:
        render_top_songs_day_tab()
    
    with tab3:
        render_top_artists_region_tab()
    
    with tab4:
        render_chatbot_tab()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #888; padding: 20px;'>
        <p style='font-size: 0.9rem;'>
            🎵 <strong>Spotify Analytics Dashboard</strong> | 
            Powered by <strong>Databricks Asset Bundles</strong> & <strong>Delta Live Tables</strong>
        </p>
        <p style='font-size: 0.8rem; margin-top: 10px;'>
            📊 Data Source: <code>spotify_dev.prod_schema</code> | 
            🎯 Tables: daily_chart_positions, monthly_artist_performance, monthly_top_100_artists
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

