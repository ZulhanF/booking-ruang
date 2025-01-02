import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import os

st.set_page_config(page_title="Booking Ruangan", page_icon="🎓", layout="wide")

# Cek status login
if "user" not in st.session_state:
    st.warning("Silakan login terlebih dahulu")
    if st.button("HOME"):
        st.query_params.clear()
        st.query_params[""] = ""
    st.stop()

ROOMS = [
    "A10.01.01",
    "A10.01.02",
    "A10.01.03",
    "A10.01.04",
    "A10.01.05",
    "A10.01.06",
    "A10.01.07",
    "A10.01.08",
    "A10.01.09",
    "A10.01.10",
]


def get_datetime_options():
    options = []
    today = datetime.now()

    for i in range(7):
        date = today + timedelta(days=i)
        for hour in [7, 8, 9, 10, 11, 13, 14, 15, 16]:
            dt = date.replace(hour=hour, minute=0, second=0, microsecond=0)
            options.append(dt)
    return options


def initialize_json():
    """Load file json untuk menyimpan data ruangan"""
    try:
        with open("data/ruangans.json", "r") as f:
            content = f.read().strip()
            if not content:
                json.dump({}, f)
            return json.loads(content) if content else {}
    except Exception as e:
        print(f"Error reading JSON: {e}")
        return {}


def get_room_status(selected_date, selected_time):
    """Status ruangan pada waktu tertentu"""
    initialize_json()
    try:
        with open("data/ruangans.json", "r") as f:
            content = f.read().strip()
            ruangan = json.loads(content) if content else {}

        date_str = selected_date.strftime("%Y-%m-%d")
        time_str = f"{selected_time:02d}:00"
        booking_key = f"{date_str}_{time_str}"

        status_dict = {}
        for room in ROOMS:
            if booking_key in ruangan and room in ruangan[booking_key]:
                status_dict[room] = {
                    "status": "Booked",
                    "bookedBy": ruangan[booking_key][room]["bookedBy"],
                    "duration": ruangan[booking_key][room]["duration"],
                    "matkul": ruangan[booking_key][room].get("matkul", "-"),
                }
            else:
                status_dict[room] = {
                    "status": "Free",
                    "bookedBy": "-",
                    "duration": 0,
                    "matkul": "-",
                }
        return status_dict
    except Exception as e:
        print(f"Error reading JSON: {e}")
        return {
            room: {"status": "Free", "bookedBy": "-", "duration": 0, "matkul": "-"}
            for room in ROOMS
        }


user_info = st.session_state.user
st.title("🎓 Sistem Booking Ruangan")
st.header(f"Selamat datang {user_info['name']}!")

today = datetime.now()
one_week_later = today + timedelta(days=7)

selected_date = st.date_input(
    "Pilih Tanggal", min_value=today, max_value=one_week_later, value=today
)
selected_time = st.selectbox(
    "Pilih Waktu",
    options=[
        f"{hour}:00 - {hour + 1}:00" for hour in range(7, 17)
    ],  # Interval satu jam mulai dari jam 7 pagi hingga jam 4 sore
)

st.divider()
room_status = get_room_status(selected_date, int(selected_time.split(":")[0]))
df = pd.DataFrame(
    {
        "Nama Ruangan": ROOMS,
        "Status": [room_status[room]["status"] for room in ROOMS],
        "Dosen": [room_status[room]["bookedBy"] for room in ROOMS],
        "Mata Kuliah": [room_status[room]["matkul"] for room in ROOMS],
    }
)
# Dapatkan status ruangan
# Get room status

st.subheader("Status Ruangan")
styled_df = df.style.apply(
    lambda row: ["color: green" if x == "Free" else "color: red" for x in row],
    subset=["Status"],
)


st.dataframe(
    styled_df,
    column_config={
        "Nama Ruangan": st.column_config.TextColumn("Nama Ruangan", width=200),
        "Status": st.column_config.TextColumn("Status", width=150),
        "Dosen": st.column_config.TextColumn("Dosen", width=200),
        "Mata Kuliah": st.column_config.TextColumn("Mata Kuliah", width=250),
    },
    hide_index=True,
)
