import requests
import streamlit as st
import time
from datetime import date, datetime, timedelta

def get_sheet_key():
    return st.secrets["SHEETY_URL"].rstrip('/').split('/')[-1]

def save_to_sheety(item_name, value):
    url = st.secrets["SHEETY_URL"]
    sheet_key = get_sheet_key() 
    
    if "sheety_ids" not in st.session_state:
        st.session_state.sheety_ids = {}
        
    row_id = st.session_state.sheety_ids.get(item_name)
    save_val = str(value) 
    
    data = {sheet_key: {"item": item_name, "value": save_val}}
    
    try:
        if row_id:
            requests.put(f"{url}/{row_id}", json=data)
        else:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                json_data = response.json()
                ret_key = list(json_data.keys())[0]
                st.session_state.sheety_ids[item_name] = json_data[ret_key].get("id")
    except:
        pass

def load_from_sheety():
    url = st.secrets["SHEETY_URL"]
    st.session_state.sheety_ids = {} 
        
    try:
        response = requests.get(url)
        if response.status_code == 200:
            json_data = response.json()
            if json_data:
                first_key = list(json_data.keys())[0]
                data = json_data[first_key]
                for row in data:
                    st.session_state.sheety_ids[row["item"]] = row.get("id")
                    if row["item"] in st.session_state:
                        val_str = str(row.get("value", ""))
                        if val_str == "True": val = True
                        elif val_str == "False": val = False
                        elif val_str == "None": val = None
                        elif val_str.isdigit(): val = int(val_str)
                        elif val_str.startswith("{") or val_str.startswith("["):
                            try: val = eval(val_str)
                            except: val = val_str
                        else:
                            val = val_str
                        st.session_state[row["item"]] = val
    except:
        pass

# --- Page Config ---
st.set_page_config(page_title="Study Tracker", page_icon="📚", layout="centered")

# --- The Brute Force White Bar ---
brute_force_bar = """
    <style>
    /* Forcefully hides the top header menu completely */
    [data-testid="stHeader"] {display: none !important;}
    
    /* The giant white box to cover the bottom footer */
    .cover-up {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 60px; /* Makes the bar 60 pixels tall. Increase if it doesn't cover enough */
        background-color: white; /* Matches the default app background */
        z-index: 999999; /* Forces it to sit on top of everything else */
    }
    </style>
    <div class="cover-up"></div>
"""
st.markdown(brute_force_bar, unsafe_allow_html=True)
# --- Core Data Setup ---
SUBJECTS = [
    "Chinese", "English", "Math", "History", 
    "Literature", "Geography", "Life Science", "Physical Science"
]

# 1. State Initialization
for key in ["streaks", "half_sessions", "full_sessions"]:
    if key not in st.session_state: st.session_state[key] = {sub: 0 for sub in SUBJECTS}

if "last_studied_date" not in st.session_state: st.session_state.last_studied_date = {sub: None for sub in SUBJECTS}
if "jp_streak" not in st.session_state: st.session_state.jp_streak = 0
if "jp_tasks" not in st.session_state: st.session_state.jp_tasks = {"Duolingo": False, "Jgrammar": False, "Kanji Dojo": False}
if "jp_completed_today" not in st.session_state: st.session_state.jp_completed_today = False
if "jp_last_date" not in st.session_state: st.session_state.jp_last_date = None
if "piano_count" not in st.session_state: st.session_state.piano_count = 0
if "piano_last_date" not in st.session_state: st.session_state.piano_last_date = None
if "piano_week" not in st.session_state: st.session_state.piano_week = date.today().isocalendar()[1]
if "workout_total" not in st.session_state: st.session_state.workout_total = 0
if "workout_last_date" not in st.session_state: st.session_state.workout_last_date = None
if "exams" not in st.session_state: st.session_state.exams = []
if "courseworks" not in st.session_state: st.session_state.courseworks = []
if "homework" not in st.session_state: st.session_state.homework = []
if "wash_total" not in st.session_state: st.session_state.wash_total = 0
if "sunblock_total" not in st.session_state: st.session_state.sunblock_total = 0
if "wash_day_done" not in st.session_state: st.session_state.wash_day_done = False
if "wash_night_done" not in st.session_state: st.session_state.wash_night_done = False
if "sunblock_done" not in st.session_state: st.session_state.sunblock_done = False
if "pack_bag_done" not in st.session_state: st.session_state.pack_bag_done = False
if "habits_last_date" not in st.session_state: st.session_state.habits_last_date = None
if "bible_chapters" not in st.session_state: st.session_state.bible_chapters = 0
if "bible_verses" not in st.session_state: st.session_state.bible_verses = 0
if "bible_days" not in st.session_state: st.session_state.bible_days = 0
if "bible_last_date" not in st.session_state: st.session_state.bible_last_date = None
if "timer_active" not in st.session_state: st.session_state.timer_active = False
if "timer_end_time" not in st.session_state: st.session_state.timer_end_time = None
if "timer_subject" not in st.session_state: st.session_state.timer_subject = None
if "timer_type" not in st.session_state: st.session_state.timer_type = None

# LOAD MEMORY ONCE PER REFRESH
if "memory_loaded" not in st.session_state:
    load_from_sheety()
    st.session_state.memory_loaded = True

today = date.today()
today_str = str(today)

# --- Background Logic Updates ---

# A. Subject Streak Decay
for sub in SUBJECTS:
    last_date_str = st.session_state.last_studied_date[sub]
    if last_date_str and last_date_str != "None":
        try:
            last_date_obj = datetime.strptime(last_date_str, "%Y-%m-%d").date()
            if (today - last_date_obj).days > 2:  
                st.session_state.streaks[sub] = 0
                st.session_state.half_sessions[sub] = 0
                st.session_state.full_sessions[sub] = 0
                st.session_state.last_studied_date[sub] = None
                save_to_sheety("streaks", st.session_state.streaks)
                save_to_sheety("half_sessions", st.session_state.half_sessions)
                save_to_sheety("full_sessions", st.session_state.full_sessions)
                save_to_sheety("last_studied_date", st.session_state.last_studied_date)
        except:
            pass

# B. Japanese Streak Decay
if st.session_state.jp_last_date and st.session_state.jp_last_date != "None":
    try:
        jp_last_obj = datetime.strptime(st.session_state.jp_last_date, "%Y-%m-%d").date()
        if (today - jp_last_obj).days > 2:
            st.session_state.jp_streak = 0
            st.session_state.jp_tasks = {"Duolingo": False, "Jgrammar": False, "Kanji Dojo": False}
            st.session_state.jp_completed_today = False
            st.session_state.jp_last_date = None
            save_to_sheety("jp_streak", st.session_state.jp_streak)
            save_to_sheety("jp_tasks", st.session_state.jp_tasks)
            save_to_sheety("jp_completed_today", st.session_state.jp_completed_today)
            save_to_sheety("jp_last_date", st.session_state.jp_last_date)
    except:
        pass

# C. Piano Weekly Reset
current_week = today.isocalendar()[1]
if st.session_state.piano_week != current_week:
    st.session_state.piano_week = current_week
    st.session_state.piano_count = 0 
    save_to_sheety("piano_week", st.session_state.piano_week)
    save_to_sheety("piano_count", st.session_state.piano_count)

# D. Habits Daily Reset
if st.session_state.habits_last_date != today_str:
    st.session_state.wash_day_done = False
    st.session_state.wash_night_done = False
    st.session_state.sunblock_done = False
    st.session_state.pack_bag_done = False
    st.session_state.habits_last_date = today_str
    save_to_sheety("wash_day_done", False)
    save_to_sheety("wash_night_done", False)
    save_to_sheety("sunblock_done", False)
    save_to_sheety("pack_bag_done", False)
    save_to_sheety("habits_last_date", today_str)

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
        st.session_state.last_studied_date[sub] = today_str
        
    st.session_state.timer_active = False

    save_to_sheety("full_sessions", st.session_state.full_sessions)
    save_to_sheety("half_sessions", st.session_state.half_sessions)
    save_to_sheety("streaks", st.session_state.streaks)
    save_to_sheety("last_studied_date", st.session_state.last_studied_date)
    save_to_sheety("timer_active", st.session_state.timer_active)
    st.rerun()

# --- Main UI Menu ---
if not st.session_state.timer_active:
    
    col1, col2, col3, col4 = st.columns(4)
    
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
            duo = st.checkbox("Duolingo", value=st.session_state.jp_tasks.get("Duolingo", False), disabled=st.session_state.jp_completed_today)
            jgram = st.checkbox("Jgrammar", value=st.session_state.jp_tasks.get("Jgrammar", False), disabled=st.session_state.jp_completed_today)
            kanji = st.checkbox("Kanji Dojo", value=st.session_state.jp_tasks.get("Kanji Dojo", False), disabled=st.session_state.jp_completed_today)

            if not st.session_state.jp_completed_today:
                if duo and jgram and kanji:
                    st.session_state.jp_completed_today = True
                    st.session_state.jp_streak += 1
                    st.session_state.jp_last_date = today_str
                    st.session_state.jp_tasks = {"Duolingo": True, "Jgrammar": True, "Kanji Dojo": True}
                    save_to_sheety("jp_completed_today", True)
                    save_to_sheety("jp_streak", st.session_state.jp_streak)
                    save_to_sheety("jp_last_date", today_str)
                    save_to_sheety("jp_tasks", st.session_state.jp_tasks)
                    st.rerun() 
                else:
                    new_tasks = {"Duolingo": duo, "Jgrammar": jgram, "Kanji Dojo": kanji}
                    if st.session_state.jp_tasks != new_tasks:
                        st.session_state.jp_tasks = new_tasks
                        save_to_sheety("jp_tasks", new_tasks)
                        st.rerun()

    with col3:
        with st.popover("💪 Activities"):
            st.write("### 🎹 Piano")
            piano_done_today = (st.session_state.piano_last_date == today_str)
            st.write(f"**Weekly Progress:** {st.session_state.piano_count} / 4 days")
            p_tick = st.checkbox("Practice Complete", value=piano_done_today, disabled=piano_done_today)
            if p_tick and not piano_done_today:
                st.session_state.piano_count += 1
                st.session_state.piano_last_date = today_str
                save_to_sheety("piano_count", st.session_state.piano_count)
                save_to_sheety("piano_last_date", today_str)
                st.rerun()
                
            st.divider()
            
            st.write("### 🏋️ Workout")
            st.write(f"**Total Lifetime Days:** {st.session_state.workout_total}")
            workout_done_today = (st.session_state.workout_last_date == today_str)
            
            days_since_workout = 999
            if st.session_state.workout_last_date and st.session_state.workout_last_date != "None":
                try:
                    last_w_date = datetime.strptime(st.session_state.workout_last_date, "%Y-%m-%d").date()
                    days_since_workout = (today - last_w_date).days
                except: pass
            
            workout_disabled = workout_done_today or (days_since_workout == 1)
            if days_since_workout == 1 and not workout_done_today:
                st.caption("⏳ Rest Day! Checkbox will unlock tomorrow.")
                
            w_tick = st.checkbox("Workout Complete", value=workout_done_today, disabled=workout_disabled)
            if w_tick and not workout_done_today:
                st.session_state.workout_total += 1
                st.session_state.workout_last_date = today_str
                save_to_sheety("workout_total", st.session_state.workout_total)
                save_to_sheety("workout_last_date", today_str)
                st.rerun()

    with col4:
        with st.popover("🌅 Routines"):
            st.write("### 🧼 Wash Face")
            st.write(f"**Total Washes:** {st.session_state.wash_total}")
            st.write(f"**Sunblock Days:** {st.session_state.sunblock_total}")
            
            w_day = st.checkbox("Morning Wash", value=st.session_state.wash_day_done, disabled=st.session_state.wash_day_done)
            if w_day and not st.session_state.wash_day_done:
                st.session_state.wash_total += 1
                st.session_state.wash_day_done = True
                save_to_sheety("wash_total", st.session_state.wash_total)
                save_to_sheety("wash_day_done", True)
                st.rerun()
                
            w_night = st.checkbox("Night Wash", value=st.session_state.wash_night_done, disabled=st.session_state.wash_night_done)
            if w_night and not st.session_state.wash_night_done:
                st.session_state.wash_total += 1
                st.session_state.wash_night_done = True
                save_to_sheety("wash_total", st.session_state.wash_total)
                save_to_sheety("wash_night_done", True)
                st.rerun()
                
            s_block = st.checkbox("Put Sunblock Today", value=st.session_state.sunblock_done, disabled=st.session_state.sunblock_done)
            if s_block and not st.session_state.sunblock_done:
                st.session_state.sunblock_total += 1
                st.session_state.sunblock_done = True
                save_to_sheety("sunblock_total", st.session_state.sunblock_total)
                save_to_sheety("sunblock_done", True)
                st.rerun()
                
            st.divider()
            
            st.write("### 🎒 Pack Bag")
            p_bag = st.checkbox("Bag Packed", value=st.session_state.pack_bag_done, disabled=st.session_state.pack_bag_done)
            if p_bag and not st.session_state.pack_bag_done:
                st.session_state.pack_bag_done = True
                save_to_sheety("pack_bag_done", True)
                st.rerun()
                
            st.divider()
            
            st.write("### 📖 Bible")
            st.write(f"**Days Read:** {st.session_state.bible_days} | **Ch:** {st.session_state.bible_chapters} | **V:** {st.session_state.bible_verses}")
            bible_done_today = (st.session_state.bible_last_date == today_str)
            
            if not bible_done_today:
                st.write("What did you read today?")
                b_col1, b_col2 = st.columns(2)
                with b_col1:
                    if st.button("1 Chapter", use_container_width=True):
                        st.session_state.bible_chapters += 1
                        st.session_state.bible_days += 1
                        st.session_state.bible_last_date = today_str
                        save_to_sheety("bible_chapters", st.session_state.bible_chapters)
                        save_to_sheety("bible_days", st.session_state.bible_days)
                        save_to_sheety("bible_last_date", today_str)
                        st.rerun()
                with b_col2:
                    if st.button("1 Verse", use_container_width=True):
                        st.session_state.bible_verses += 1
                        st.session_state.bible_days += 1
                        st.session_state.bible_last_date = today_str
                        save_to_sheety("bible_verses", st.session_state.bible_verses)
                        save_to_sheety("bible_days", st.session_state.bible_days)
                        save_to_sheety("bible_last_date", today_str)
                        st.rerun()
            else:
                st.success("✅ Completed for today!")

    st.write("---")
    
    # --- Bottom Section 1: EXAMS ---
    st.write("### 📝 Upcoming Exams")
    with st.container(border=True):
        if len(st.session_state.exams) == 0:
            st.caption("No exams added yet. You're clear!")
            
        for i, exam in enumerate(st.session_state.exams):
            try:
                formatted_date = datetime.strptime(exam["date"], "%Y-%m-%d").strftime("%d %B %Y")
                exam_date_obj = datetime.strptime(exam["date"], "%Y-%m-%d").date()
            except:
                formatted_date = str(exam["date"])
                exam_date_obj = today
                
            row_col1, row_col2 = st.columns([3, 1])
            with row_col1:
                if exam["score"] is not None:
                    st.write(f"**{exam['subject']}** — {formatted_date} ✅ **{exam['score']}%**")
                else:
                    st.write(f"**{exam['subject']}** — {formatted_date}")
            
            with row_col2:
                if exam["score"] is None and today >= exam_date_obj:
                    with st.popover("✅ Enter Result"):
                        st.write(f"Enter score for {exam['subject']}")
                        score_val = st.number_input("Percentage (%)", min_value=0.0, max_value=100.0, step=0.1, key=f"score_input_{i}")
                        if st.button("Save Result", key=f"save_score_{i}"):
                            st.session_state.exams[i]["score"] = score_val
                            save_to_sheety("exams", st.session_state.exams)
                            st.rerun()

        with st.popover("➕ Add New Exam"):
            new_sub = st.text_input("Exam Subject", placeholder="e.g., Express Math")
            new_date = st.date_input("Exam Date", min_value=today)
            btn1, btn2 = st.columns(2)
            with btn1:
                if st.button("Done", key="exam_add_done", use_container_width=True):
                    if new_sub:
                        st.session_state.exams.append({"subject": new_sub, "date": str(new_date), "score": None})
                        save_to_sheety("exams", st.session_state.exams)
                        st.rerun()
            with btn2:
                if st.button("Cancel", key="exam_add_cancel", use_container_width=True):
                    st.rerun()

    # --- Bottom Section 2: COURSEWORK ---
    st.write("### 📘 Upcoming Coursework")
    with st.container(border=True):
        if len(st.session_state.courseworks) == 0:
            st.caption("No coursework added yet. Enjoy your free time!")
            
        for i, cw in enumerate(st.session_state.courseworks):
            try:
                formatted_date = datetime.strptime(cw["due_date"], "%Y-%m-%d").strftime("%d %B %Y")
            except:
                formatted_date = str(cw["due_date"])
                
            row_col1, row_col2, row_col3 = st.columns([0.5, 3, 1.5])
            with row_col1:
                is_done = st.checkbox("Done", value=cw["completed"], key=f"cw_check_{i}", label_visibility="collapsed")
                if is_done != cw["completed"]:
                    st.session_state.courseworks[i]["completed"] = is_done
                    save_to_sheety("courseworks", st.session_state.courseworks)
                    st.rerun()
                    
            with row_col2:
                if cw["score"] is not None:
                    st.write(f"**{cw['subject']}** — Due: {formatted_date} ✅ **{cw['score']}%**")
                else:
                    st.write(f"**{cw['subject']}** — Due: {formatted_date}")
            
            with row_col3:
                if cw["completed"] and cw["score"] is None:
                    with st.popover("✅ Enter Result"):
                        st.write(f"Enter score for {cw['subject']}")
                        score_val = st.number_input("Percentage (%)", min_value=0.0, max_value=100.0, step=0.1, key=f"cw_score_input_{i}")
                        if st.button("Save Result", key=f"save_cw_score_{i}"):
                            st.session_state.courseworks[i]["score"] = score_val
                            save_to_sheety("courseworks", st.session_state.courseworks)
                            st.rerun()

        with st.popover("➕ Add New Coursework"):
            new_cw_sub = st.text_input("Coursework Subject", placeholder="e.g., Geography Project", key="new_cw_sub")
            new_cw_date = st.date_input("Due Date", min_value=today, key="new_cw_date")
            btn1, btn2 = st.columns(2)
            with btn1:
                if st.button("Done", key="cw_add_done", use_container_width=True):
                    if new_cw_sub:
                        st.session_state.courseworks.append({"subject": new_cw_sub, "due_date": str(new_cw_date), "completed": False, "score": None})
                        save_to_sheety("courseworks", st.session_state.courseworks)
                        st.rerun()
            with btn2:
                if st.button("Cancel", key="cw_add_cancel", use_container_width=True):
                    st.rerun()

    # --- Bottom Section 3: HOMEWORK ---
    st.write("### 🎒 Homework Tracker")
    with st.container(border=True):
        if len(st.session_state.homework) == 0:
            st.caption("No homework! You are completely free.")
            
        for i, hw in enumerate(st.session_state.homework):
            if hw["due_date"] == today_str:
                date_display = "🔥 **DUE TODAY**"
            else:
                try:
                    date_display = f"Due: {datetime.strptime(hw['due_date'], '%Y-%m-%d').strftime('%d %B %Y')}"
                except:
                    date_display = f"Due: {hw['due_date']}"
                
            row_col1, row_col2 = st.columns([0.5, 4.5])
            
            with row_col1:
                is_done = st.checkbox("Done", value=hw["completed"], key=f"hw_check_{i}", label_visibility="collapsed")
                if is_done and not hw["completed"]:
                    if not hw["keep"]:
                        st.session_state.homework.pop(i) 
                        save_to_sheety("homework", st.session_state.homework)
                        st.rerun()
                    else:
                        st.session_state.homework[i]["completed"] = True
                        save_to_sheety("homework", st.session_state.homework)
                        st.rerun()
                elif not is_done and hw["completed"]:
                    st.session_state.homework[i]["completed"] = False
                    save_to_sheety("homework", st.session_state.homework)
                    st.rerun()
                    
            with row_col2:
                if hw["completed"]:
                    st.write(f"~~**{hw['subject']}**: {hw['task']} — {date_display}~~ ✅")
                else:
                    st.write(f"**{hw['subject']}**: {hw['task']} — {date_display}")

        with st.popover("➕ Add New Homework"):
            hw_sub = st.text_input("Subject", placeholder="e.g., Literature", key="new_hw_sub")
            hw_task = st.text_area("What do you need to do?", placeholder="e.g., Finish character mindmap", key="new_hw_task")
            due_today = st.checkbox("🔥 Due Today!", key="hw_due_today")
            
            if due_today:
                hw_date_str = today_str
            else:
                hw_date = st.date_input("Due Date", min_value=today, key="new_hw_date")
                hw_date_str = str(hw_date)
                
            hw_keep = st.checkbox("Keep assignment on board after completed", key="hw_keep")
            
            btn1, btn2 = st.columns(2)
            with btn1:
                if st.button("Done", key="hw_add_done2", use_container_width=True):
                    if hw_sub and hw_task:
                        st.session_state.homework.append({
                            "subject": hw_sub,
                            "task": hw_task,
                            "due_date": hw_date_str,
                            "keep": hw_keep,
                            "completed": False
                        })
                        save_to_sheety("homework", st.session_state.homework)
                        st.rerun()
            with btn2:
                if st.button("Cancel", key="hw_add_cancel2", use_container_width=True):
                    st.rerun()
