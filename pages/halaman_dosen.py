import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
import json
import os

st.set_page_config(page_title="Booking Ruangan", page_icon="🎓", layout="wide")

# Cek status login
if "user" not in st.session_state:
    st.warning("Silakan login terlebih dahulu")
    st.markdown('''
        <a href="/" target="_self" style="
            text-decoration: none;
            background-color: #FF4B4B;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            display: inline-block;">
            🏠 HOME
        </a>
    ''', unsafe_allow_html=True)
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


def create_booking_entries(
    bookings, date_str, start_hour, duration, room_choice, user_name, matkul
):
    """Create booking entries for all hours in duration"""
    for i in range(duration):
        current_hour = start_hour + i
        booking_key = f"{date_str}_{current_hour:02d}:00"

        if booking_key not in bookings:
            bookings[booking_key] = {}

        bookings[booking_key][room_choice] = {
            "status": "Booked",
            "bookedBy": user_name,
            "duration": duration,
            "endTime": f"{(start_hour + duration):02d}:00",
            "matkul": matkul,
        }
    return bookings


def check_room_availability(bookings, date_str, start_hour, duration, room_choice):
    """Buat cek apakah waktu yang dipilih tersedia"""
    for i in range(duration):
        check_hour = start_hour + i
        check_key = f"{date_str}_{check_hour:02d}:00"
        if check_key in bookings and room_choice in bookings[check_key]:
            return False
    return True


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

# Dapatkan status ruangan
room_status = get_room_status(selected_date, int(selected_time.split(":")[0]))
# Buat DataFrame
df = pd.DataFrame(
    {"Nama Ruangan": ROOMS, "Status": [room_status.get(room, "Free") for room in ROOMS]}
)

col1, col2 = st.columns([2, 1])

with col1:
    # Get room status
    room_status = get_room_status(selected_date, int(selected_time.split(":")[0]))

    # Create DataFrame with all info
    df = pd.DataFrame(
        {
            "Nama Ruangan": ROOMS,
            "Status": [room_status[room]["status"] for room in ROOMS],
            "Dosen": [room_status[room]["bookedBy"] for room in ROOMS],
            "Mata Kuliah": [room_status[room]["matkul"] for room in ROOMS],
        }
    )

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
    selected_room = st.selectbox("Pilih Booking untuk Dihapus", ROOMS)
    if st.button("🗑️Hapus Booking"):
        try:
            initialize_json()
            with open("data/ruangans.json", "r") as f:
                bookings = json.loads(f.read().strip() or "{}")

            date_str = selected_date.strftime("%Y-%m-%d")
            time_str = f"{int(selected_time.split(':')[0]):02d}:00"
            booking_key = f"{date_str}_{time_str}"

            if (
                booking_key not in bookings
                or selected_room not in bookings[booking_key]
            ):
                st.warning("Ruangan belum dibooking.")
            elif bookings[booking_key][selected_room]["bookedBy"] != user_info["name"]:
                st.error("❌ Anda tidak memiliki izin untuk menghapus booking ini.")
            else:
                del bookings[booking_key][selected_room]
                if not bookings[booking_key]:
                    del bookings[booking_key]
                with open("data/ruangans.json", "w") as f:
                    json.dump(bookings, f, indent=4)
                st.success(f"🚮 Booking ruangan {selected_room} berhasil dihapus!")
                time.sleep(2)
                st.rerun()
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")

with col2:
    st.subheader("Booking Ruangan")

    with st.form("booking_form"):
        room_choice = st.selectbox("Pilih Ruangan", ROOMS)

        start_time = st.selectbox(
            "Jam Mulai", options=[f"{hour:02d}:00" for hour in range(7, 17)]
        )

        duration = st.number_input("Durasi (jam)", min_value=1, max_value=4, value=1)

        matkul = st.selectbox(
            "Pilih Mata Kuliah", options=st.session_state.user.get("matkul", ["-"])
        )

        submit = st.form_submit_button("Book Ruangan")

        if submit:
            try:
                initialize_json()

                with open("data/ruangans.json", "r") as f:
                    content = f.read().strip()
                    bookings = json.loads(content) if content else {}

                start_hour = int(start_time.split(":")[0])
                end_hour = start_hour + duration

                if end_hour > 17:
                    st.error("Booking melebihi jam operasional (17:00)")
                else:
                    date_str = selected_date.strftime("%Y-%m-%d")

                    # Check availability for all time slots
                    if check_room_availability(
                        bookings, date_str, start_hour, duration, room_choice
                    ):
                        # Create bookings for all hours in duration
                        bookings = create_booking_entries(
                            bookings,
                            date_str,
                            start_hour,
                            duration,
                            room_choice,
                            st.session_state.user["name"],
                            matkul,
                        )

                        with open("data/ruangans.json", "w") as f:
                            json.dump(bookings, f, indent=4)

                        success_message = st.success(
                            f"✅ Booking Berhasil dilakukan untuk Ruangan {room_choice}!\n\n"
                        )
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("❌ Ruangan tidak tersedia untuk durasi yang dipilih!")

            except Exception as e:
                st.error(f"Terjadi kesalahan: {str(e)}")


def create_booking_entries(
    bookings, date_str, start_hour, duration, room_choice, user_name, matkul
):
    """Create booking entries for all hours in duration"""
    for i in range(duration):
        current_hour = start_hour + i
        booking_key = f"{date_str}_{current_hour:02d}:00"

        if booking_key not in bookings:
            bookings[booking_key] = {}

        bookings[booking_key][room_choice] = {
            "status": "Booked",
            "bookedBy": user_name,
            "duration": duration,
            "endTime": f"{(start_hour + duration):02d}:00",
            "matkul": matkul,
        }
    return bookings
