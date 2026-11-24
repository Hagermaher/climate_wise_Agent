"""Streamlit app: run with `streamlit run app.py`."""
import os
import time
import asyncio
import streamlit as st
from llama_index.core.llms import ChatMessage

from agent import build_index, build_agent, ask
from config import LOCATION_NAME
from dashboard import show_dashboard, show_carbon_calculator
from style import apply_style, show_header

st.set_page_config(page_title="ClimateWise", page_icon="🌍", layout="wide")
apply_style()
show_header(f"Climate change assistant with daily NASA POWER data for {LOCATION_NAME} (2015-2025)")

EXAMPLES = [
    "How does climate change affect agriculture?",
    "How did the average temperature change from 2015 to 2025?",
    "What were the hottest days in 2024?",
    "I use 300 kWh monthly and drive 100 km weekly. What is my footprint?",
]


@st.cache_resource(show_spinner="Loading knowledge base (first time only)...")
def get_index():
    return build_index()


def get_api_key():
    """Look in Streamlit secrets, then environment variables, then the sidebar box."""
    try:
        key = st.secrets["GROQ_API_KEY"]
    except Exception:
        key = os.getenv("GROQ_API_KEY")
    return key or st.sidebar.text_input("Groq API key", type="password")


def word_stream(text):
    """Show the answer word by word (typing effect)."""
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.03)


def show_chat():
    st.sidebar.header("Try these")
    for example in EXAMPLES:
        if st.sidebar.button(example):
            st.session_state["pending"] = example
    if st.sidebar.button("🗑️ Clear chat"):
        st.session_state["messages"] = []

    api_key = get_api_key()
    if not api_key:
        st.info("Enter your Groq API key in the sidebar to start.")
        return

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg.get("tools"):
                st.caption("🔧 Tools used: " + ", ".join(msg["tools"]))

    question = st.chat_input("Ask about climate change...")
    if "pending" in st.session_state:
        question = st.session_state.pop("pending")
    if not question:
        return

    # previous messages become the chat history for the agent
    history = [ChatMessage(role=m["role"], content=m["content"]) for m in st.session_state["messages"]]
    st.session_state["messages"].append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.status("ClimateWise is thinking...", expanded=False) as status:
            try:
                agent = build_agent(get_index(), api_key)
                answer, tools_used = asyncio.run(ask(agent, question, history))
                label = "Used: " + ", ".join(tools_used) if tools_used else "Answered"
                status.update(label=label, state="complete")
            except Exception as e:
                answer, tools_used = f"Something went wrong: {e}", []
                status.update(label="Error", state="error")
        st.write_stream(word_stream(answer))
        if tools_used:
            st.caption("🔧 Tools used: " + ", ".join(tools_used))

    st.session_state["messages"].append({"role": "assistant", "content": answer, "tools": tools_used})


# ---------- Pages ----------
page = st.sidebar.radio("Page", ["💬 Chat", "📊 Dashboard", "🌱 Carbon calculator"])
st.sidebar.divider()

if page == "💬 Chat":
    show_chat()
elif page == "📊 Dashboard":
    show_dashboard()
else:
    show_carbon_calculator()
