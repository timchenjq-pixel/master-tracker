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

# State Initialization: Subjects
for key in ["streaks", "half_sessions", "full_sessions"]:
    if key not in st.session_state:
        st.session_state[key] = {sub: 0 for sub in SUBJECTS}

if "last_studied_date" not in st.session_state:
    st.session_state.last_studied_date = {sub: None for sub in SUBJECTS}

# State Initialization: Japanese Box
if "jp_streak" not in st.session_state:
    st.session_state.jp_streak = 0
if "jp_tasks" not in st.session_state:
    st.session_state.jp_tasks = {"Duolingo": False, "Jgrammar": False, "Kanji Dojo": False}
if "jp_completed_today" not in st.session_state:
    st.session_state.jp_completed_today = False
if "jp_last_date" not in st.session_state:
    st.session_state.jp_last_date = None

# Timer Memory State
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
# Normal Subjects
for sub in SUBJECTS:
    last_date = st.session_state.last_studied_date[sub]
    if last_date is not None:
        days_passed = (today - last_date).days
        if days_passed > 2:  
            st.session_state.streaks[sub] = 0
            st.session_state.half_sessions[sub] = 0
            st.session_state.full_sessions[sub] = 0
            st.session_state.last_studied_date[sub] = None

# Japanese Streak Decay (Miss 2 days = Streak dies)
if st.session_state.jp_last_date is not None:
    if (today - st.session_state.jp_last_date).days > 2:
        st.session_state.jp_streak = 0
        st.session_state.jp_tasks = {"Duolingo": False, "Jgrammar": False, "Kanji Dojo": False}
        st.session_state.jp_completed_today = False
        st.session_state.jp_last_date = None

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
    
    # Place the boxes side-by-side to keep the screen clean
    col1, col2 = st.columns(2)
    
    with col1:
        with st.popover("📚
