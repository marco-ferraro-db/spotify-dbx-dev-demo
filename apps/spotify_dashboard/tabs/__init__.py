"""
Tab modules for the Spotify Analytics Dashboard
"""

from .top_artists_year import render_top_artists_year_tab
from .top_songs_day import render_top_songs_day_tab
from .top_artists_region import render_top_artists_region_tab
from .chatbot import render_chatbot_tab

__all__ = [
    'render_top_artists_year_tab',
    'render_top_songs_day_tab',
    'render_top_artists_region_tab',
    'render_chatbot_tab'
]

