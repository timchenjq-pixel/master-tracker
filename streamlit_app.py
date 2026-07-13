import streamlit as st
import time
from datetime import date, datetime, timedelta

# --- Page Config ---
st.set_page_config(page_title="Study Tracker", page_icon="📚", layout="centered")

# --- Custom CSS to Force a Tiny Box ---
st.markdown("""
    <style>
    /* Force the button to sit in the top corner and be small */
    div[data-testid="stPopover"] {
        position: fixed !important;
        top: 15px !important;
        right: 15px !important; /* Change to left: 15px if you prefer top-left */
        z-index: 999999 !important;
        width: auto !important;
    }
    
    /* Make the button look like a compact box */
    div[data-testid="stPopover"] > button {
        border: 2px solid #4CAF50 !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        padding: 5px 15px !important;
        background-color: white !important;
        color: #4CAF50 !important;
        width: auto !important; 
        min-width: 120px !important;
    }

    /* Lock the width of the dropdown menu so it doesn't stretch */
    div[data-testid="stPopoverBody"] {
        width: 320px !important;
        max-width: 90vw !important;
        right: 0px !important;
        left: auto !important;
    }

    /* Hide standard Streamlit clutter */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
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

# Timer Memory State (This prevents clicks from breaking the timer)
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
    # Calculate how much time is left based on the real-world clock
    time_left = (st.session_state.timer_end_time - datetime.now()).total_seconds()
    
    if time_left > 0:
        timer_display = st.empty()
        # Resume the countdown loop
        for i in range(int(time_left), -1, -1):
            mins, secs = divmod(i, 60)
            timer_display.markdown(
                f"<h1 style='text-align: center; font-size: 80px; margin-top: 20vh;'>⏱️ {mins:02d}:{secs:02d}</h1>"
                f"<h3 style='text-align: center; color: gray;'>Focusing on {st.session_state.timer_subject}...</h3>"
                f"<p style='text-align: center; color: lightgray;'>Clicks won't kick you out anymore.</p>", 
                unsafe_allow_html=True
            )
            time.sleep(1)
        timer_display.empty()
        
    # When timer finishes normally
    sub = st.session_state.timer_subject
    t_type = st.session_state.timer_type
    has_completed_today = (st.session_state.full_sessions[sub] >= 1) or (st.session_state.half_sessions[sub] >= 2)
    
    if t_type == "full":
        st.session_state.full_sessions[sub] += 1
    else:
        st.session_state.half_sessions[sub] += 1
        
    if not has_completed_today and ((st.session_state.full_sessions[sub] >= 1) or (st.session_state.half_sessions[sub] >= 2)):
        st.session_state.streaks[sub] += 1
        st.session_state.last_studied_date[sub] = today
        
    # Reset timer state and reload the menu
    st.session_state.timer_active = False
    st.rerun()

# --- The Floating UI Menu (Hidden when timer runs) ---
if not st.session_state.timer_active:
    with st.popover("📚 Tracker"):
        for sub in SUBJECTS:
            has_completed_today = (st.session_state.full_sessions[sub] >= 1) or (st.session_state.half_sessions[sub] >= 2)
            status_emoji = "✅" if has_completed_today else "⏳"
            streak_val = st.session_state.streaks[sub]
            
            with st.expander(f"{status_emoji} {sub} (Streak: {streak_val}d)"):
                st.checkbox("Completed for today", value=has_completed_today, disabled=True, key=f"status_{sub}")
                st.write(f"Progress: Full ({st.session_state.full_sessions[sub]}/1) | Half ({st.session_state.half_sessions[sub]}/2)")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("⏱️ Full", key=f"full_{sub}", use_container_width=True):
                        st.session_state.timer_active = True
                        st.session_state.timer_end_time = datetime.now() + timedelta(minutes=15)
                        st.session_state.timer_subject = sub
                        st.session_state.timer_type = "full"
                        st.rerun() 
                            
                with col2:
                    if st.button("⚡ Half", key=f"half_{sub}", use_container_width=True):
                        st.session_state.timer_active = True
                        st.session_state.timer_end_time = datetime.now() + timedelta(minutes=5)
                        st.session_state.timer_subject = sub
                        st.session_state.timer_type = "half"
                        st.rerun()
