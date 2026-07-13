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

# 1. State Initialization: Subjects
for key in ["streaks", "half_sessions", "full_sessions"]:
    if key not in st.session_state:
        st.session_state[key] = {sub: 0 for sub in SUBJECTS}

if "last_studied_date" not in st.session_state:
    st.session_state.last_studied_date = {sub: None for sub in SUBJECTS}

# 2. State Initialization: Japanese Box
if "jp_streak" not in st.session_state: st.session_state.jp_streak = 0
if "jp_tasks" not in st.session_state: st.session_state.jp_tasks = {"Duolingo": False, "Jgrammar": False, "Kanji Dojo": False}
if "jp_completed_today" not in st.session_state: st.session_state.jp_completed_today = False
if "jp_last_date" not in st.session_state: st.session_state.jp_last_date = None

# 3. State Initialization: Activities (Piano & Workout)
if "piano_count" not in st.session_state: st.session_state.piano_count = 0
if "piano_last_date" not in st.session_state: st.session_state.piano_last_date = None
if "piano_week" not in st.session_state: st.session_state.piano_week = date.today().isocalendar()[1] # Tracks the current week number

if "workout_total" not in st.session_state: st.session_state.workout_total = 0
if "workout_last_date" not in st.session_state: st.session_state.workout_last_date = None

# 4. Timer Memory State
if "timer_active" not in st.session_state: st.session_state.timer_active = False
if "timer_end_time" not in st.session_state: st.session_state.timer_end_time = None
if "timer_subject" not in st.session_state: st.session_state.timer_subject = None
if "timer_type" not in st.session_state: st.session_state.timer_type = None

today = date.today()

# --- Background Logic Updates ---

# A. Subject Streak Decay
for sub in SUBJECTS:
    last_date = st.session_state.last_studied_date[sub]
    if last_date is not None:
        if (today - last_date).days > 2:  
            st.session_state.streaks[sub] = 0
            st.session_state.half_sessions[sub] = 0
            st.session_state.full_sessions[sub] = 0
            st.session_state.last_studied_date[sub] = None

# B. Japanese Streak Decay
if st.session_state.jp_last_date is not None:
    if (today - st.session_state.jp_last_date).days > 2:
        st.session_state.jp_streak = 0
        st.session_state.jp_tasks = {"Duolingo": False, "Jgrammar": False, "Kanji Dojo": False}
        st.session_state.jp_completed_today = False
        st.session_state.jp_last_date = None

# C. Piano Weekly Reset Logic
current_week = today.isocalendar()[1]
if st.session_state.piano_week != current_week:
    st.session_state.piano_week = current_week
    st.session_state.piano_count = 0 # Resets back to 0 at the start of a new week

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
    
    # We now have 3 columns for our 3 main boxes!
    col1, col2, col3 = st.columns(3)
    
    # BOX 1: MAIN SUBJECTS
    with col1:
        with st.popover("📚 Tracker"):
            for sub in SUBJECTS:
                has_completed_today = (st.session_state.full_sessions[sub] >= 1) or (st.session_state.half_sessions[sub] >= 2)
                status_emoji = "✅" if has_completed_today else "⏳"
                streak_val = st.session_state.streaks[sub]
                
                with st.expander(f"{status_emoji} {sub} (Streak: {streak_val}d)"):
                    st.checkbox("Completed for today", value=has_completed_today, disabled=True, key=f"status_{sub}")
                    st.write(f"Progress: Full ({st.session_state.full_sessions[sub]}/1) | Half ({st.session_state.half_sessions[sub]}/2)")
                    
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button("⏱️ Full (15m)", key=f"full_{sub}", use_container_width=True):
                            st.session_state.timer_active = True
                            st.session_state.timer_end_time = datetime.now() + timedelta(minutes=15)
                            st.session_state.timer_subject = sub
                            st.session_state.timer_type = "full"
                            st.rerun() 
                                
                    with btn_col2:
                        if st.button("⚡ Half (5m)", key=f"half_{sub}", use_container_width=True):
                            st.session_state.timer_active = True
                            st.session_state.timer_end_time = datetime.now() + timedelta(minutes=5)
                            st.session_state.timer_subject = sub
                            st.session_state.timer_type = "half"
                            st.rerun()

    # BOX 2: JAPANESE
    with col2:
        jp_label = "✅ Japanese (Done)" if st.session_state.jp_completed_today else "🎌 Japanese"
        with st.popover(jp_label):
            st.write(f"**Current Streak: {st.session_state.jp_streak} days**")
            
            duo = st.checkbox("Duolingo", value=st.session_state.jp_tasks["Duolingo"], disabled=st.session_state.jp_completed_today)
            jgram = st.checkbox("Jgrammar", value=st.session_state.jp_tasks["Jgrammar"], disabled=st.session_state.jp_completed_today)
            kanji = st.checkbox("Kanji Dojo", value=st.session_state.jp_tasks["Kanji Dojo"], disabled=st.session_state.jp_completed_today)

            if not st.session_state.jp_completed_today:
                if duo and jgram and kanji:
                    st.session_state.jp_completed_today = True
                    st.session_state.jp_streak += 1
                    st.session_state.jp_last_date = today
                    st.session_state.jp_tasks = {"Duolingo": True, "Jgrammar": True, "Kanji Dojo": True}
                    st.rerun() 
                else:
                    st.session_state.jp_tasks["Duolingo"] = duo
                    st.session_state.jp_tasks["Jgrammar"] = jgram
                    st.session_state.jp_tasks["Kanji Dojo"] = kanji

    # BOX 3: ACTIVITIES (New!)
    with col3:
        with st.popover("💪 Activities"):
            
            # --- PIANO SECTION ---
            st.write("### 🎹 Piano")
            piano_done_today = (st.session_state.piano_last_date == today)
            st.write(f"**Weekly Progress:** {st.session_state.piano_count} / 4 days")
            
            p_tick = st.checkbox("Practice Complete", value=piano_done_today, disabled=piano_done_today)
            if p_tick and not piano_done_today:
                st.session_state.piano_count += 1
                st.session_state.piano_last_date = today
                st.rerun()
                
            st.divider()
            
            # --- WORKOUT SECTION ---
            st.write("### 🏋️ Workout")
            st.write(f"**Total Lifetime Days:** {st.session_state.workout_total}")
            
            workout_done_today = (st.session_state.workout_last_date == today)
            days_since_workout = (today - st.session_state.workout_last_date).days if st.session_state.workout_last_date else 999
            
            # Disable checkbox if ticked today, OR if ticked yesterday (1 day ago)
            workout_disabled = workout_done_today or (days_since_workout == 1)
            
            if days_since_workout == 1 and not workout_done_today:
                st.caption("⏳ Rest Day! Checkbox will unlock tomorrow.")
                
            w_tick = st.checkbox("Workout Complete", value=workout_done_today, disabled=workout_disabled)
            if w_tick and not workout_done_today:
                st.session_state.workout_total += 1
                st.session_state.workout_last_date = today
                st.rerun()
