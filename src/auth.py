import streamlit as st
import hashlib
from src.utils import read_json, write_json

USERS_FILE = "data/users.json"

ADMIN_USERNAME = "admin"


# ---------------- PASSWORD HELPERS ----------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def is_hashed(value: str) -> bool:
    # SHA256 hash length = 64
    return isinstance(value, str) and len(value) == 64


def migrate_plaintext_to_hash():
    """
    If users.json has plain text passwords, convert them to hashes automatically.
    """
    users = read_json(USERS_FILE, {})
    changed = False

    for u, p in list(users.items()):
        if not is_hashed(p):  # plain password -> hash
            users[u] = hash_password(p)
            changed = True

    if changed:
        write_json(USERS_FILE, users)


# ---------------- SIGNUP ----------------
def signup_ui():
    st.sidebar.subheader("🆕 Register (Sign Up)")

    new_user = st.sidebar.text_input("New Username", key="signup_user")
    new_pass = st.sidebar.text_input("New Password", type="password", key="signup_pass")
    confirm_pass = st.sidebar.text_input("Confirm Password", type="password", key="signup_confirm")

    if st.sidebar.button("Create Account ✅"):
        new_user = new_user.strip()

        if new_user == "" or new_pass.strip() == "":
            st.sidebar.error("❌ Username & Password cannot be empty")
            return

        if len(new_user) < 3:
            st.sidebar.error("❌ Username must be at least 3 characters")
            return

        if len(new_pass) < 4:
            st.sidebar.error("❌ Password must be at least 4 characters")
            return

        if new_pass != confirm_pass:
            st.sidebar.error("❌ Passwords do not match")
            return

        users = read_json(USERS_FILE, {})

        if new_user in users:
            st.sidebar.error("❌ Username already exists")
            return

        users[new_user] = hash_password(new_pass)
        write_json(USERS_FILE, users)

        st.sidebar.success("✅ Account created! Now login below 👇")


# ---------------- LOGIN ----------------
def login_ui():
    st.sidebar.subheader("🔐 Login")

    username = st.sidebar.text_input("Username", key="login_user")
    password = st.sidebar.text_input("Password", type="password", key="login_pass")

    users = read_json(USERS_FILE, {})

    if st.sidebar.button("Login 🚀"):
        username = username.strip()

        if username in users and users[username] == hash_password(password):
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.sidebar.success("✅ Logged in!")
            st.rerun()
        else:
            st.sidebar.error("❌ Invalid username/password")


# ---------------- FORGOT PASSWORD (RESET) ----------------
def forgot_password_ui():
    st.sidebar.subheader("🔁 Forgot Password")

    user = st.sidebar.text_input("Username to reset", key="reset_user")
    new_pass = st.sidebar.text_input("New Password", type="password", key="reset_pass")
    confirm_pass = st.sidebar.text_input("Confirm New Password", type="password", key="reset_confirm")

    st.sidebar.caption("⚠️ For this mini project, password reset works without email/OTP.")

    if st.sidebar.button("Reset Password 🔧"):
        user = user.strip()

        users = read_json(USERS_FILE, {})

        if user == "":
            st.sidebar.error("❌ Enter username")
            return

        if user not in users:
            st.sidebar.error("❌ User not found")
            return

        if len(new_pass) < 4:
            st.sidebar.error("❌ Password must be at least 4 characters")
            return

        if new_pass != confirm_pass:
            st.sidebar.error("❌ Passwords do not match")
            return

        users[user] = hash_password(new_pass)
        write_json(USERS_FILE, users)
        st.sidebar.success("✅ Password reset successful! Now login ✅")


# ---------------- ADMIN PANEL ----------------
def admin_panel_ui():
    """
    Only visible to admin user.
    Admin can:
    - view total users
    - delete users
    - reset user password
    """
    st.sidebar.markdown("---")
    st.sidebar.subheader("🛠 Admin Panel")

    users = read_json(USERS_FILE, {})

    st.sidebar.info(f"👥 Total Registered Users: {len(users)}")

    # User list
    user_list = sorted(list(users.keys()))
    if ADMIN_USERNAME in user_list:
        user_list.remove(ADMIN_USERNAME)

    if len(user_list) == 0:
        st.sidebar.warning("No users to manage yet.")
        return

    st.sidebar.write("📌 Manage Users")

    selected_user = st.sidebar.selectbox("Select user", user_list, key="admin_selected_user")

    # Delete user
    if st.sidebar.button("❌ Delete User"):
        users = read_json(USERS_FILE, {})
        if selected_user in users:
            del users[selected_user]
            write_json(USERS_FILE, users)
            st.sidebar.success(f"✅ Deleted user: {selected_user}")
            st.rerun()

    # Reset user password by admin
    new_admin_reset = st.sidebar.text_input("Set new password for user", type="password", key="admin_reset_pw")

    if st.sidebar.button("🔧 Admin Reset Password"):
        if len(new_admin_reset) < 4:
            st.sidebar.error("❌ Password must be at least 4 characters")
            return

        users = read_json(USERS_FILE, {})
        users[selected_user] = hash_password(new_admin_reset)
        write_json(USERS_FILE, users)
        st.sidebar.success(f"✅ Password reset for {selected_user}")


# ---------------- MAIN AUTH FLOW ----------------
def require_login():
    # Auto-fix old plain passwords into hashed
    migrate_plaintext_to_hash()

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        st.sidebar.title("👤 User Access")
        signup_ui()
        st.sidebar.markdown("---")
        login_ui()
        st.sidebar.markdown("---")
        forgot_password_ui()
        st.stop()


def logout_button():
    # Show admin panel only after login
    if st.session_state.get("username") == ADMIN_USERNAME:
        admin_panel_ui()

    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = None
        st.rerun()
