import streamlit as st
import time
from datetime import date

# --- Page Config ---
st.set_page_config(page_title="Tim's Hub", page_icon="📚", layout="centered")

# --- Custom CSS for the Top-Right Floating Box ---
st.markdown("""
    <style>
    /* Float the small box to the top right */
    div[data-testid="stPopover"] {
        position: fixed !important;
        top: 20px !important;
        right: 20px !important;
        z-index: 999999 !important;
    }
    
    /* Make the button look like a neat, clickable box */
    div[data-testid="stPopover"] button {
        border: 2px solid #4CAF50 !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
        padding: 10px 20px !important;
        background-color: white !important;
        color: #4CAF50 !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
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

today = date.today()

# --- Streak Decay Logic ---
# Rule: If you don't get at least 1 full day within a span of 2 days, streak dies.
for sub in SUBJECTS:
    last_date = st.session_state.last_studied_date[sub]
    if last_date is not None:
        days_passed = (today - last_date).days
        if days_passed > 2:  # Streak shatters
            st.session_state.streaks[sub] = 0
            st.session_state.half_sessions[sub] = 0
            st.session_state.full_sessions[sub] = 0
            st.session_state.last_studied_date[sub] = None

# --- Main Empty Screen ---
st.title("Tim's Hub")
st.write("The page is clean! Click the **Study Tracker** box hovering at the top right.")

# Placeholder for the giant focus timer
timer_display = st.empty()

def run_timer(minutes, subject):
    total_seconds = minutes * 60
    for i in range(total_seconds, -1, -1):
        mins, secs = divmod(i, 60)
        # Giant, centered timer display
        timer_display.markdown(
            f"<h1 style='text-align: center; font-size: 80px;'>⏱️ {mins:02d}:{secs:02d}</h1>"
            f"<h3 style='text-align: center; color: gray;'>Focusing on {subject}...</h3>", 
            unsafe_allow_html=True
        )
        time.sleep(1)
    timer_display.empty()
    return True

# --- The Floating Popover wrapped in a container we can hide ---
ui_container = st.empty()

with ui_container.container():
    with st.popover("📚 Study Tracker"):
        st.write("### Your Subjects")
        
        for sub in SUBJECTS:
            # Check if requirements are met: 1 full OR 2 halves
            has_completed_today = (st.session_state.full_sessions[sub] >= 1) or (st.session_state.half_sessions[sub] >= 2)
            
            status_emoji = "✅" if has_completed_today else "⏳"
            streak_val = st.session_state.streaks[sub]
            
            with st.expander(f"{status_emoji} {sub} (Streak: {streak_val}d)"):
                # Disabled checkbox: completely unclickable by hand, only ticks automatically
                st.checkbox(
                    "Completed for today", 
                    value=has_completed_today, 
                    disabled=True, 
                    key=f"status_{sub}"
                )
                
                st.write(f"Progress: Full ({st.session_state.full_sessions[sub]}/1) | Half ({st.session_state.half_sessions[sub]}/2)")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("⏱️ Full (15m)", key=f"full_{sub}", use_container_width=True):
                        ui_container.empty() # instantly erases the entire menu to prevent cheating!
                        if run_timer(15, sub):
                            st.session_state.full_sessions[sub] += 1
                            if not has_completed_today and ((st.session_state.full_sessions[sub] >= 1) or (st.session_state.half_sessions[sub] >= 2)):
                                st.session_state.streaks[sub] += 1
                                st.session_state.last_studied_date[sub] = today
                            st.rerun() # Brings the menu back and updates the stats
                            
                with col2:
                    if st.button("⚡ Half (5m)", key=f"half_{sub}", use_container_width=True):
                        ui_container.empty() # instantly erases the entire menu to prevent cheating!
                        if run_timer(5, sub):
                            st.session_state.half_sessions[sub] += 1
                            if not has_completed_today and ((st.session_state.full_sessions[sub] >= 1) or (st.session_state.half_sessions[sub] >=
