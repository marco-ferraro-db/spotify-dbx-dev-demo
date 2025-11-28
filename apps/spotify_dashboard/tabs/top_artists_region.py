"""
Tab: Top Artists by Region
Shows top artists filtered by region and year
"""

import streamlit as st
import pandas as pd
import plotly.express as px

from config import CATALOG, SCHEMA
from utils import load_data


def render_top_artists_region_tab():
    """Render the Top Artists by Region tab"""
    st.markdown("## 🌍 Top Artists per Region")
    st.markdown("##### Top performing artists filtered by region and year")
    st.markdown("")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Load available filters
        if st.button("🔄 Load Filters", key="load_filters"):
            with st.spinner("Loading filters..."):
                # Load regions
                regions_query = f"""
                SELECT DISTINCT region 
                FROM {CATALOG}.{SCHEMA}.monthly_top_100_artists
                ORDER BY region
                """
                regions_df = load_data(regions_query, limit=1000)
                
                # Load years
                years_query = f"""
                SELECT DISTINCT year 
                FROM {CATALOG}.{SCHEMA}.monthly_top_100_artists
                ORDER BY year DESC
                """
                years_df = load_data(years_query, limit=1000)
                
                if not regions_df.empty and not years_df.empty:
                    st.session_state['available_regions'] = ['All'] + regions_df['region'].tolist()
                    st.session_state['available_years'] = ['All'] + years_df['year'].tolist()
                    st.success(f"Loaded {len(regions_df)} regions and {len(years_df)} years")
        
        # Show region selector
        if 'available_regions' in st.session_state:
            filter_region = st.selectbox(
                "Select region",
                options=st.session_state['available_regions'],
                key="filter_region"
            )
        else:
            st.info("👆 Click 'Load Filters' first")
            filter_region = None
        
        # Show year selector
        if 'available_years' in st.session_state:
            filter_year = st.selectbox(
                "Select year",
                options=st.session_state['available_years'],
                key="filter_year"
            )
        else:
            filter_year = None
        
        if st.button("Load Top Artists", key="load_top"):
            with st.spinner("Loading data..."):
                where_clauses = []
                
                if filter_region and filter_region != 'All':
                    where_clauses.append(f"region = '{filter_region}'")
                
                if filter_year and filter_year != 'All':
                    where_clauses.append(f"year = {filter_year}")
                
                where_clause = ""
                if where_clauses:
                    where_clause = "WHERE " + " AND ".join(where_clauses)
                
                query = f"""
                SELECT 
                    artist,
                    total_streams
                FROM {CATALOG}.{SCHEMA}.monthly_top_100_artists
                {where_clause}
                ORDER BY total_streams DESC
                """
                df = load_data(query, limit=100)
                
                if not df.empty:
                    st.session_state['top_df'] = df
                else:
                    st.error("No data returned. Check if tables exist.")
    
    with col2:
        if 'top_df' in st.session_state:
            # Show only the chart
            if not st.session_state['top_df'].empty and len(st.session_state['top_df']) > 0:
                # Get top N based on user preference
                display_count = st.slider("Number of artists to display", 5, 50, 10, key="display_count")
                top_artists = st.session_state['top_df'].head(display_count)
                
                # Convert total_streams to numeric
                top_artists['total_streams'] = pd.to_numeric(top_artists['total_streams'], errors='coerce')
                
                st.markdown(f"### 📊 Top {display_count} Artists by Total Streams")
                st.info(f"Total artists found: {len(st.session_state['top_df'])}")
                
                fig = px.bar(
                    top_artists,
                    x='artist',
                    y='total_streams',
                    labels={'total_streams': 'Total Streams', 'artist': 'Artist'},
                    color='total_streams',
                    color_continuous_scale='blues',
                    height=600
                )
                fig.update_layout(
                    xaxis_tickangle=-45,
                    showlegend=False,
                    xaxis_title="Artist",
                    yaxis_title="Total Streams"
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("👈 Select filters and click 'Load Top Artists' to view the chart")

