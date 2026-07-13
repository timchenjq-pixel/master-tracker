import streamlit as st
import time
from datetime import date

# --- Page Config ---
st.set_page_config(page_title="Tim's Setup", page_icon="📚", layout="centered")

# --- Custom CSS for the Top-Right Floating Box ---
st.markdown("""
    <style>
    /* Float the small box to the top right */
    div[data-testid="stPopover"] {
        position: fixed !important;
        top: 15px !important;
        right: 15px !important;
        z-index: 999999 !important;
    }
    
    /* Force the button to be small and not stretch */
    div[data-testid="stPopover"] > button {
        border: 2px solid #4CAF50 !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
        padding: 8px 16px !important;
        background-color: white !important;
        color: #4CAF50 !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2) !important;
        width: auto !important; 
    }

    /* Constrain the dropdown menu so it doesn't cover the whole screen */
    div[data-testid="stPopoverBody"] {
        width: 300px !important;
        max-width: 90vw !important;
    }

    /* Hide the default Streamlit header and footer for max cleanliness */
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

today = date.today()

# --- Streak Decay Logic ---
for sub in SUBJECTS:
    last_date = st.session_state.last_studied_date[sub]
    if last_date is not None:
        days_passed = (today - last_date).days
        if days_passed > 2:  # Streak shatters
            st.session_state.streaks[sub] = 0
            st.session_state.half_sessions[sub] = 0
            st.session_state.full_sessions[sub] = 0
            st.session_state.last_studied_date[sub] = None

# Placeholder for the giant focus timer
timer_display = st.empty()

def run_timer(minutes, subject):
    total_seconds = minutes * 60
    for i in range(total_seconds, -1, -1):
        mins, secs = divmod(i, 60)
        timer_display.markdown(
            f"<h1 style='text-align: center; font-size: 80px; margin-top: 20vh;'>⏱️ {mins:02d}:{secs:02d}</h1>"
            f"<h3 style='text-align: center; color: gray;'>Focusing on {subject}...</h3>", 
            unsafe_allow_html=True
        )
        time.sleep(1)
    timer_display.empty()
    return True

# --- The Floating Popover ---
ui_container = st.empty()

with ui_container.container():
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
                        ui_container.empty() 
                        if run_timer(15, sub):
                            st.session_state.full_sessions[sub] += 1
                            if not has_completed_today and ((st.session_state.full_sessions[sub] >= 1) or (st.session_state.half_sessions[sub] >= 2)):
                                st.session_state.streaks[sub] += 1
                                st.session_state.last_studied_date[sub] = today
                            st.rerun() 
                            
                with col2:
                    if st.button("⚡ Half", key=f"half_{sub}", use_container_width=True):
                        ui_container.empty() 
                        if run_timer(5, sub):
                            st.session_state.half_sessions[sub] += 1
                            if not has_completed_today and ((st.session_state.full_sessions[sub] >= 1) or (st.session_state.half_sessions[sub] >= 2)):
                                st.session_state.streaks[sub] += 1
                                st.session_state.last_studied_date[sub] = today
                            st.rerun()
