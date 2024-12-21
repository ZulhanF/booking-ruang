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


def get_room_status(selected_date, selected_time):
    if not os.path.exists("data/ruangan.json"):
        with open("data/ruangan.json", "w") as f:
            json.dump({}, f)

    try:
        with open("data/ruangan.json", "r") as f:
            ruangan = json.load(f)

        date_str = selected_date.strftime("%Y-%m-%d")
        time_str = f"{selected_time}:00 - {int(selected_time) + 1}:00"
        ruangan_index = f"{date_str}_{time_str}"

        if ruangan_index in ruangan:
            return ruangan[ruangan_index]
        return {room: "Free" for room in ROOMS}
    except Exception as e:
        print(f"Error: {e}")
        return {room: "Free" for room in ROOMS}


st.title("🎓 Sistem Booking Ruangan")

selected_date = st.date_input("Pilih Tanggal", datetime.now())
selected_time = st.selectbox(
    "Pilih Waktu",
    options=[f"{hour}:00" for hour in range(8, 17)],
)

st.divider()

# Dapatkan status ruangan
room_status = get_room_status(selected_date, selected_time)

# Buat DataFrame
df = pd.DataFrame(
    {"Nama Ruangan": ROOMS, "Status": [room_status.get(room, "Free") for room in ROOMS]}
)

# Tampilkan DataFrame dengan styling
st.subheader("Status Ruangan")
styled_df = df.style.apply(
    lambda row: ["color: green" if x == "Free" else "color: red" for x in row],
    subset=["Status"],
)

st.dataframe(
    styled_df,
    column_config={
        "Nama Ruangan": st.column_config.TextColumn("Nama Ruangan", width=300),
        "Status": st.column_config.TextColumn("Status", width=200),
    },
    hide_index=True,
)
