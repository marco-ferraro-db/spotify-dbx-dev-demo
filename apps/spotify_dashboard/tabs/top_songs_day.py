"""
Tab: Top Songs by Day
Shows most streamed songs on a specific date
"""

import streamlit as st
import pandas as pd
import plotly.express as px

from config import CATALOG, SCHEMA
from utils import load_data


def render_top_songs_day_tab():
    """Render the Top Songs by Day tab"""
    st.markdown("## 🎧 Most Streamed Songs on a Specific Day")
    st.markdown("##### Discover which songs dominated the charts on any given day")
    st.markdown("")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Load available dates
        if st.button("🔄 Load Available Dates", key="load_dates"):
            with st.spinner("Loading dates..."):
                dates_query = f"""
                SELECT DISTINCT chart_date 
                FROM {CATALOG}.{SCHEMA}.daily_chart_positions
                ORDER BY chart_date DESC
                """
                dates_df = load_data(dates_query, limit=1000)
                if not dates_df.empty:
                    st.session_state['available_dates'] = dates_df['chart_date'].tolist()
                    st.success(f"Loaded {len(dates_df)} dates")
        
        # Show date selector
        if 'available_dates' in st.session_state:
            selected_date = st.selectbox(
                "Select date",
                options=st.session_state['available_dates'],
                key="date_tab2"
            )
        else:
            st.info("👆 Click 'Load Available Dates' first")
            selected_date = None
        
        if st.button("Show Top Songs", key="load_day_songs"):
            if selected_date:
                with st.spinner("Loading top songs for the day..."):
                    query = f"""
                    SELECT 
                        title,
                        artist,
                        SUM(streams) as total_streams,
                        AVG(rank) as avg_rank
                    FROM {CATALOG}.{SCHEMA}.daily_chart_positions
                    WHERE chart_date = '{selected_date}'
                    GROUP BY title, artist
                    ORDER BY total_streams DESC
                    LIMIT 50
                    """
                    df = load_data(query, limit=50)
                    
                    if not df.empty:
                        # Create a combined column for display
                        df['song_display'] = df['title'] + ' - ' + df['artist']
                        st.session_state['day_songs_df'] = df
                        st.session_state['selected_date_display'] = selected_date
                    else:
                        st.error("No data returned.")
    
    with col2:
        if 'day_songs_df' in st.session_state:
            st.markdown(f"## 🎵 Top Songs on {st.session_state['selected_date_display']}")
            
            # Slider for display count
            display_count = st.slider("Number of songs to display", 5, 50, 20, key="display_day")
            top_songs = st.session_state['day_songs_df'].head(display_count)
            
            # Convert to numeric
            top_songs['total_streams'] = pd.to_numeric(top_songs['total_streams'], errors='coerce')
            
            fig = px.bar(
                top_songs,
                y='song_display',
                x='total_streams',
                orientation='h',
                labels={'total_streams': 'Total Streams', 'song_display': 'Song'},
                color='total_streams',
                color_continuous_scale='greens',
                height=max(400, display_count * 30)
            )
            fig.update_layout(
                showlegend=False,
                yaxis={'categoryorder':'total ascending'},
                xaxis_title="Total Streams",
                yaxis_title=""
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Stats
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                total_streams = top_songs['total_streams'].sum()
                st.metric("Total Streams", f"{total_streams:,.0f}")
            with col_b:
                st.metric("Songs Shown", len(top_songs))
            with col_c:
                unique_artists = top_songs['artist'].nunique()
                st.metric("Unique Artists", unique_artists)
        else:
            st.info("👈 Select a date and click 'Show Top Songs'")

