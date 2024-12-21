# login.py
import json
import streamlit as st


def signIn(username, password):
    """Verifikasi login user"""
    try:
        with open("data/mahasiswa.json", "r") as f:
            users = json.load(f)

        if username in users:
            if users[username]["password"] == password:
                st.session_state["user"] = users[
                    username
                ]  # Simpan seluruh informasi pengguna
                return users[username]["role"]
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def tambah_akun(username, password, role="user", name=""):
    """Menambah user baru"""
    try:
        with open("data/mahasiswa.json", "r") as f:
            users = json.load(f)

        users[username] = {"password": password, "role": role, "name": name}

        with open("users.json", "w") as f:
            json.dump(users, f, indent=4)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
