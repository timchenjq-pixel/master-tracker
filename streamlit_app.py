import streamlit as st
import time
from datetime import date, datetime

# --- Page Config ---
st.set_page_config(page_title="Tim's Hub", page_icon="⚡", layout="wide")

# --- Premium Cyberpunk/Dark Glassmorphism Styling ---
st.markdown("""
    <style>
    /* Global Background Adjustments */
    .stApp {
        background: #0d0e15;
        color: #e2e8f0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Force UI into a Floating Top-Right Mini-Box */
    [data-testid="stVerticalBlock"] > div:has(.floating-hub) {
        position: fixed;
        top: 20px;
        right: 20px;
        width: 360px;
        z-index: 999999;
        background: rgba(22, 25, 41, 0.85);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }

    /* Target mobile screens to keep it responsive */
    @media (max-width: 768px) {
        [data-testid="stVerticalBlock"] > div:has(.floating-hub) {
            width: 90%;
            right: 5%;
            top: 15px;
        }
    }

    /* Style Headers and Expanders */
    .stExpander {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 10px !important;
        margin-bottom: 8px !important;
    }
    
    .stMarkdown h1 {
        font-size: 22px !important;
        background: linear-gradient(45deg, #ff7e5f, #feb47b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px !important;
    }
    </style>
    <div class="floating-hub"></div>
""", unsafe_allow_html=True)

# --- Core Data Setup ---
SUBJECTS = [
    "Chinese", "English", "Math", "History", 
    "Literature", "Geography", "Life Science", "Physical Science"
]

# State Initialization
if "streaks" not in st.session_state:
    st.session_state.streaks = {sub: 0 for sub in SUBJECTS}
if "half_sessions" not in st.session_state:
    st.session_state.half_sessions = {sub: 0 for sub in SUBJECTS}
if "full_sessions" not in st.session_state:
    st.session_state.full_sessions = {sub: 0 for sub in SUBJECTS}
if "last_studied_date" not in st.session_state:
    st.session_state.last_studied_date = {sub: None for sub in SUBJECTS}

today = date.today()

# --- Streak Decay Logic (Check if 2 days have passed since last study) ---
for sub in SUBJECTS:
    last_date = st.session_state.last_studied_date[sub]
    if last_date is not None:
        days_passed = (today - last_date).days
        if days_passed > 1:  # Missed more than 2 consecutive days
            st.session_state.streaks[sub] = 0
            st.session_state.half_sessions[sub] = 0
            st.session_state.full_sessions[sub] = 0
            st.session_state.last_studied_date[sub] = None

# --- UI Layout ---
st.title("⚡ Tim's Master Hub")
st.caption("Express Track Setup")
st.write("---")

def run_timer(minutes):
    placeholder = st.empty()
    total_seconds = minutes * 60
    for i in range(total_seconds, -1, -1):
        mins, secs = divmod(i, 60)
        placeholder.metric("Time Remaining", f"{mins:02d}:{secs:02d}")
        time.sleep(1)
    placeholder.empty()
    return True

# --- Subject Modular Blocks ---
for sub in SUBJECTS:
    # Check if requirements are met: 1 full OR 2 halves
    has_completed_today = (st.session_state.full_sessions[sub] >= 1) or (st.session_state.half_sessions[sub] >= 2)
    
    status_emoji = "🔥" if has_completed_today else "⏳"
    streak_val = st.session_state.streaks[sub]
    
    with st.expander(f"{status_emoji} {sub} (Streak: {streak_val}d)"):
        # The Checkbox is explicitly disabled so it cannot be ticked manually
        st.checkbox(
            "Completed for today", 
            value=has_completed_today, 
            disabled=True, 
            key=f"status_{sub}"
        )
        
        # Display session track progress info
        st.write(f"Progress: Full ({st.session_state.full_sessions[sub]}/1) | Half ({st.session_state.half_sessions[sub]}/2)")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⏱️ Full (15m)", key=f"full_btn_{sub}", use_container_width=True):
                if run_timer(15):
                    st.session_state.full_sessions[sub] += 1
                    if not has_completed_today and ((st.session_state.full_sessions[sub] == 1) or (st.session_state.half_sessions[sub] >= 2)):
                        st.session_state.streaks[sub] += 1
                        st.session_state.last_studied_date[sub] = today
                    st.rerun()
                    
        with col2:
            if st.button("⚡ Half (5m)", key=f"half_btn_{sub}", use_container_width=True):
                if run_timer(5):
                    st.session_state.half_sessions[sub] += 1
                    if not has_completed_today and ((st.session_state.full_sessions[sub] >= 1) or (st.session_state.half_sessions[sub] == 2)):
                        st.session_state.streaks[sub] += 1
                        st.session_state.last_studied_date[sub] = today
                    st.rerun()
