
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

# Get API keys from environment variables
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
        return "Email feature is disabled in demo mode. Please contact support."
    except:
        return "Email service unavailable."

# Sidebar
with st.sidebar:
    st.title("💰 UXXCA Finance Assistant")
    st.markdown("---")
    
    st.subheader("Quick Questions")
    questions = [
        "How to create a budget?",
        "Best investment for beginners?",
        "How to save for retirement?",
        "Tips to reduce debt?",
        "What is an emergency fund?",
        "How to improve credit score?",
        "Roth IRA vs Traditional IRA",
        "How to start investing?"
    ]
    
    # FIXED: Using enumerate to create unique keys
    for idx, q in enumerate(questions):
        if st.button(q, use_container_width=True, key=f"quick_q_{idx}"):
            st.session_state.messages.append({"role": "user", "content": q})
            with st.spinner("Thinking..."):
                response = ask_perplexity(q)
                st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    st.markdown("---")
    st.subheader("Tools")
    
    # Email feature with unique keys
    with st.expander("📧 Send Email"):
        email_to = st.text_input("To:", placeholder="recipient@example.com", key="email_to")
        email_subject = st.text_input("Subject:", placeholder="Financial Advice", key="email_subject")
        email_body = st.text_area("Message:", height=100, key="email_body")
        if st.button("Send Email", use_container_width=True, key="send_email_btn"):
            if email_to and email_subject and email_body:
                with st.spinner("Sending..."):
                    result = send_email(email_subject, email_body, email_to)
                    st.success(result)
            else:
                st.warning("Please fill all fields")
    
    st.markdown("---")
    
    # Clear chat button with unique key
    if st.button("🗑️ Clear Chat", use_container_width=True, key="clear_chat_btn"):
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

# Chat input with unique key
if prompt := st.chat_input("Ask me about finance...", key="main_chat_input"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            response = ask_perplexity(prompt)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

# Budget Calculator with unique keys
st.markdown("---")
st.subheader("💰 Budget Calculator")

col1, col2 = st.columns(2)
with col1:
    income = st.number_input("Monthly Income ($)", min_value=0, value=3000, key="income_input")
    housing = st.number_input("Housing ($)", min_value=0, value=1000, key="housing_input")
with col2:
    expenses = st.number_input("Other Expenses ($)", min_value=0, value=1500, key="expenses_input")
    savings_goal = st.number_input("Savings Goal ($)", min_value=0, value=500, key="savings_goal")

total_expenses = housing + expenses
savings = income - total_expenses

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Income", f"${income}")
with col2:
    st.metric("Expenses", f"${total_expenses}")
with col3:
    st.metric("Remaining", f"${savings}")

if savings < 0:
    st.error("⚠️ You're spending more than you earn!")
elif savings < savings_goal:
    st.warning(f"You're saving ${savings}, but your goal is ${savings_goal}")
else:
    st.success(f"✅ Great! You're meeting your savings goal of ${savings_goal}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; padding: 1rem;'>
        <small>💰 UXXCA Finance Assistant | General advice only</small>
    </div>
    """,
    unsafe_allow_html=True
)
