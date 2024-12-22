import streamlit as st
from verifikasi import signIn
import time

st.set_page_config(page_title="Booking Ruangan", page_icon="🎓")
st.title("🎓Sistem Booking Ruangan")


with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown(
    '<link rel="stylesheet" type="text/css" href="https://github.com/ZulhanF/booking-ruang/blob/main/styles.css">',
    unsafe_allow_html=True,
)
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
        st.success(f"Anda berhasil login sebagai {role}")
        time.sleep(2)
        if role == "Mahasiswa":
            st.switch_page("pages/halaman_siswa.py")
        elif role == "Dosen":
            st.switch_page("pages/halaman_dosen.py")
    else:
        st.error("Username atau password salah!")
