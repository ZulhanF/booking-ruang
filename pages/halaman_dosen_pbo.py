from abc import ABC, abstractmethod
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional
import os

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


class RoomStatus:
    def __init__(
        self,
        status: str = "Free",
        booked_by: str = "-",
        duration: int = 0,
        matkul: str = "-",
    ):
        self.status = status
        self.booked_by = booked_by
        self.duration = duration
        self.matkul = matkul

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "bookedBy": self.booked_by,
            "duration": self.duration,
            "matkul": self.matkul,
        }


class BookingInterface(ABC):
    @abstractmethod
    def get_room_status(
        self, selected_date: datetime, selected_time: int
    ) -> Dict[str, RoomStatus]:
        pass

    @abstractmethod
    def create_booking(
        self,
        date: str,
        start_hour: int,
        duration: int,
        room: str,
        user: str,
        matkul: str,
    ) -> bool:
        pass


class Booking(ABC):
    def __init__(
        self, room: str, start_hour: int, duration: int, user: str, matkul: str
    ):
        self.room = room
        self.start_hour = start_hour
        self.duration = duration
        self.user = user
        self.matkul = matkul

    @abstractmethod
    def validate(self) -> bool:
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        pass


class RegularBooking(Booking):
    def validate(self) -> bool:
        return self.duration <= 2 and 7 <= self.start_hour <= 16

    def to_dict(self) -> dict:
        return {
            "status": "Booked",
            "bookedBy": self.user,
            "duration": self.duration,
            "endTime": f"{(self.start_hour + self.duration):02d}:00",
            "matkul": self.matkul,
            "type": "Regular",
        }


class ExtendedBooking(Booking):
    def validate(self) -> bool:
        return self.duration <= 4 and 7 <= self.start_hour <= 16

    def to_dict(self) -> dict:
        return {
            "status": "Booked (Extended)",
            "bookedBy": self.user,
            "duration": self.duration,
            "endTime": f"{(self.start_hour + self.duration):02d}:00",
            "matkul": self.matkul,
            "type": "Extended",
        }


class RoomBookingSystem(BookingInterface):
    def __init__(self, rooms: List[str] = ROOMS):
        self.rooms = rooms
        self.json_file = "data/ruangans.json"
        self._initialize_json()

    def _initialize_json(self):
        try:
            if not os.path.exists(self.json_file):
                with open(self.json_file, "w") as f:
                    json.dump({}, f)
        except Exception as e:
            print(f"Error initializing JSON: {e}")

    def _check_availability(
        self, date: str, start_hour: int, duration: int, room: str
    ) -> bool:
        """Check if room is available for all required time slots"""
        try:
            with open(self.json_file, "r") as f:
                bookings = json.load(f)

            # Check each hour in the duration range
            for i in range(duration):
                current_hour = start_hour + i
                booking_key = f"{date}_{current_hour:02d}:00"

                if (
                    booking_key in bookings
                    and room in bookings[booking_key]
                    and bookings[booking_key][room]["status"] == "Booked"
                ):
                    return False
            return True
        except Exception as e:
            print(f"Error checking availability: {e}")
            return False

    def create_booking(
        self,
        date: str,
        start_hour: int,
        duration: int,
        room: str,
        user: str,
        matkul: str,
    ) -> bool:
        try:
            # Check availability first
            if not self._check_availability(date, start_hour, duration, room):
                st.error(f"Ruangan {room} sudah dibooking untuk waktu yang dipilih")
                return False

            # Create booking if available
            booking: Booking
            if duration <= 2:
                booking = RegularBooking(room, start_hour, duration, user, matkul)
            else:
                booking = ExtendedBooking(room, start_hour, duration, user, matkul)

            if not booking.validate():
                st.error("Booking tidak valid")
                return False

            with open(self.json_file, "r") as f:
                bookings = json.load(f)

            for i in range(duration):
                current_hour = start_hour + i
                booking_key = f"{date}_{current_hour:02d}:00"

                if booking_key not in bookings:
                    bookings[booking_key] = {}

                bookings[booking_key][room] = booking.to_dict()

            with open(self.json_file, "w") as f:
                json.dump(bookings, f, indent=4)
            st.success(
                f"Ruangan {room} berhasil dibooking untuk jam {start_hour:02d}:00 - {(start_hour + duration):02d}:00\n"
            )
            st.rerun()
            return True

        except Exception as e:
            print(f"Error creating booking: {e}")
            return False

    def get_room_status(
        self, selected_date: datetime, selected_time: int
    ) -> Dict[str, RoomStatus]:
        try:
            with open(self.json_file, "r") as f:
                bookings = json.load(f)

            date_str = selected_date.strftime("%Y-%m-%d")
            booking_key = f"{date_str}_{selected_time:02d}:00"

            status_dict: Dict[str, RoomStatus] = {}
            for room in self.rooms:
                if booking_key in bookings and room in bookings[booking_key]:
                    booking_data = bookings[booking_key][room]
                    status_dict[room] = RoomStatus(
                        status="Booked",
                        booked_by=booking_data["bookedBy"],
                        duration=booking_data["duration"],
                        matkul=booking_data.get("matkul", "-"),
                    )
                else:
                    status_dict[room] = RoomStatus()

            return status_dict

        except Exception as e:
            print(f"Error getting room status: {e}")
            return {room: RoomStatus() for room in self.rooms}


class BookingUI:
    def __init__(self, booking_system: BookingInterface):
        self.booking_system = booking_system
        self.setup_page()

    def setup_page(self):
        st.set_page_config(page_title="Booking Ruangan", page_icon="🎓", layout="wide")

        if "user" not in st.session_state:
            st.warning("Silakan login terlebih dahulu")
            if st.button("HOME"):
                st.query_params.clear()
                st.query_params[""] = ""
            st.stop()

        self.user_info = st.session_state.user
        st.title("🎓 Sistem Booking Ruangan")
        st.header(f"Selamat datang {self.user_info['name']}!")

    def render_date_time_selection(self):
        today = datetime.now()
        one_week_later = today + timedelta(days=7)

        self.selected_date = st.date_input(
            "Pilih Tanggal", min_value=today, max_value=one_week_later, value=today
        )
        self.selected_time = st.selectbox(
            "Pilih Waktu",
            options=[f"{hour}:00 - {hour + 1}:00" for hour in range(7, 17)],
        )

    def render_room_status(self):
        selected_hour = int(self.selected_time.split(":")[0])
        room_status = self.booking_system.get_room_status(
            self.selected_date, selected_hour
        )

        df = pd.DataFrame(
            {
                "Nama Ruangan": ROOMS,
                "Status": [room_status[room].status for room in ROOMS],
                "Dosen": [room_status[room].booked_by for room in ROOMS],
                "Mata Kuliah": [room_status[room].matkul for room in ROOMS],
            }
        )

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

    def render_booking_form(self):
        with st.form("booking_form"):
            room_choice = st.selectbox("Pilih Ruangan", ROOMS)
            start_time = st.selectbox(
                "Jam Mulai", options=[f"{hour:02d}:00" for hour in range(7, 17)]
            )
            duration = st.number_input(
                "Durasi (jam)", min_value=1, max_value=4, value=1
            )
            matkul = st.selectbox(
                "Pilih Mata Kuliah", options=st.session_state.user.get("matkul", ["-"])
            )

            if st.form_submit_button("Book Ruangan"):
                self.handle_booking_submission(
                    room_choice, start_time, duration, matkul
                )

    def handle_booking_submission(
        self, room_choice: str, start_time: str, duration: int, matkul: str
    ):
        start_hour = int(start_time.split(":")[0])
        end_hour = start_hour + duration

        if end_hour > 17:
            st.error("Booking melebihi jam operasional (17:00)")
            return

        date_str = self.selected_date.strftime("%Y-%m-%d")
        success = self.booking_system.create_booking(
            date_str, start_hour, duration, room_choice, self.user_info["name"], matkul
        )

        if success:
            st.success(
                f"Ruangan {room_choice} berhasil dibooking untuk {duration} jam!"
            )
            st.rerun()
        else:
            st.error("Ruangan tidak tersedia untuk durasi yang dipilih")

    def render(self):
        self.render_date_time_selection()
        st.divider()

        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("Status Ruangan")
            self.render_room_status()

        with col2:
            st.subheader("Booking Ruangan")
            self.render_booking_form()


# Constants


# Main execution
if __name__ == "__main__":
    booking_system = RoomBookingSystem()
    ui = BookingUI(booking_system)
    ui.render()
