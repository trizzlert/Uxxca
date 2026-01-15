
# app.py
import streamlit as st
import requests
import datetime
import smtplib
from email.message import EmailMessage
import json
import time

# Page configuration
st.set_page_config(
    page_title="UXXCA Finance Assistant",
    page_icon="💰",
    layout="wide"
)

# API Configuration
PERPLEXITY_API_URL = 'https://api.perplexity.ai/chat/completions'
PERPLEXITY_API_KEY = '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'
CHAT_HISTORY_FILE = "bot_chat_history.txt"
YOUR_EMAIL = "trijal539@gmail.com"
YOUR_APP_PASSWORD = "trijla@12345"

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm UXXCA, your financial expert assistant. How can I help you with your finances today?"}
    ]

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Custom CSS for ChatGPT-like interface
st.markdown("""
<style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    
    .user-message {
        background-color: #f0f2f6;
        border-left: 4px solid #4a90e2;
    }
    
    .assistant-message {
        background-color: #e3f2fd;
        border-left: 4px solid #34a853;
    }
    
    .chat-container {
        max-width: 800px;
        margin: 0 auto;
    }
    
    .stTextInput > div > div > input {
        border-radius: 20px;
        padding: 10px 20px;
    }
    
    .stButton > button {
        border-radius: 20px;
        padding: 10px 30px;
        background-color: #4a90e2;
        color: white;
        border: none;
    }
    
    .stButton > button:hover {
        background-color: #357abd;
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
    """Query Perplexity API for financial advice"""
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Add financial context to improve relevance
    system_prompt = """You are UXXCA, a financial expert assistant specializing in:
    1. Personal Finance Management
    2. Investment Strategies
    3. Budget Planning
    4. Tax Advice
    5. Debt Management
    6. Retirement Planning
    7. Stock Market Insights
    8. Cryptocurrency Guidance
    9. Real Estate Investment
    10. Financial Risk Assessment
    
    Provide clear, practical, and actionable financial advice. 
    Break down complex topics. Use bullet points when helpful.
    Always prioritize user's financial safety and recommend consulting professionals for major decisions."""
    
    data = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Financial question: {question}"}
        ],
        "max_tokens": 1000,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(PERPLEXITY_API_URL, json=data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            answer = result['choices'][0]['message']['content']
            return answer
        else:
            return "I'm having trouble accessing financial data right now. Please try again shortly."
    except Exception as e:
        print(f"API Error: {e}")
        return "Connection error. Please check your internet connection."

def send_email(subject, body, to_addr):
    """Send email through Gmail"""
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = YOUR_EMAIL
    msg["To"] = to_addr
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(YOUR_EMAIL, YOUR_APP_PASSWORD)
            smtp.send_message(msg)
        return "Email sent successfully!"
    except Exception as e:
        print(f"Email error: {e}")
        return "Failed to send email. Please check your email configuration."

def log_history(user_input, bot_response):
    """Log conversation to file"""
    with open(CHAT_HISTORY_FILE, "a", encoding="utf-8") as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] USER: {user_input}\n")
        f.write(f"[{timestamp}] BOT: {bot_response}\n\n")

def get_quick_replies():
    """Return predefined financial questions for quick access"""
    return [
        "How to create a budget?",
        "Best investment options for beginners?",
        "How to save for retirement?",
        "Tips to reduce debt?",
        "Stock market basics",
        "Tax saving strategies",
        "Emergency fund planning",
        "Real estate investment tips"
    ]

# Sidebar
with st.sidebar:
    st.title("💰 UXXCA Finance Assistant")
    st.markdown("---")
    
    st.subheader("Quick Actions")
    
    # Email Feature
    with st.expander("📧 Send Financial Email"):
        email_to = st.text_input("To:", placeholder="recipient@example.com")
        email_subject = st.text_input("Subject:", placeholder="Financial Report/Advice")
        email_body = st.text_area("Message:", height=100)
        if st.button("Send Email", use_container_width=True):
            if email_to and email_subject and email_body:
                with st.spinner("Sending email..."):
                    result = send_email(email_subject, email_body, email_to)
                    st.success(result)
            else:
                st.warning("Please fill all fields")
    
    st.markdown("---")
    st.subheader("Common Questions")
    
    # Quick reply buttons
    for question in get_quick_replies():
        if st.button(f"❓ {question}", use_container_width=True, key=f"q_{question[:10]}"):
            st.session_state.messages.append({"role": "user", "content": question})
            with st.spinner("Thinking..."):
                response = ask_perplexity(question)
                st.session_state.messages.append({"role": "assistant", "content": response})
                log_history(question, response)
            st.rerun()
    
    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True, type="secondary"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Chat cleared! How can I help with your finances today?"}
        ]
        st.rerun()

# Main Chat Interface
st.title("💬 UXXCA Finance Chatbot")
st.markdown("*Your personal financial expert assistant*")

# Features showcase
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="feature-card"><h4>📊 Budgeting</h4><small>Smart spending plans</small></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="feature-card"><h4>📈 Investing</h4><small>Growth strategies</small></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="feature-card"><h4>💰 Saving</h4><small>Wealth accumulation</small></div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="feature-card"><h4>🏦 Debt Help</h4><small>Reduction strategies</small></div>', unsafe_allow_html=True)

st.markdown("---")

# Chat container
chat_container = st.container()

with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me about finance (e.g., 'How to save money?' or 'Investment advice')"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get assistant response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing your financial query..."):
            # Check for specific commands
            if prompt.lower().startswith("send email"):
                response = "Please use the sidebar email feature to send emails with proper formatting."
            elif "who are you" in prompt.lower():
                response = "I'm UXXCA, your dedicated financial expert assistant. I specialize in helping with budgeting, investments, savings, debt management, retirement planning, and all aspects of personal finance. I'm here to provide practical, actionable financial guidance."
            elif "who made you" in prompt.lower():
                response = "I was created to be your personal finance assistant, leveraging AI technology to provide financial insights and guidance. My goal is to help you make informed financial decisions."
            else:
                # Get response from Perplexity API
                response = ask_perplexity(prompt)
            
            # Display response
            st.markdown(response)
            
            # Add to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Log conversation
            log_history(prompt, response)

# Additional Features Section
st.markdown("---")
st.subheader("📋 Financial Tools")

tab1, tab2, tab3 = st.tabs(["💰 Budget Calculator", "📈 Investment Planner", "🎯 Financial Goals"])

with tab1:
    st.write("**Monthly Budget Calculator**")
    col1, col2 = st.columns(2)
    with col1:
        income = st.number_input("Monthly Income ($)", min_value=0, value=5000, step=100)
        housing = st.number_input("Housing ($)", min_value=0, value=1500, step=50)
        transportation = st.number_input("Transportation ($)", min_value=0, value=500, step=50)
    with col2:
        food = st.number_input("Food ($)", min_value=0, value=600, step=50)
        utilities = st.number_input("Utilities ($)", min_value=0, value=300, step=50)
        entertainment = st.number_input("Entertainment ($)", min_value=0, value=300, step=50)
    
    expenses = housing + transportation + food + utilities + entertainment
    savings = income - expenses
    
    st.metric("Total Expenses", f"${expenses}")
    st.metric("Remaining for Savings", f"${savings}")
    
    if savings < 0:
        st.error("⚠️ You're spending more than you earn! Consider reducing expenses.")
    elif savings < income * 0.2:
        st.warning("💰 Try to save at least 20% of your income for better financial health.")
    else:
        st.success("✅ Great! You have a healthy budget surplus.")

with tab2:
    st.write("**Investment Growth Projection**")
    principal = st.number_input("Initial Investment ($)", min_value=100, value=10000, step=500)
    years = st.slider("Investment Period (years)", 1, 30, 10)
    rate = st.slider("Expected Annual Return (%)", 1.0, 15.0, 7.0)
    
    future_value = principal * ((1 + rate/100) ** years)
    profit = future_value - principal
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Future Value", f"${future_value:,.2f}")
    with col2:
        st.metric("Total Profit", f"${profit:,.2f}")
    
    st.info(f"💡 **Tip**: Starting early with regular investments can significantly increase your returns through compound interest!")

with tab3:
    st.write("**Set Your Financial Goals**")
    goal = st.text_input("Financial Goal", placeholder="e.g., Save for down payment")
    target = st.number_input("Target Amount ($)", min_value=100, value=50000, step=1000)
    timeline = st.number_input("Timeline (months)", min_value=1, value=60, step=12)
    
    monthly_saving = target / timeline if timeline > 0 else 0
    
    st.metric("Monthly Saving Required", f"${monthly_saving:,.2f}")
    
    if st.button("Add Goal", use_container_width=True):
        st.success(f"✅ Goal '{goal}' added! Save ${monthly_saving:,.2f} monthly to reach ${target:,.0f} in {timeline} months.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; padding: 1rem;'>
        <small>💰 UXXCA Finance Assistant | Always consult with qualified professionals for major financial decisions</small><br>
        <small>This assistant provides general guidance, not personalized financial advice</small>
    </div>
    """,
    unsafe_allow_html=True
)  