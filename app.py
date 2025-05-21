"""
Grabalo Concurrency Dashboard
"""

import streamlit as st

# Make sure to import the new function
from helpers import get_active_keys, get_active_meeting_count

st.set_page_config(page_title="Grabalo Concurrency Dashboard", page_icon="🔑")

st.title("Grabalo Concurrency Dashboard")

# Get Active Deepgram API Keys
active_keys = get_active_keys()
if isinstance(active_keys, str) and "Error" in active_keys:
    st.error(f"Deepgram Keys: {active_keys}")
    active_keys_value = "Error"
else:
    active_keys_value = active_keys

st.metric(label="Active Deepgram API Keys", value=active_keys_value)

# Get Active Meetings
active_meetings = get_active_meeting_count()
if isinstance(active_meetings, str) and "Error" in active_meetings:
    st.error(f"Active Meetings: {active_meetings}")
    active_meetings_value = "Error"
else:
    active_meetings_value = active_meetings

st.metric(label="Active Meetings 🔴", value=active_meetings_value)
