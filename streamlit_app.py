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
if "piano_week" not in st.session_state: st.session_state.piano_week = date.today().isocalendar()[1]

if "workout_total" not in st.session_state: st.session_state.workout_total = 0
if "workout_last_date" not in st.session_state: st.session_state.workout_last_date = None

# 4. State Initialization: Exams (New!)
if "exams" not in st.session_state: 
    st.session_state.exams = [] # Stores a list of dictionaries

# 5. Timer Memory State
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
    st.session_state.piano_count = 0 

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
    
    # --- Top Row: Daily Trackers ---
    col1, col2, col3 = st.columns(3)
    
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

    with col3:
        with st.popover("💪 Activities"):
            st.write("### 🎹 Piano")
            piano_done_today = (st.session_state.piano_last_date == today)
            st.write(f"**Weekly Progress:** {st.session_state.piano_count} / 4 days")
            p_tick = st.checkbox("Practice Complete", value=piano_done_today, disabled=piano_done_today)
            if p_tick and not piano_done_today:
                st.session_state.piano_count += 1
                st.session_state.piano_last_date = today
                st.rerun()
                
            st.divider()
            
            st.write("### 🏋️ Workout")
            st.write(f"**Total Lifetime Days:** {st.session_state.workout_total}")
            workout_done_today = (st.session_state.workout_last_date == today)
            days_since_workout = (today - st.session_state.workout_last_date).days if st.session_state.workout_last_date else 999
            
            workout_disabled = workout_done_today or (days_since_workout == 1)
            if days_since_workout == 1 and not workout_done_today:
                st.caption("⏳ Rest Day! Checkbox will unlock tomorrow.")
                
            w_tick = st.checkbox("Workout Complete", value=workout_done_today, disabled=workout_disabled)
            if w_tick and not workout_done_today:
                st.session_state.workout_total += 1
                st.session_state.workout_last_date = today
                st.rerun()

    st.write("---")
    
    # --- Bottom Section: EXAMS ---
    st.write("### 📝 Upcoming Exams")
    
    with st.container(border=True):
        # 1. Show existing exams dynamically
        if len(st.session_state.exams) == 0:
            st.caption("No exams added yet. You're clear!")
            
        for i, exam in enumerate(st.session_state.exams):
            # Format the date exactly how you asked: "29 July 2026"
            formatted_date = exam["date"].strftime("%d %B %Y")
            
            row_col1, row_col2 = st.columns([3, 1])
            with row_col1:
                if exam["score"] is not None:
                    # If score is entered, show the green tick and the percentage!
                    st.write(f"**{exam['subject']}** — {formatted_date} ✅ **{exam['score']}%**")
                else:
                    st.write(f"**{exam['subject']}** — {formatted_date}")
            
            with row_col2:
                # If the current date matches or passes the exam date, and no score exists yet
                if exam["score"] is None and today >= exam["date"]:
                    with st.popover("✅ Enter Result"):
                        st.write(f"Enter score for {exam['subject']}")
                        score_val = st.number_input("Percentage (%)", min_value=0.0, max_value=100.0, step=0.1, key=f"score_input_{i}")
                        
                        if st.button("Save Result", key=f"save_score_{i}"):
                            st.session_state.exams[i]["score"] = score_val
                            st.rerun()

        # 2. The button to add new ones
        with st.popover("➕ Add New Exam"):
            new_sub = st.text_input("Exam Subject", placeholder="e.g., Express Math")
            new_date = st.date_input("Exam Date", min_value=today)
            
            btn1, btn2 = st.columns(2)
            with btn1:
                if st.button("Done", use_container_width=True):
                    if new_sub:
                        st.session_state.exams.append({
                            "subject": new_sub,
                            "date": new_date,
                            "score": None
                        })
                        st.rerun()
            with btn2:
                if st.button("Cancel", use_container_width=True):
                    st.rerun() # Refreshing the page safely closes the popover naturally
                    # --- Bottom Section 2: COURSEWORK ---
    if "courseworks" not in st.session_state:
        st.session_state.courseworks = []

    st.write("### 📘 Upcoming Coursework")
    
    with st.container(border=True):
        if len(st.session_state.courseworks) == 0:
            st.caption("No coursework added yet. Enjoy your free time!")
            
        for i, cw in enumerate(st.session_state.courseworks):
            # Formats the calendar date perfectly
            formatted_date = cw["due_date"].strftime("%d %B %Y")
            
            # Using 3 columns so the checkbox sits neatly on the left
            row_col1, row_col2, row_col3 = st.columns([0.5, 3, 1.5])
            
            with row_col1:
                # The completion checkbox
                is_done = st.checkbox("Done", value=cw["completed"], key=f"cw_check_{i}", label_visibility="collapsed")
                if is_done != cw["completed"]:
                    st.session_state.courseworks[i]["completed"] = is_done
                    st.rerun()
                    
            with row_col2:
                if cw["score"] is not None:
                    st.write(f"**{cw['subject']}** — Due: {formatted_date} ✅ **{cw['score']}%**")
                else:
                    st.write(f"**{cw['subject']}** — Due: {formatted_date}")
            
            with row_col3:
                # STRICT LOCK: Score button ONLY appears if the checkbox is ticked!
                if cw["completed"] and cw["score"] is None:
                    with st.popover("✅ Enter Result"):
                        st.write(f"Enter score for {cw['subject']}")
                        score_val = st.number_input("Percentage (%)", min_value=0.0, max_value=100.0, step=0.1, key=f"cw_score_input_{i}")
                        
                        if st.button("Save Result", key=f"save_cw_score_{i}"):
                            st.session_state.courseworks[i]["score"] = score_val
                            st.rerun()

        with st.popover("➕ Add New Coursework"):
            new_cw_sub = st.text_input("Coursework Subject", placeholder="e.g., Geography Project", key="new_cw_sub")
            new_cw_date = st.date_input("Due Date", min_value=today, key="new_cw_date")
            
            btn1, btn2 = st.columns(2)
            with btn1:
                if st.button("Done", key="cw_add_done", use_container_width=True):
                    if new_cw_sub:
                        st.session_state.courseworks.append({
                            "subject": new_cw_sub,
                            "due_date": new_cw_date,
                            "completed": False,
                            "score": None
                        })
                        st.rerun()
            with btn2:
                if st.button("Cancel", key="cw_add_cancel", use_container_width=True):
                    st.rerun()
# --- Bottom Section 3: HOMEWORK ---
    if "homework" not in st.session_state:
        st.session_state.homework = []

    st.write("### 🎒 Homework Tracker")
    
    with st.container(border=True):
        if len(st.session_state.homework) == 0:
            st.caption("No homework! You are completely free.")
            
        for i, hw in enumerate(st.session_state.homework):
            # Creates a bold red warning if it's due today
            if hw["due_date"] == today:
                date_display = "🔥 **DUE TODAY**"
            else:
                date_display = f"Due: {hw['due_date'].strftime('%d %B %Y')}"
                
            row_col1, row_col2 = st.columns([0.5, 4.5])
            
            with row_col1:
                is_done = st.checkbox("Done", value=hw["completed"], key=f"hw_check_{i}", label_visibility="collapsed")
                
                # Auto-delete logic
                if is_done and not hw["completed"]:
                    if not hw["keep"]:
                        st.session_state.homework.pop(i) # Instantly vanishes from the board!
                        st.rerun()
                    else:
                        st.session_state.homework[i]["completed"] = True
                        st.rerun()
                elif not is_done and hw["completed"]:
                    st.session_state.homework[i]["completed"] = False
                    st.rerun()
                    
            with row_col2:
                # Adds a strikethrough effect if you kept it on the board and finished it
                if hw["completed"]:
                    st.write(f"~~**{hw['subject']}**: {hw['task']} — {date_display}~~ ✅")
                else:
                    st.write(f"**{hw['subject']}**: {hw['task']} — {date_display}")

        with st.popover("➕ Add New Homework"):
            hw_sub = st.text_input("Subject", placeholder="e.g., Literature", key="new_hw_sub")
            hw_task = st.text_area("What do you need to do?", placeholder="e.g., Finish character mindmap", key="new_hw_task")
            
            # The instant "Due Today" shortcut
            due_today = st.checkbox("🔥 Due Today!", key="hw_due_today")
            if due_today:
                hw_date = today
            else:
                hw_date = st.date_input("Due Date", min_value=today, key="new_hw_date")
                
            hw_keep = st.checkbox("Keep assignment on board after completed", key="hw_keep")
            
            btn1, btn2 = st.columns(2)
            with btn1:
                if st.button("Done", key="hw_add_done", use_container_width=True):
                    if hw_sub and hw_task:
                        st.session_state.homework.append({
                            "subject": hw_sub,
                            "task": hw_task,
                            "due_date": hw_date,
                            "keep": hw_keep,
                            "completed": False
                        })
                        st.rerun()
            with btn2:
                if st.button("Cancel", key="hw_add_cancel", use_container_width=True):
                    st.rerun()
