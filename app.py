
# app.py

import streamlit as st
import requests
import datetime
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="UXXCA Finance Assistant",
    page_icon="💰",
    layout="wide"
)

# Get API keys from environment variables (SAFER)
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "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")
YOUR_EMAIL = os.getenv("YOUR_EMAIL", "trijal539@gmail.com")
YOUR_APP_PASSWORD = os.getenv("YOUR_APP_PASSWORD", "trijla@12345")

PERPLEXITY_API_URL = 'https://api.perplexity.ai/chat/completions'
CHAT_HISTORY_FILE = "bot_chat_history.txt"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm UXXCA, your financial expert assistant. How can I help you with your finances today?"}
    ]

# Custom CSS
st.markdown("""
<style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    
    .stButton > button {
        border-radius: 20px;
        padding: 10px 30px;
        background-color: #4a90e2;
        color: white;
        border: none;
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
        border-left: 4px solid #4a90e2;
    }
</style>
""", unsafe_allow_html=True)

# Helper Functions
def ask_perplexity(question):
    """Query Perplexity API"""
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    system_prompt = """You are UXXCA, a financial expert assistant. Provide clear, practical financial advice."""
    
    data = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(PERPLEXITY_API_URL, json=data, headers=headers, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return "I'm having trouble accessing financial data. Please try again."
    except:
        return "I can't connect to my knowledge base right now. Please check your connection."

def send_email(subject, body, to_addr):
    """Send email - Simplified for demo"""
    try:
        # For demo purposes - in production, implement proper email
        return "Email feature is disabled in demo mode. Please contact support."
    except:
        return "Email service unavailable."

# Sidebar
with st.sidebar:
    st.title("💰 UXXCA Finance")
    st.markdown("---")
    
    st.subheader("Quick Questions")
    questions = [
        "How to create a budget?",
        "Best investment for beginners?",
        "How to save for retirement?",
        "Tips to reduce debt?"
    ]
    
    for q in questions:
        if st.button(q, use_container_width=True, key=f"btn_{q[:5]}"):
            st.session_state.messages.append({"role": "user", "content": q})
            with st.spinner("Thinking..."):
                response = ask_perplexity(q)
                st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "Chat cleared! How can I help with your finances today?"}
        ]
        st.rerun()

# Main Chat Interface
st.title("💬 UXXCA Finance Chatbot")
st.markdown("*Your personal financial assistant*")

# Display chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me about finance..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            response = ask_perplexity(prompt)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

# Simple Calculator
st.markdown("---")
st.subheader("💰 Quick Budget Calculator")

col1, col2 = st.columns(2)
with col1:
    income = st.number_input("Monthly Income", min_value=0, value=3000)
with col2:
    expenses = st.number_input("Monthly Expenses", min_value=0, value=2000)

savings = income - expenses
st.metric("Monthly Savings", f"${savings}")

if savings < 0:
    st.error("You're spending more than you earn!")
elif savings > 0:
    st.success(f"You can save ${savings} per month")

