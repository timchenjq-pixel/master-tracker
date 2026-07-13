import streamlit as st
import time
from datetime import date, datetime, timedelta

# --- Page Config ---
st.set_page_config(page_title="Study Tracker", page_icon="📚", layout="centered")

# --- Custom CSS to Force a Square, Clickable Box ---
st.markdown("""
    <style>
    /* Remove the default Streamlit header */
    header {display: none !important;}
    #MainMenu {display: none !important;}
    footer {display: none !important;}

    /* THE FIX: Lock the invisible wrapper so it cannot stretch across the screen */
    div[data-testid="stPopover"] {
        position: fixed !important;
        top: 20px !important;
        right: 20px !important;
        z-index: 999999 !important;
        width: 80px !important;  
        height: 80px !important; 
    }
    
    /* Style the actual button to fill that 80x80 wrapper perfectly */
    div[data-testid="stPopover"] > button {
        border: 3px solid #4CAF50 !important;
        border-radius: 16px !important; 
        background-color: white !important;
        color: #4CAF50 !important;
        width: 100% !important;  
        height: 100% !important; 
        font-size: 30px !important; 
        padding: 0px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 0 !important;
    }

    /* Lock the width of the dropdown menu so it opens neatly below */
    div[data-testid="stPopoverBody"] {
        width: 320px !important;
        max-width: 90vw !important;
        right: 0px !important;
        left: auto !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- Core Data Setup ---
SUBJECTS = [
    "Chinese", "English", "Math", "History", 
    "Literature", "Geography", "Life Science", "Physical Science"
]

# State Initialization
for key in ["streaks", "half_sessions", "full_sessions"]:
    if key not in st.session_state:
        st.session_state[key] = {sub: 0 for sub in SUBJECTS}

if "last_studied_date" not in st.session_state:
    st.session_state.last_studied_date = {sub: None for sub in SUBJECTS}

# Timer Memory State (Prevents clicks from breaking the timer)
if "timer_active" not in st.session_state:
    st.session_state.timer_active = False
if "timer_end_time" not in st.session_state:
    st.session_state.timer_end_time = None
if "timer_subject" not in st.session_state:
    st.session_state.timer_subject = None
if "timer_type" not in st.session_state:
    st.session_state.timer_type = None

today = date.today()

# --- Streak Decay Logic ---
for sub in SUBJECTS:
    last_date = st.session_state.last_studied_date[sub]
    if last_date is not None:
        days_passed = (today - last_date).days
        if days_passed > 2:  
            st.session_state.streaks[sub] = 0
            st.session_state.half_sessions[sub] = 0
            st.session_state.full_sessions[sub] = 0
            st.session_state.last_studied_date[sub] = None

# --- Active Timer Display Logic ---
if st.session_state.timer_active:
    time_left = (st.session_state.timer_end_time - datetime.now()).total_seconds()
    
    if time_left > 0:
        timer_display = st.empty()
        for i in range(int(time_left), -1, -1):
            mins, secs = divmod(i, 60)
            timer_display.markdown(
                f"<h1 style='text-align: center; font-size: 80px; margin-top: 20vh;'>⏱️ {mins:02d}:{secs:02d}</h1>"
                f"<h3 style='text-align: center; color: gray;'>Focusing on {st.session_state.timer_subject}...</h3>", 
                unsafe_allow_html=True
            )
            time.sleep(1)
        timer_display.
