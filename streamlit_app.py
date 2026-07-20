import requests
import streamlit as st
import streamlit.components.v1 as components
from datetime import date, datetime, timedelta, timezone

def save_to_sheety(item_name, value):
    url = "https://script.google.com/macros/s/AKfycbx2P88HxjO6zhZsDbS99s-EFRBJHavA0yz5XddsrAaBXWufFdsOD3DJvcsOU2xH-mneqA/exec" 
    save_val = str(value) 
    data = {"data": {"item": item_name, "value": save_val}}
    try:
        requests.post(url, json=data)
    except:
        pass

def load_from_sheety():
    url = "https://script.google.com/macros/s/AKfycbx2P88HxjO6zhZsDbS99s-EFRBJHavA0yz5XddsrAaBXWufFdsOD3DJvcsOU2xH-mneqA/exec"
    try:
        headers = {"Cache-Control": "no-cache"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            json_data = response.json()
            data = json_data.get("sheet1", [])
            for row in data:
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
st.set_page_config(page_title="Master Tracker", layout="centered")

# --- Top Header Nuke ---
hide_header = """
    <style>
    [data-testid="stHeader"] {display: none !important;}
    </style>
"""
st.markdown(hide_header, unsafe_allow_html=True)

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
if "bible_chapters" not in st.session_state: st.session_state.bible_chapters = 0
if "bible_verses" not in st.session_state: st.session_state.bible_verses = 0
if "bible_days" not in st.session_state: st.session_state.bible_days = 0
if "bible_last_date" not in st.session_state: st.session_state.bible_last_date = None

if "timer_active" not in st.session_state: st.session_state.timer_active = False
if "timer_end_time" not in st.session_state: st.session_state.timer_end_time = 0.0
if "timer_subject" not in st.session_state: st.session_state.timer_subject = "None"
if "timer_type" not in st.session_state: st.session_state.timer_type = "None"

SG_TZ = timezone(timedelta(hours=8))
now_sg = datetime.now(SG_TZ)
today_str = str(now_sg.date())

# LOAD MEMORY
if "memory_loaded" not in st.session_state:
    load_from_sheety()
    st.session_state.memory_loaded = True

# --- MANUAL RESET BUTTON ---
if st.button("🌅 Start New Day (Manual Reset)"):
    for sub in SUBJECTS:
        st.session_state.full_sessions[sub] = 0
        st.session_state.half_sessions[sub] = 0
    st.session_state.jp_tasks = {"Duolingo": False, "Jgrammar": False, "Kanji Dojo": False}
    st.session_state.jp_completed_today = False
    st.session_state.wash_day_done = False
    st.session_state.wash_night_done = False
    st.session_state.sunblock_done = False
    st.session_state.pack_bag_done = False
    
    save_to_sheety("full_sessions", st.session_state.full_sessions)
    save_to_sheety("half_sessions", st.session_state.half_sessions)
    save_to_sheety("jp_tasks", st.session_state.jp_tasks)
    save_to_sheety("jp_completed_today", False)
    save_to_sheety("wash_day_done", False)
    save_to_sheety("wash_night_done", False)
    save_to_sheety("sunblock_done", False)
    save_to_sheety("pack_bag_done", False)
    st.rerun()

# --- Active Timer Display Logic ---
if st.session_state.timer_active:
    try:
        end_time_val = float(st.session_state.timer_end_time)
    except:
        end_time_val = 0.0
        
    time_left = end_time_val - datetime.now().timestamp()
    
    if time_left > 0:
        st.markdown(f"<h3 style='text-align: center; color: gray;'>Focusing on {st.session_state.timer_subject}...</h3>", unsafe_allow_html=True)
        html_code = f"""
        <div style="text-align: center; font-family: sans-serif;">
            <h1 id="clock" style="font-size: 80px; margin-top: 5vh; margin-bottom: 5vh;">⏱️ --:--</h1>
        </div>
        <script>
            var countDownDate = {end_time_val} * 1000;
            var x = setInterval(function() {{
                var now = new Date().getTime();
                var distance = countDownDate - now;
                if (distance <= 0) {{
                    clearInterval(x);
                    document.getElementById("clock").innerHTML = "⏱️ 00:00";
                }} else {{
                    var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                    var seconds = Math.floor((distance % (1000 * 60)) / 1000);
                    var m = minutes < 10 ? "0" + minutes : minutes;
                    var s = seconds < 10 ? "0" + seconds : seconds;
                    document.getElementById("clock").innerHTML = "⏱️ " + m + ":" + s;
                }}
            }}, 1000);
        </script>
        """
        components.html(html_code, height=200)
        if st.button("✅ Claim Session", use_container_width=True):
            st.rerun()
        st.stop()
            
    if datetime.now().timestamp() >= end_time_val and end_time_val > 0:
        sub = st.session_state.timer_subject
        t_type = st.session_state.timer_type
        if sub in SUBJECTS:
            has_completed_today = (st.session_state.full_sessions[sub] >= 1) or (st.session_state.half_sessions[sub] >= 2)
            if t_type == "full": st.session_state.full_sessions[sub] += 1
            else: st.session_state.half_sessions[sub] += 1
            if not has_completed_today and ((st.session_state.full_sessions[sub] >= 1) or (st.session_state.half_sessions[sub] >= 2)):
                st.session_state.streaks[sub] += 1
                st.session_state.last_studied_date[sub] = today_str
            save_to_sheety("full_sessions", st.session_state.full_sessions)
            save_to_sheety("half_sessions", st.session_state.half_sessions)
            save_to_sheety("streaks", st.session_state.streaks)
            save_to_sheety("last_studied_date", st.session_state.last_studied_date)
        st.session_state.timer_active = False
        save_to_sheety("timer_active", False)
        st.rerun()

# --- UI Continues ... (Paste the rest of your UI code here) ---
