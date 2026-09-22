content = open('ui/app.py', 'w', encoding='utf-8')

app_code = """
import streamlit as st
import sys
import os
import pandas as pd
from io import BytesIO

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import run_agent
from database import (init_db, login_user, register_user,
                      save_chat, get_all_users, get_all_chats,
                      get_user_chats, delete_user)

init_db()

ROLES = [
    "CEO",
    "Director",
    "Manager",
    "Team Lead (TL)",
    "Analyst",
    "Designer",
    "Employee"
]

SENIOR_ROLES = ["CEO", "Director"]
MID_ROLES = ["Manager", "Team Lead (TL)", "Analyst", "Designer"]
EMPLOYEE_ROLES = ["Employee"]

st.set_page_config(
    page_title="Financial AI Agent",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(\"\"\"
    <style>
        .main-header { font-size: 2rem; font-weight: bold; color: #1f77b4; text-align: center; padding: 1rem 0; }
        .sub-header { font-size: 1rem; color: #888; text-align: center; margin-bottom: 1rem; }
        .chat-message-user { background-color: rgba(31,119,180,0.15); padding: 1rem; border-radius: 10px; margin: 0.5rem 0; border-left: 4px solid #1f77b4; color: inherit; }
        .chat-message-agent { background-color: rgba(76,175,80,0.15); padding: 1rem; border-radius: 10px; margin: 0.5rem 0; border-left: 4px solid #4caf50; color: inherit; }
        .role-badge-senior { background: #ff4444; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; }
        .role-badge-mid { background: #ff9800; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; }
        .role-badge-employee { background: #4caf50; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; }
        footer { visibility: hidden; }
        .stButton > button { background-color: #1f77b4; color: white; border-radius: 8px; padding: 0.5rem 2rem; font-size: 1rem; border: none; width: 100%; height: 45px; }
        .stButton > button:hover { background-color: #1565c0; }
        .main .block-container { padding-bottom: 100px !important; }
    </style>
\"\"\", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "full_name" not in st.session_state:
    st.session_state.full_name = ""
if "role" not in st.session_state:
    st.session_state.role = ""
if "messages" not in st.session_state:
    st.session_state.messages = []
if "input_key" not in st.session_state:
    st.session_state.input_key = 0
if "selected_query" not in st.session_state:
    st.session_state.selected_query = ""
if "page" not in st.session_state:
    st.session_state.page = "chat"


def get_role_level(role):
    if role in SENIOR_ROLES:
        return "senior"
    elif role in MID_ROLES:
        return "mid"
    else:
        return "employee"


def show_auth_page():
    st.markdown(\"\"\"
        <div style='text-align:center; padding: 2rem 0 1rem 0;'>
            <span style='font-size:4rem'>📈</span>
            <div style='font-size:1.8rem; font-weight:bold; color:#1f77b4;'>Financial AI Agent</div>
            <div style='color:#888;'>Enterprise Market Insight Platform</div>
        </div>
    \"\"\", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            username = st.text_input("Username", placeholder="Enter username", key="login_username")
            password = st.text_input("Password", type="password", placeholder="Enter password", key="login_password")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Login", key="login_btn"):
                if not username or not password:
                    st.error("Please fill in all fields!")
                else:
                    success, result = login_user(username, password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.full_name = result["full_name"]
                        st.session_state.role = result["role"]
                        st.session_state.messages = []
                        st.session_state.page = "chat"
                        st.success(f"Welcome, {result['full_name']}!")
                        st.rerun()
                    else:
                        st.error(result)

        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            col_a, col_b = st.columns(2)
            with col_a:
                full_name = st.text_input("Full Name *", placeholder="Your full name", key="reg_name")
                email = st.text_input("Email ID *", placeholder="your@email.com", key="reg_email")
                phone = st.text_input("Phone No *", placeholder="+91 XXXXXXXXXX", key="reg_phone")
                national_id = st.text_input("National ID (Aadhar/PAN) *", placeholder="XXXX XXXX XXXX", key="reg_natid")
            with col_b:
                new_username = st.text_input("Username *", placeholder="Choose username", key="reg_username")
                role = st.selectbox("Select Role *", ROLES, key="reg_role")
                new_password = st.text_input("Password *", type="password", placeholder="Min 6 characters", key="reg_password")
                confirm_password = st.text_input("Confirm Password *", type="password", placeholder="Repeat password", key="reg_confirm")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Register", key="register_btn"):
                if not all([full_name, email, phone, national_id, new_username, new_password, confirm_password]):
                    st.error("Please fill in all fields!")
                elif new_password != confirm_password:
                    st.error("Passwords do not match!")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters!")
                else:
                    success, msg = register_user(full_name, email, phone, national_id, new_username, new_password, role)
                    if success:
                        st.success("Registration successful! Please login.")
                    else:
                        st.error(msg)


def show_sidebar():
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/stock-market.png", width=60)
        st.markdown(f"### {st.session_state.full_name}")

        level = get_role_level(st.session_state.role)
        if level == "senior":
            st.markdown(f"<span class='role-badge-senior'>{st.session_state.role}</span>", unsafe_allow_html=True)
        elif level == "mid":
            st.markdown(f"<span class='role-badge-mid'>{st.session_state.role}</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"<span class='role-badge-employee'>{st.session_state.role}</span>", unsafe_allow_html=True)

        st.markdown("---")

        st.markdown("### Navigation")
        if st.button("💬 Chat", key="nav_chat"):
            st.session_state.page = "chat"
            st.rerun()

        level = get_role_level(st.session_state.role)
        if level in ["senior", "mid"]:
            if st.button("👥 User Management", key="nav_users"):
                st.session_state.page = "users"
                st.rerun()
            if st.button("📊 Chat History", key="nav_history"):
                st.session_state.page = "history"
                st.rerun()

        if level == "senior":
            if st.button("📥 Export Data", key="nav_export"):
                st.session_state.page = "export"
                st.rerun()

        st.markdown("---")
        st.markdown("### Tools")
        st.markdown("""
        - 📰 News Fetcher
        - 🧠 FinBERT Sentiment
        - 💰 Stock Price
        - 🏷️ NER Tool
        - 📝 Summarizer
        """)

        st.markdown("---")
        st.markdown("### Sample Queries")
        sample_queries = [
            "What is Tesla's stock price?",
            "Apple market insights",
            "How is Infosys performing?",
            "Microsoft news summary",
            "Bitcoin sentiment"
        ]
        for query in sample_queries:
            if st.button(query, key=f"sq_{query}"):
                st.session_state.selected_query = query
                st.session_state.input_key += 1
                st.session_state.page = "chat"
                st.rerun()

        st.markdown("---")
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
        if st.button("🚪 Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


def show_chat_page():
    st.markdown('<div class="main-header">📈 Financial AI Agent for Market Insight</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Ask me anything about stocks, market sentiment, and financial news</div>', unsafe_allow_html=True)
    st.markdown("---")

    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="chat-message-user">👤 <strong>You:</strong><br>{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message-agent">🤖 <strong>Agent:</strong><br>{message["content"]}</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:80px'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input("query", value=st.session_state.selected_query,
                                   placeholder="e.g. What is Tesla's market sentiment today?",
                                   key=f"input_{st.session_state.input_key}",
                                   label_visibility="collapsed")
    with col2:
        send = st.button("🚀 Ask", key="send")

    if send and user_input.strip():
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("Agent is analyzing..."):
            try:
                response = run_agent(user_input, st.session_state.messages)
            except Exception as e:
                response = f"Error: {str(e)}. Please try again!"
        st.session_state.messages.append({"role": "assistant", "content": response})
        save_chat(st.session_state.username, st.session_state.full_name,
                  st.session_state.role, user_input, response)
        st.session_state.selected_query = ""
        st.session_state.input_key += 1
        st.rerun()
    elif send:
        st.warning("Please enter a query first!")


def show_users_page():
    st.markdown('<div class="main-header">👥 User Management</div>', unsafe_allow_html=True)
    st.markdown("---")

    users = get_all_users()
    if not users:
        st.info("No users registered yet!")
        return

    df = pd.DataFrame(users, columns=["ID", "Full Name", "Email", "Phone", "National ID", "Username", "Role", "Registered At"])

    level = get_role_level(st.session_state.role)

    # Senior can see all, mid can see employees only
    if level == "mid":
        df = df[df["Role"].isin(EMPLOYEE_ROLES)]
        st.info("Showing employee records only")

    st.markdown(f"### Total Users: {len(df)}")

    # Role filter
    role_filter = st.selectbox("Filter by Role", ["All"] + ROLES)
    if role_filter != "All":
        df = df[df["Role"] == role_filter]

    st.dataframe(df, use_container_width=True)

    # Delete user — senior only
    if level == "senior":
        st.markdown("---")
        st.markdown("### Delete User")
        usernames = [u[5] for u in users]
        del_user = st.selectbox("Select user to delete", usernames)
        if st.button("Delete User", key="del_btn"):
            if del_user == st.session_state.username:
                st.error("You cannot delete yourself!")
            else:
                success, msg = delete_user(del_user)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)


def show_history_page():
    st.markdown('<div class="main-header">📊 Chat History</div>', unsafe_allow_html=True)
    st.markdown("---")

    level = get_role_level(st.session_state.role)

    if level == "senior":
        chats = get_all_chats()
        st.markdown("### All Users Chat History")
    else:
        chats = get_user_chats(st.session_state.username)
        st.markdown("### My Chat History")

    if not chats:
        st.info("No chat history found!")
        return

    if level == "senior":
        df = pd.DataFrame(chats, columns=["Username", "Full Name", "Role", "Query", "Response", "Timestamp"])
    else:
        df = pd.DataFrame(chats, columns=["Query", "Response", "Timestamp"])

    # Search filter
    search = st.text_input("Search in history", placeholder="Type to search...")
    if search:
        mask = df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
        df = df[mask]

    st.dataframe(df, use_container_width=True)


def show_export_page():
    st.markdown('<div class="main-header">📥 Export Data</div>', unsafe_allow_html=True)
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Export Users")
        users = get_all_users()
        if users:
            df_users = pd.DataFrame(users, columns=["ID", "Full Name", "Email", "Phone", "National ID", "Username", "Role", "Registered At"])

            # CSV export
            csv = df_users.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Users CSV", csv, "users.csv", "text/csv")

            # Excel export
            excel_buffer = BytesIO()
            df_users.to_excel(excel_buffer, index=False)
            st.download_button("📥 Download Users Excel", excel_buffer.getvalue(), "users.xlsx")
        else:
            st.info("No users to export!")

    with col2:
        st.markdown("### Export Chat History")
        chats = get_all_chats()
        if chats:
            df_chats = pd.DataFrame(chats, columns=["Username", "Full Name", "Role", "Query", "Response", "Timestamp"])

            csv = df_chats.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Chats CSV", csv, "chat_history.csv", "text/csv")

            excel_buffer2 = BytesIO()
            df_chats.to_excel(excel_buffer2, index=False)
            st.download_button("📥 Download Chats Excel", excel_buffer2.getvalue(), "chat_history.xlsx")
        else:
            st.info("No chat history to export!")


# ── Main Router ───────────────────────────────────────────────
if not st.session_state.logged_in:
    show_auth_page()
else:
    show_sidebar()
    if st.session_state.page == "chat":
        show_chat_page()
    elif st.session_state.page == "users":
        show_users_page()
    elif st.session_state.page == "history":
        show_history_page()
    elif st.session_state.page == "export":
        show_export_page()
"""

with open('ui/app.py', 'w', encoding='utf-8') as f:
    f.write(app_code)

print("app.py written successfully!")