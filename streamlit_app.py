import streamlit as st
import time
from datetime import date, datetime, timedelta

# --- Page Config ---
st.set_page_config(page_title="Study Tracker", page_icon="📚", layout="centered")

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
        timer_display.empty()
        
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
        
    st.session_state.timer_active = False
    st.rerun()

# --- Main UI Menu ---
if not st.session_state.timer_active:
    st.title("📚 Express Track Dashboard")
    st.write("Click any subject box below to open your timers.")
    
    for sub in SUBJECTS:
        has_completed_today = (st.session_state.full_sessions[sub] >= 1) or (st.session_state.half_sessions[sub] >= 2)
        status_emoji = "✅" if has_completed_today else "⏳"
        streak_val = st.session_state.streaks[sub]
        
        # Native Streamlit expander boxes - perfectly safe and bug-free
        with st.expander(f"{status_emoji} {sub} (Streak: {streak_val}d)"):
            st.checkbox("Completed for today", value=has_completed_today, disabled=True, key=f"status_{sub}")
            st.write(f"Progress: Full ({st.session_state.full_sessions[sub]}/1) | Half ({st.session_state.half_sessions[sub]}/2)")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⏱️ Full (15m)", key=f"full_{sub}", use_container_width=True):
                    st.session_state.timer_active = True
                    st.session_state.timer_end_time = datetime.now() + timedelta(minutes=15)
                    st.session_state.timer_subject = sub
                    st.session_state.timer_type = "full"
                    st.rerun() 
                        
            with col2:
                if st.button("⚡ Half (5m)", key=f"half_{sub}", use_container_width=True):
                    st.session_state.timer_active = True
                    st.session_state.timer_end_time = datetime.now() + timedelta(minutes=5)
                    st.session_state.timer_subject = sub
                    st.session_state.timer_type = "half"
                    st.rerun()
