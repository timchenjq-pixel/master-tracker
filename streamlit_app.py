import streamlit as st
from datetime import date, timedelta

# --- SETUP & MEMORY ---
# This keeps our data saved while we click around
if 'subjects' not in st.session_state:
    default_data = {"streak": 0.0, "last_date": None}
    st.session_state.subjects = {
        "Chinese": default_data.copy(),
        "English": default_data.copy(),
        "Math": default_data.copy(),
        "History": default_data.copy(),
        "Literature": default_data.copy(),
        "Geography": default_data.copy(),
        "Life science": default_data.copy(),
        "Physical science": default_data.copy(),
    }

# This controls our timer screen
if 'timer_active' not in st.session_state:
    st.session_state.timer_active = False
    st.session_state.current_subject = ""
    st.session_state.timer_amount = 0 
    st.session_state.streak_value = 0.0 

# --- MAIN APP LAYOUT ---
st.title("Tim's Study Tracker")

today = date.today()

# If the timer is NOT running, show the main list
if not st.session_state.timer_active:
    st.subheader("Your Subjects")

    # Create a nice layout for each subject
    for subject, data in st.session_state.subjects.items():
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

        with col1:
            st.write(f"**{subject}**")
            st.write(f"Streak: {data['streak']} 🔥")

        with col2:
            if st.button("15 Min (Full)", key=f"full_{subject}"):
                st.session_state.timer_active = True
                st.session_state.current_subject = subject
                st.session_state.timer_amount = 15
                st.session_state.streak_value = 1.0
                st.rerun()

        with col3:
            if st.button("5 Min (Half)", key=f"half_{subject}"):
                st.session_state.timer_active = True
                st.session_state.current_subject = subject
                st.session_state.timer_amount = 5
                st.session_state.streak_value = 0.5
                st.rerun()

        with col4:
            # Shows when it was last studied
            last = data['last_date']
            if last:
                st.write(f"Last: {last.strftime('%b %d')}")
            else:
                st.write("Last: Never")

        st.divider()

# If the timer IS running, show the timer screen
else:
    subject = st.session_state.current_subject
    minutes = st.session_state.timer_amount
    st.header(f"Studying: {subject}")
    st.write(f"Session length: {minutes} minutes")

    # Manual button to claim points for testing purposes
    if st.button("Finish Session & Claim Streak", type="primary"):
        # 1. Check if we broke the streak (gap of more than 1 break day)
        last_date = st.session_state.subjects[subject]['last_date']
        if last_date:
            days_passed = (today - last_date).days
            # If gap is 3 days or more, streak is broken!
            if days_passed > 2: 
                st.session_state.subjects[subject]['streak'] = 0.0

        # 2. Add the streak points and update date
        st.session_state.subjects[subject]['streak'] += st.session_state.streak_value
        st.session_state.subjects[subject]['last_date'] = today

        # 3. Go back to main screen
        st.session_state.timer_active = False
        st.rerun()

    if st.button("Cancel (Go Back)"):
         st.session_state.timer_active = False
         st.rerun()
