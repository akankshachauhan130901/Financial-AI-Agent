import streamlit as st
import sys
import os
import pandas as pd
from io import BytesIO
import plotly.graph_objects as go  #type: ignore
import yfinance as yf

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import run_agent
from database import (init_db, login_user, register_user,
                      save_chat, get_all_users, get_all_chats,
                      get_user_chats, delete_user)

init_db()

ROLES = ["CEO", "Director", "Manager", "Team Lead (TL)", "Analyst", "Designer", "Employee"]
SENIOR_ROLES = ["CEO", "Director"]
MID_ROLES = ["Manager", "Team Lead (TL)", "Analyst", "Designer"]
EMPLOYEE_ROLES = ["Employee"]

st.set_page_config(page_title="Financial AI Agent", page_icon="📈", layout="wide")

st.markdown("""
    <style>
        .main-header { font-size: 2rem; font-weight: bold; color: #1f77b4; text-align: center; padding: 1rem 0; }
        .sub-header { font-size: 1rem; color: #888; text-align: center; margin-bottom: 1rem; }
        .chat-message-user { background-color: rgba(31,119,180,0.15); padding: 1rem; border-radius: 10px; margin: 0.5rem 0; border-left: 4px solid #1f77b4; color: inherit; }
        .chat-message-agent { background-color: rgba(76,175,80,0.15); padding: 1rem; border-radius: 10px; margin: 0.5rem 0; border-left: 4px solid #4caf50; color: inherit; }
        .badge-senior { background: #ff4444; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; }
        .badge-mid { background: #ff9800; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; }
        .badge-employee { background: #4caf50; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; }
        .history-item { background: rgba(255,255,255,0.05); padding: 8px; border-radius: 8px; margin: 4px 0; font-size: 0.85rem; border-left: 3px solid #1f77b4; }
        .impersonate-bar { background: rgba(255,165,0,0.2); padding: 8px; border-radius: 8px; border-left: 3px solid orange; margin-bottom: 10px; font-size: 0.85rem; }
        footer { visibility: hidden; }
        .stButton > button { background-color: #1f77b4; color: white; border-radius: 8px; padding: 0.5rem 2rem; font-size: 1rem; border: none; width: 100%; height: 45px; }
        .stButton > button:hover { background-color: #1565c0; }
        .logout-btn > button { background-color: #ff4444 !important; }
        .main .block-container { padding-bottom: 100px !important; }
    </style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────
defaults = {
    "logged_in": False,
    "username": "",
    "full_name": "",
    "role": "",
    "original_username": "",
    "original_full_name": "",
    "original_role": "",
    "is_impersonating": False,
    "messages": [],
    "input_key": 0,
    "selected_query": "",
    "page": "chat",
    "show_login_as": False,
    "last_ticker": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# Stock ticker detection
TICKER_MAP = {
    "tesla": "TSLA", "apple": "AAPL", "microsoft": "MSFT",
    "google": "GOOGL", "amazon": "AMZN", "meta": "META",
    "nvidia": "NVDA", "netflix": "NFLX", "bitcoin": "BTC-USD",
    "infosys": "INFY.NS", "tcs": "TCS.NS", "wipro": "WIPRO.NS",
    "reliance": "RELIANCE.NS", "hdfc": "HDFCBANK.NS",
    "icici": "ICICIBANK.NS", "sbi": "SBIN.NS",
    "tatamotors": "TATAMOTORS.NS", "adani": "ADANIENT.NS",
    "bajaj": "BAJFINANCE.NS", "maruti": "MARUTI.NS",
    "sunpharma": "SUNPHARMA.NS", "ongc": "ONGC.NS",
    "vedanta": "VEDL.NS", "suzlon": "SUZLON.NS",
    "zomato": "ZOMATO.NS", "paytm": "PAYTM.NS",
    "nifty": "^NSEI", "sensex": "^BSESN"
}


def detect_ticker(query: str):
    """Detect stock ticker from user query"""
    query_lower = query.lower()
    for name, ticker in TICKER_MAP.items():
        if name in query_lower:
            return ticker
    return None


def show_stock_chart(ticker: str, days: int = 30):
    """Show interactive stock chart"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=f"{days}d")

        if hist.empty:
            return

        company_name = stock.info.get("longName", ticker)

        fig = go.Figure()

        # Candlestick chart
        fig.add_trace(go.Scatter(
            x=hist.index,
            y=hist["Close"],
            mode="lines",
            name="Close Price",
            line=dict(color="#1f77b4", width=2),
            fill="tozeroy",
            fillcolor="rgba(31,119,180,0.1)"
        ))

        # Add 7 day moving average
        hist["MA7"] = hist["Close"].rolling(window=7).mean()
        fig.add_trace(go.Scatter(
            x=hist.index,
            y=hist["MA7"],
            mode="lines",
            name="7-Day MA",
            line=dict(color="#ff7f0e", width=1.5, dash="dash")
        ))

        # Styling
        fig.update_layout(
            title=f"{company_name} — Stock Price (Last {days} Days)",
            xaxis_title="Date",
            yaxis_title=f"Price ({stock.info.get('currency', 'USD')})",
            template="plotly_dark",
            hovermode="x unified",
            showlegend=True,
            height=400,
            margin=dict(l=40, r=40, t=60, b=40),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            xaxis=dict(
                gridcolor="rgba(255,255,255,0.1)",
                showgrid=True
            ),
            yaxis=dict(
                gridcolor="rgba(255,255,255,0.1)",
                showgrid=True
            )
        )

        # Price change indicator
        first_price = hist["Close"].iloc[0]
        last_price = hist["Close"].iloc[-1]
        change = last_price - first_price
        change_pct = (change / first_price) * 100
        color = "green" if change >= 0 else "red"
        arrow = "▲" if change >= 0 else "▼"

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current Price",
                      f"{stock.info.get('currency','$')} {last_price:.2f}",
                      f"{arrow} {abs(change_pct):.2f}%")
        with col2:
            st.metric("Period High",
                      f"{hist['High'].max():.2f}")
        with col3:
            st.metric("Period Low",
                      f"{hist['Low'].min():.2f}")

        st.plotly_chart(fig, use_container_width=True)

        # Volume bar chart
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Bar(
            x=hist.index,
            y=hist["Volume"],
            name="Volume",
            marker_color="rgba(31,119,180,0.6)"
        ))
        fig_vol.update_layout(
            title="Trading Volume",
            template="plotly_dark",
            height=200,
            margin=dict(l=40, r=40, t=40, b=40),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.1)")
        )
        st.plotly_chart(fig_vol, use_container_width=True)

    except Exception as e:
        st.warning(f"Chart could not be loaded: {str(e)}")

def get_level(role):
    if role in SENIOR_ROLES:
        return "senior"
    elif role in MID_ROLES:
        return "mid"
    return "employee"


# ══════════════════════════════════════════════════════════════
# AUTH PAGE
# ══════════════════════════════════════════════════════════════
def show_auth_page():
    st.markdown("""
        <div style='text-align:center; padding:2rem 0 1rem 0;'>
            <span style='font-size:4rem'>📈</span>
            <div style='font-size:1.8rem; font-weight:bold; color:#1f77b4;'>Financial AI Agent</div>
            <div style='color:#888;'>Enterprise Market Insight Platform</div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["Login", "Register"])

        # ── Login ──
        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            username = st.text_input("Username", placeholder="Enter username", key="login_user")
            password = st.text_input("Password", type="password", placeholder="Enter password", key="login_pass")
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
                        st.session_state.original_username = username
                        st.session_state.original_full_name = result["full_name"]
                        st.session_state.original_role = result["role"]
                        st.session_state.is_impersonating = False
                        st.session_state.messages = []
                        st.session_state.page = "chat"
                        st.success(f"Welcome, {result['full_name']}!")
                        st.rerun()
                    else:
                        st.error(result)
                        st.markdown("""
                            <div style='text-align:center; margin-top:10px; color:#888; font-size:0.9rem;'>
                                Not registered yet? 
                                <span style='color:#1f77b4; font-weight:bold;'>
                                    Click the 'Register' tab above to create your account first.
                                </span>
                            </div>
                        """, unsafe_allow_html=True)
                    st.markdown("""
                <div style='text-align:center; margin-top:20px; color:#888; font-size:0.9rem; border-top:1px solid #333; padding-top:15px;'>
                    New to Financial AI Agent? &nbsp;
                    <span style='color:#1f77b4; font-weight:bold;'>
                        Register yourself first to get access — click the 'Register' tab above.
                    </span>
                </div>
            """, unsafe_allow_html=True)
                    
        # ── Register ──
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
                new_password = st.text_input("Password *", type="password", placeholder="Min 6 characters", key="reg_pass")
                confirm_password = st.text_input("Confirm Password *", type="password", placeholder="Repeat password", key="reg_confirm")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Register", key="reg_btn"):
                if not all([full_name, email, phone, national_id, new_username, new_password, confirm_password]):
                    st.error("Please fill in all fields!")
                elif new_password != confirm_password:
                    st.error("Passwords do not match!")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters!")
                else:
                    success, msg = register_user(full_name, email, phone, national_id,
                                                  new_username, new_password, role)
                    if success:
                        st.success("Registration successful! Please login.")
                    else:
                        st.error(msg)
                        st.markdown("---")
            st.markdown("""
                <div style='text-align:center; color:#888; font-size:0.9rem;'>
                    Already have an account? &nbsp;
                    <span style='color:#1f77b4; font-weight:bold;'>
                        Click the 'Login' tab above to sign in and access your dashboard.
                    </span>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("""
                <div style='text-align:center; margin-top:20px; color:#888; font-size:0.9rem; border-top:1px solid #333; padding-top:15px;'>
                    Already have an account? &nbsp;
                    <span style='color:#1f77b4; font-weight:bold;'>
                        Click the 'Login' tab above to sign in to your dashboard.
                    </span>
                </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
def show_sidebar():
    with st.sidebar:

        # ── User Info ──
        st.markdown("## Financial AI Agent")
        st.markdown("---")

        # Show impersonation bar if CEO is viewing as another user
        if st.session_state.is_impersonating:
            st.markdown(f"""
                <div class='impersonate-bar'>
                    Viewing as: <strong>{st.session_state.full_name}</strong>
                    ({st.session_state.role})
                </div>
            """, unsafe_allow_html=True)
            if st.button("Back to My Account", key="back_to_own"):
                st.session_state.username = st.session_state.original_username
                st.session_state.full_name = st.session_state.original_full_name
                st.session_state.role = st.session_state.original_role
                st.session_state.is_impersonating = False
                st.session_state.messages = []
                st.session_state.page = "chat"
                st.rerun()
            st.markdown("---")

        st.markdown(f"### {st.session_state.full_name}")
        level = get_level(st.session_state.role)
        badge = "badge-senior" if level == "senior" else "badge-mid" if level == "mid" else "badge-employee"
        st.markdown(f"<span class='{badge}'>{st.session_state.role}</span>", unsafe_allow_html=True)
        st.markdown("---")

        # ── Navigation ──
        st.markdown("### Navigation")
        if st.button("💬 Chat", key="nav_chat"):
            st.session_state.page = "chat"
            st.rerun()

        if level in ["senior", "mid"]:
            if st.button("👥 User Management", key="nav_users"):
                st.session_state.page = "users"
                st.rerun()
            if st.button("📊 All Chat History", key="nav_history"):
                st.session_state.page = "history"
                st.rerun()

        if level == "senior":
            if st.button("📥 Export Data", key="nav_export"):
                st.session_state.page = "export"
                st.rerun()
            if st.button("🔁 Login as Another User", key="nav_loginas"):
                st.session_state.show_login_as = not st.session_state.show_login_as
                st.rerun()

        # ── Login as Another User Panel ──
        if st.session_state.show_login_as and level == "senior":
            st.markdown("---")
            st.markdown("### Login as Another User")
            users = get_all_users()
            other_users = [u for u in users if u[5] != st.session_state.original_username]
            if other_users:
                user_options = {f"{u[1]} ({u[6]}) - @{u[5]}": u for u in other_users}
                selected = st.selectbox("Select User", list(user_options.keys()), key="impersonate_select")
                if st.button("View as This User", key="impersonate_btn"):
                    selected_user = user_options[selected]
                    st.session_state.username = selected_user[5]
                    st.session_state.full_name = selected_user[1]
                    st.session_state.role = selected_user[6]
                    st.session_state.is_impersonating = True
                    st.session_state.messages = []
                    st.session_state.page = "chat"
                    st.session_state.show_login_as = False
                    st.rerun()
            else:
                st.info("No other users registered yet!")

        st.markdown("---")

        # ── My Chat History in Sidebar ──
        st.markdown("### My Recent Chats")
        my_chats = get_user_chats(st.session_state.username)
        if my_chats:
            for i, chat in enumerate(my_chats[:5]):
                query_short = chat[0][:35] + "..." if len(chat[0]) > 35 else chat[0]
                if st.button(f"💬 {query_short}", key=f"hist_{i}"):
                    st.session_state.selected_query = chat[0]
                    st.session_state.input_key += 1
                    st.session_state.page = "chat"
                    st.rerun()
        else:
            st.info("No chat history yet!")

        st.markdown("---")

        # ── Sample Queries ──
        st.markdown("### Sample Queries")
        queries = [
            "Tesla stock price?",
            "Apple market insights",
            "Infosys performance?",
            "Microsoft news",
            "Bitcoin sentiment"
        ]
        for q in queries:
            if st.button(q, key=f"sq_{q}"):
                st.session_state.selected_query = q
                st.session_state.input_key += 1
                st.session_state.page = "chat"
                st.rerun()

        st.markdown("---")

        # ── Action Buttons ──
        if st.button("🗑️ Clear Chat", key="clear_chat"):
            st.session_state.messages = []
            st.rerun()

        st.markdown("<div class='logout-btn'>", unsafe_allow_html=True)
        if st.button("🚪 Logout", key="logout_btn"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# CHAT PAGE
# ══════════════════════════════════════════════════════════════
def show_chat_page():
    st.markdown('<div class="main-header">📈 Financial AI Agent for Market Insight</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Ask me anything about stocks, market sentiment, and financial news</div>',
                unsafe_allow_html=True)
    st.markdown("---")

    # Display all messages
    for idx, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-message-user">👤 <strong>You:</strong><br>{msg["content"]}</div>',
                        unsafe_allow_html=True)
        else:
            # Agent response — use container so markdown renders properly
            with st.container():
                st.markdown('<div class="chat-message-agent">🤖 <strong>Agent:</strong></div>',
                            unsafe_allow_html=True)
                st.markdown(msg["content"])

            # Show chart only after last agent message
            if idx == len(st.session_state.messages) - 1:
                if st.session_state.get("last_ticker"):
                    st.markdown("---")
                    st.markdown("### 📈 Stock Chart")
                    days = st.select_slider(
                        "Select Time Period",
                        options=[7, 14, 30, 60, 90],
                        value=30,
                        key="chart_days"
                    )
                    show_stock_chart(st.session_state.last_ticker, days)
                    st.markdown("---")

    st.markdown("<div style='height:80px'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input(
            "q",
            value=st.session_state.selected_query,
            placeholder="e.g. What is Tesla's market sentiment today?",
            key=f"input_{st.session_state.input_key}",
            label_visibility="collapsed"
        )
    with col2:
        send = st.button("Ask", key="send")

    if send and user_input.strip():
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        # Run agent
        with st.spinner("Agent is analyzing..."):
            try:
                response = run_agent(user_input, st.session_state.messages)
            except Exception as e:
                response = f"Error: {str(e)}. Please try again!"

        # Add agent response
        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })

        # Save to database
        save_chat(
            st.session_state.username,
            st.session_state.full_name,
            st.session_state.role,
            user_input,
            response
        )

        # Detect ticker for chart
        ticker = detect_ticker(user_input)
        if ticker:
            st.session_state.last_ticker = ticker
        else:
            st.session_state.last_ticker = None

        st.session_state.selected_query = ""
        st.session_state.input_key += 1
        st.rerun()

    elif send:
        st.warning("Please enter a query first!")


# ══════════════════════════════════════════════════════════════
# USER MANAGEMENT PAGE
# ══════════════════════════════════════════════════════════════
def show_users_page():
    st.markdown('<div class="main-header">👥 User Management</div>', unsafe_allow_html=True)
    st.markdown("---")

    users = get_all_users()
    if not users:
        st.info("No users registered yet!")
        return

    df = pd.DataFrame(users, columns=["ID", "Full Name", "Email", "Phone",
                                       "National ID", "Username", "Role", "Registered At"])

    level = get_level(st.session_state.role)
    if level == "mid":
        df = df[df["Role"].isin(EMPLOYEE_ROLES)]
        st.info("Showing employee records only")

    st.markdown(f"### Total Users: {len(df)}")
    role_filter = st.selectbox("Filter by Role", ["All"] + ROLES)
    if role_filter != "All":
        df = df[df["Role"] == role_filter]

    st.dataframe(df, use_container_width=True)

    if level == "senior":
        st.markdown("---")
        st.markdown("### Delete User")
        usernames = [u[5] for u in users]
        del_user = st.selectbox("Select user to delete", usernames)
        if st.button("Delete User"):
            if del_user == st.session_state.original_username:
                st.error("You cannot delete yourself!")
            else:
                success, msg = delete_user(del_user)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)


# ══════════════════════════════════════════════════════════════
# CHAT HISTORY PAGE
# ══════════════════════════════════════════════════════════════
def show_history_page():
    st.markdown('<div class="main-header">📊 Chat History</div>', unsafe_allow_html=True)
    st.markdown("---")

    level = get_level(st.session_state.original_role)

    if level == "senior":
        chats = get_all_chats()
        st.markdown("### All Users Chat History")
        if not chats:
            st.info("No chat history found!")
            return
        df = pd.DataFrame(chats, columns=["Username", "Full Name", "Role",
                                           "Query", "Response", "Timestamp"])
    else:
        chats = get_user_chats(st.session_state.username)
        st.markdown("### My Chat History")
        if not chats:
            st.info("No chat history found!")
            return
        df = pd.DataFrame(chats, columns=["Query", "Response", "Timestamp"])

    search = st.text_input("Search in history", placeholder="Type to search...")
    if search:
        mask = df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
        df = df[mask]

    st.dataframe(df, use_container_width=True)


# ══════════════════════════════════════════════════════════════
# EXPORT PAGE
# ══════════════════════════════════════════════════════════════
def show_export_page():
    st.markdown('<div class="main-header">📥 Export Data</div>', unsafe_allow_html=True)
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Export Users")
        users = get_all_users()
        if users:
            df_users = pd.DataFrame(users, columns=["ID", "Full Name", "Email", "Phone",
                                                      "National ID", "Username", "Role", "Registered At"])
            csv = df_users.to_csv(index=False).encode("utf-8")
            st.download_button("Download Users CSV", csv, "users.csv", "text/csv")
            excel_buf = BytesIO()
            df_users.to_excel(excel_buf, index=False)
            st.download_button("Download Users Excel", excel_buf.getvalue(), "users.xlsx")
        else:
            st.info("No users to export!")

    with col2:
        st.markdown("### Export Chat History")
        chats = get_all_chats()
        if chats:
            df_chats = pd.DataFrame(chats, columns=["Username", "Full Name", "Role",
                                                      "Query", "Response", "Timestamp"])
            csv2 = df_chats.to_csv(index=False).encode("utf-8")
            st.download_button("Download Chats CSV", csv2, "chats.csv", "text/csv")
            excel_buf2 = BytesIO()
            df_chats.to_excel(excel_buf2, index=False)
            st.download_button("Download Chats Excel", excel_buf2.getvalue(), "chats.xlsx")
        else:
            st.info("No chat history to export!")


# ══════════════════════════════════════════════════════════════
# MAIN ROUTER
# ══════════════════════════════════════════════════════════════
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