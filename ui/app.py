import streamlit as st
import sys
import os

# Add parent directory to path so we can import agent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import run_agent

# ── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Financial AI Agent",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1f77b4;
            text-align: center;
            padding: 1rem 0;
        }
        .sub-header {
            font-size: 1rem;
            color: #666;
            text-align: center;
            margin-bottom: 2rem;
        }
        .chat-message-user {
            background-color: rgba(31, 119, 180, 0.15);
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            border-left: 4px solid #1f77b4;
            color: inherit;
        }
        .chat-message-agent {
            background-color: rgba(76, 175, 80, 0.15);
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            border-left: 4px solid #4caf50;
            color: inherit;
        }
        .stButton > button {
            background-color: #1f77b4;
            color: white;
            border-radius: 8px;
            padding: 0.5rem 2rem;
            font-size: 1rem;
            border: none;
            width: 100%;
        }
        .stButton > button:hover {
            background-color: #1565c0;
        }
    </style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/96/stock-market.png", width=80)
    st.markdown("## 📊 Financial AI Agent")
    st.markdown("---")
    st.markdown("### 🛠️ Available Tools")
    st.markdown("""
    - 📰 **News Fetcher** — Live financial news
    - 🧠 **Sentiment Analyzer** — FinBERT analysis
    - 💰 **Stock Price** — Real-time prices
    - 🏷️ **NER Tool** — Entity extraction
    - 📝 **Summarizer** — News summaries
    """)

    st.markdown("---")
    st.markdown("### 💡 Sample Queries")
    sample_queries = [
        "What is Tesla's current stock price and sentiment?",
        "Give me Apple market insights",
        "How is Infosys stock performing?",
        "Summarize latest Microsoft news",
        "What is the sentiment around Bitcoin?"
    ]

    for query in sample_queries:
        if st.button(query, key=query):
            st.session_state.selected_query = query

    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("""
    Built with:
    - 🦙 Groq LLaMA 3.1
    - 🤗 FinBERT
    - 📊 yFinance
    - 🔗 LangChain
    """)

# ── Main Page ─────────────────────────────────────────────────
st.markdown('<div class="main-header">📈 Financial AI Agent for Market Insight</div>',
            unsafe_allow_html=True)
st.markdown('<div class="sub-header">Ask me anything about stocks, market sentiment, and financial news</div>',
            unsafe_allow_html=True)

# ── Initialize Chat History ───────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_query" not in st.session_state:
    st.session_state.selected_query = ""

# ── Display Chat History ──────────────────────────────────────
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"""
            <div class="chat-message-user">
                👤 <strong>You:</strong><br>{message["content"]}
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="chat-message-agent">
                🤖 <strong>Agent:</strong><br>{message["content"]}
            </div>
        """, unsafe_allow_html=True)

# ── Input Area ────────────────────────────────────────────────
st.markdown("---")
col1, col2 = st.columns([5, 1])

with col1:
    user_input = st.text_input(
        "Ask about any stock or company:",
        value=st.session_state.selected_query,
        placeholder="e.g. What is Tesla's market sentiment today?",
        key="user_input",
        label_visibility="collapsed"
    )

with col2:
    send_button = st.button("🚀 Ask", key="send")

# ── Process Query ─────────────────────────────────────────────
if send_button and user_input.strip():
    # Add user message to history
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Show user message immediately
    st.markdown(f"""
        <div class="chat-message-user">
            👤 <strong>You:</strong><br>{user_input}
        </div>
    """, unsafe_allow_html=True)

    # Run agent with loading spinner
    with st.spinner("🤖 Agent is analyzing... please wait"):
        response = run_agent(user_input)

    # Add agent response to history
    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

    # Display response
    st.markdown(f"""
        <div class="chat-message-agent">
            🤖 <strong>Agent:</strong><br>{response}
        </div>
    """, unsafe_allow_html=True)

    # Clear selected query
    st.session_state.selected_query = ""

elif send_button and not user_input.strip():
    st.warning("⚠️ Please enter a query first!")

# ── Clear Chat Button ─────────────────────────────────────────
if st.session_state.messages:
    st.markdown("---")
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# ── Footer ────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #999; font-size: 0.8rem;'>
        Financial AI Agent for Market Insight | Built with Streamlit + Groq + FinBERT
    </div>
""", unsafe_allow_html=True)