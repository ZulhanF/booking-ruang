import streamlit as st
from verifikasi import signIn
import time

st.set_page_config(page_title="Booking Ruangan", page_icon="🎓")
st.title("🎓Sistem Booking Ruangan")

with st.form("login_form"):
    st.header("Login Page")

    username = st.text_input(
        "Username",
        placeholder="Masukkan username...",
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Masukkan password...",
    )

    submitted = st.form_submit_button("Submit")

    if submitted:
        role = signIn(username, password)
        if role:
            st.session_state["user"] = role
            st.success(f"Anda berhasil login sebagai {role}")
            time.sleep(1)
            st.switch_page("pages/Halaman.py")
        else:
            st.error("Username atau password salah!")
