from dotenv import load_dotenv
import streamlit as st
import os

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
SERP_API_KEY = os.getenv("SERP_API_KEY") or st.secrets.get("SERP_API_KEY")

MODEL_NAME = "llama-3.3-70b-versatile"

RESPONSE_MODES = {
    "Concise": "Give short and clear medical advice.",
    "Detailed": "Give detailed medical explanations and guidance."
}