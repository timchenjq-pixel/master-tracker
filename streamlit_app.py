import streamlit as st
import time
from datetime import date

# --- Setup & Configuration ---
# This forces the layout to be centered and narrow instead of wide!
st.set_page_config(page_title="Tim's Dashboard", page_icon="📚", layout="centered")

# Custom CSS to make it look less boring and style the blocks
st.markdown("""
    <style>
    .block-container { max-width: 600px; padding-top: 2rem; }
    .stCheckbox { margin-bottom: -10px; }
    </style>
""", unsafe_allow_html=True)

# List of subjects
SUBJECTS = [
    "Chinese", "English", "Math", "History", 
    "Literature", "Geography", "Life Science", "Physical Science"
]

# Initialize Session States
if "streaks" not in st.session_state:
    st.session_state.streaks = {sub: 0 for sub in SUBJECTS}
if "completed_today" not in st.session_state:
    st.session_state.completed_today = {sub: False for sub in SUBJECTS}

# --- Main UI ---
st.title("⚡ Tim's Master Hub")
st.caption("Express Track Edition • One block at a time.")
st.write("---")

# --- Timer Functions ---
def run_timer(minutes):
    if st.session_state.get("test_mode", False):
        st.success("Test Mode: Timer bypassed!")
        return True
        
    placeholder = st.empty()
    total_seconds = minutes * 60
    for i in range(total_seconds, -1, -1):
        mins, secs = divmod(i, 60)
        placeholder.metric("Time Remaining", f"{mins:02d}:{secs:02d}")
        time.sleep(1)
    placeholder.empty()
    return True

# --- Sidebar ---
st.sidebar.header("Developer Settings")
st.session_state.test_mode = st.sidebar.checkbox("Enable Test Mode")

# --- Subject Display (Confined Boxes) ---
for subject in SUBJECTS:
    # Creating a neat drop-down container box for each subject
    with st.expander(f"📘 {subject} — Streak: {st.session_state.streaks[subject]} days"):
        
        # Checkbox replaces the clunky "last studied" text
        is_done = st.checkbox("Mark as completed for today", key=f"check_{subject}", value=st.session_state.completed_today[subject])
        
        if is_done and not st.session_state.completed_today[subject]:
            st.session_state.streaks[subject] += 1
            st.session_state.completed_today[subject] = True
            st.rerun()
        elif not is_done and st.session_state.completed_today[subject]:
            st.session_state.streaks[subject] = max(0, st.session_state.streaks[subject] - 1)
            st.session_state.completed_today[subject] = False
            st.rerun()
            
        st.write("Or run a timed session:")
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"⏱️ 15 Min", key=f"full_{subject}", use_container_width=True):
                if run_timer(15):
                    if not st.session_state.completed_today[subject]:
                        st.session_state.streaks[subject] += 1
                        st.session_state.completed_today[subject] = True
                        st.rerun()
        with col2:
            if st.button(f"⚡ 5 Min", key=f"half_{subject}", use_container_width=True):
                if run_timer(5):
                    if not st.session_state.completed_today[subject]:
                        st.session_state.streaks[subject] += 1
                        st.session_state.completed_today[subject] = True
                        st.rerun()
