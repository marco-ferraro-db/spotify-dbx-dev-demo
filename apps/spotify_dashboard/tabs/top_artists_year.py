"""
Tab: Top Artists by Year
Shows global top artists for a selected year
"""

import streamlit as st
import pandas as pd
import plotly.express as px

from config import CATALOG, SCHEMA
from utils import load_data


def render_top_artists_year_tab():
    """Render the Top Artists by Year tab"""
    st.markdown("## 🎵 Global Top Artists by Year")
    st.markdown("##### Discover the most-streamed artists worldwide each year")
    st.markdown("")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Load available years
        if st.button("🔄 Load Years", key="load_years_tab1"):
            with st.spinner("Loading years..."):
                years_query = f"""
                SELECT DISTINCT year 
                FROM {CATALOG}.{SCHEMA}.monthly_artist_performance
                ORDER BY year DESC
                """
                years_df = load_data(years_query, limit=100)
                if not years_df.empty:
                    st.session_state['available_years_tab1'] = years_df['year'].tolist()
                    st.success(f"Loaded {len(years_df)} years")
        
        # Show year selector
        if 'available_years_tab1' in st.session_state:
            selected_year = st.selectbox(
                "Select year",
                options=st.session_state['available_years_tab1'],
                key="year_tab1"
            )
        else:
            st.info("👆 Click 'Load Years' first")
            selected_year = None
        
        if st.button("Show Top Artists", key="load_year_artists"):
            if selected_year:
                with st.spinner("Loading top artists..."):
                    query = f"""
                    SELECT 
                        artist,
                        SUM(total_streams) as total_streams
                    FROM {CATALOG}.{SCHEMA}.monthly_artist_performance
                    WHERE year = {selected_year}
                    GROUP BY artist
                    ORDER BY total_streams DESC
                    LIMIT 50
                    """
                    df = load_data(query, limit=50)
                    
                    if not df.empty:
                        st.session_state['year_artists_df'] = df
                        st.session_state['selected_year_display'] = selected_year
                    else:
                        st.error("No data returned.")
    
    with col2:
        if 'year_artists_df' in st.session_state:
            st.markdown(f"## 🏆 Top Artists of {st.session_state['selected_year_display']}")
            
            # Slider for display count
            display_count = st.slider("Number of artists to display", 5, 50, 20, key="display_year")
            top_artists = st.session_state['year_artists_df'].head(display_count)
            
            # Convert to numeric
            top_artists['total_streams'] = pd.to_numeric(top_artists['total_streams'], errors='coerce')
            
            fig = px.bar(
                top_artists,
                y='artist',
                x='total_streams',
                orientation='h',
                labels={'total_streams': 'Total Streams', 'artist': 'Artist'},
                color='total_streams',
                color_continuous_scale='purples',
                height=max(400, display_count * 25)
            )
            fig.update_layout(
                showlegend=False,
                yaxis={'categoryorder':'total ascending'},
                xaxis_title="Total Streams",
                yaxis_title=""
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Stats
            col_a, col_b = st.columns(2)
            with col_a:
                total_streams = top_artists['total_streams'].sum()
                st.metric("Total Streams (Top Artists)", f"{total_streams:,.0f}")
            with col_b:
                st.metric("Artists Shown", len(top_artists))
        else:
            st.info("👈 Select a year and click 'Show Top Artists'")

