"""Custom CSS: animated header, fade-in messages, hover effects."""
import streamlit as st

CSS = """
<style>
@keyframes gradientMove {
  0% {background-position: 0% 50%;}
  50% {background-position: 100% 50%;}
  100% {background-position: 0% 50%;}
}
@keyframes float {
  0%, 100% {transform: translateY(0);}
  50% {transform: translateY(-8px);}
}
@keyframes fadeIn {
  from {opacity: 0; transform: translateY(10px);}
  to {opacity: 1; transform: translateY(0);}
}

.hero {
  background: linear-gradient(-45deg, #0f766e, #16a34a, #0ea5e9, #0f766e);
  background-size: 400% 400%;
  animation: gradientMove 12s ease infinite;
  border-radius: 16px;
  padding: 20px 26px;
  display: flex;
  align-items: center;
  gap: 18px;
  margin-bottom: 14px;
}
.hero .globe {font-size: 3rem; animation: float 3s ease-in-out infinite;}
.hero h1 {margin: 0; padding: 0; font-size: 2rem; color: white;}
.hero p {margin: 2px 0 0 0; color: white; opacity: 0.92;}

[data-testid="stChatMessage"] {animation: fadeIn 0.5s ease; border-radius: 14px;}
[data-testid="stMetric"] {
  background: rgba(22, 163, 74, 0.08);
  border: 1px solid rgba(22, 163, 74, 0.3);
  padding: 12px 16px;
  border-radius: 12px;
  animation: fadeIn 0.6s ease;
}
.stButton > button {transition: all 0.2s ease; border-radius: 10px;}
.stButton > button:hover {transform: translateY(-2px); box-shadow: 0 4px 10px rgba(0, 0, 0, 0.18);}
</style>
"""


def apply_style():
    st.markdown(CSS, unsafe_allow_html=True)


def show_header(subtitle: str):
    st.markdown(
        f'<div class="hero"><div class="globe">🌍</div>'
        f'<div><h1>ClimateWise</h1><p>{subtitle}</p></div></div>',
        unsafe_allow_html=True,
    )
