import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import numpy as np
import os

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="UXXCA - AI CFO Assistant",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== FIXED THEME WITH PROPER CONTRAST ==========
st.markdown("""
<style>
    /* MAIN BACKGROUND - Dark for contrast */
    .main {
        background-color: #0f172a !important;
    }
    
    /* Fix ALL text to be visible */
    .stApp {
        background-color: #0f172a;
    }
    
    /* Force ALL text to be white/light */
    p, h1, h2, h3, h4, h5, h6, div, span, label, .stMarkdown, .stAlert, .stMetric, .stDataFrame {
        color: #f8fafc !important;
    }
    
    /* Specific metric fix */
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        color: #f8fafc !important;
    }
    
    /* UXXCA Brand Header - Enhanced visibility */
    .uxxca-header {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        padding: 2.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 10px 30px rgba(79, 70, 229, 0.3);
    }
    
    /* Custom Metric Cards - High contrast */
    .metric-card {
        background: #1e293b;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #60a5fa;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(96, 165, 250, 0.2);
    }
    
    /* Chat Interface - FIXED CONTRAST */
    .stChatMessage {
        background-color: #1e293b !important;
        border-radius: 15px;
        margin-bottom: 1rem;
        padding: 1.2rem;
        border: 1px solid #334155;
    }
    
    /* User message - Blue tint */
    [data-testid="stChatMessage"][aria-label="You"] {
        background-color: #1e3a8a !important;
        border-color: #2563eb;
    }
    
    /* Assistant message - Dark with purple tint */
    [data-testid="stChatMessage"][aria-label="UXXCA AI"] {
        background-color: #1e1b4b !important;
        border-color: #7c3aed;
    }
    
    /* FIX CHAT INPUT - Blend with theme */
    .stChatInput {
        background-color: #1e293b !important;
        border-radius: 15px !important;
        border: 2px solid #4f46e5 !important;
        padding: 0.5rem !important;
    }
    
    .stChatInput input {
        background-color: transparent !important;
        color: #f8fafc !important;
        font-size: 1rem !important;
        padding: 0.8rem !important;
    }
    
    .stChatInput input::placeholder {
        color: #94a3b8 !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: white !important;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(79, 70, 229, 0.4);
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #334155;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #4f46e5 !important;
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
    
    /* Graph containers */
    .graph-container {
        background: #1e293b;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 1px solid #334155;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1e293b;
        border-radius: 10px;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px;
        padding: 10px 20px;
        color: #94a3b8;
        margin: 0 5px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #4f46e5 !important;
        color: white !important;
    }
    
    /* Fix dataframes */
    .stDataFrame {
        background-color: #1e293b !important;
    }
    
    /* Fix expander */
    .streamlit-expanderHeader {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }
    
    /* Fix all Streamlit text containers */
    .element-container {
        color: #f8fafc !important;
    }
    
    /* Specific fix for metrics */
    div[data-testid="metric-container"] {
        background-color: #1e293b !important;
        padding: 1rem !important;
        border-radius: 10px !important;
        border: 1px solid #334155 !important;
    }
</style>
""", unsafe_allow_html=True)

# ========== SESSION STATE ==========
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 **Welcome to UXXCA AI CFO!** I'm your financial co-pilot. I can analyze your finances, plot insights, and provide actionable advice. Let's start by setting up your financial dashboard."}
    ]

if "financial_data" not in st.session_state:
    st.session_state.financial_data = {
        "revenue": 15000,
        "expenses": 12000,
        "cash_balance": 50000,
        "profit_margin": 0,
        "runway": 0
    }
    # Calculate initial values
    revenue = st.session_state.financial_data['revenue']
    expenses = st.session_state.financial_data['expenses']
    cash_balance = st.session_state.financial_data['cash_balance']
    st.session_state.financial_data['profit_margin'] = ((revenue - expenses) / revenue * 100) if revenue > 0 else 0
    st.session_state.financial_data['runway'] = cash_balance / expenses if expenses > 0 else 0

# ========== HELPER FUNCTIONS (Keep from previous code) ==========
PERPLEXITY_API_KEY = st.secrets.get("PERPLEXITY_API_KEY", "your-api-key-here")

def ask_cfo_assistant(question, financial_context=None):
    # ... (keep your existing ask_cfo_assistant function) ...
    return f"Analysis for: {question}"

def plot_cash_flow_forecast(revenue, expenses, cash_balance, months=12):
    # ... (keep your existing plotting functions) ...
    return go.Figure()

# ========== SIDEBAR - FIXED VISIBILITY ==========
with st.sidebar:
    # UXXCA Logo with better contrast
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem 0;">
        <h1 style="color: #60a5fa; font-size: 2.2rem; margin: 0; font-weight: 800;">UXXCA</h1>
        <p style="color: #cbd5e1; font-size: 0.9rem; margin-top: 0.2rem;">AI CFO Assistant</p>
        <div style="height: 2px; background: linear-gradient(90deg, transparent, #60a5fa, transparent); margin: 1rem 0;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📊 Financial Dashboard")
    
    with st.container():
        revenue = st.number_input("**Monthly Revenue ($)**", 
                                 min_value=0, 
                                 value=15000,
                                 help="Total monthly income",
                                 key="rev_input")
        
        expenses = st.number_input("**Monthly Expenses ($)**", 
                                  min_value=0, 
                                  value=12000,
                                  help="Total monthly costs",
                                  key="exp_input")
        
        cash_balance = st.number_input("**Current Cash Balance ($)**", 
                                      min_value=0, 
                                      value=50000,
                                      help="Available cash in bank",
                                      key="cash_input")
        
        if st.button("🔄 Update Dashboard", type="primary", use_container_width=True):
            profit = revenue - expenses
            profit_margin = (profit / revenue * 100) if revenue > 0 else 0
            runway = cash_balance / expenses if expenses > 0 else 0
            
            st.session_state.financial_data = {
                "revenue": revenue,
                "expenses": expenses,
                "cash_balance": cash_balance,
                "profit_margin": profit_margin,
                "runway": runway
            }
            st.success("✅ Dashboard updated!")
            st.rerun()

# ========== MAIN DASHBOARD - FIXED METRICS ==========
# Header
st.markdown("""
<div class="uxxca-header">
    <h1 style="margin: 0; font-size: 2.8rem; font-weight: 800;">Financial Clarity at Your Fingertips</h1>
    <p style="margin: 0.8rem 0 0 0; font-size: 1.2rem; opacity: 0.95;">
        Your AI CFO Assistant • Real-time Analysis • Actionable Insights
    </p>
</div>
""", unsafe_allow_html=True)

# Live Metrics - USING ST.METRIC FOR BETTER VISIBILITY
st.markdown("### 📈 Live Financial Dashboard")

col1, col2, col3, col4 = st.columns(4)

with col1:
    revenue = st.session_state.financial_data['revenue']
    st.metric(
        label="Monthly Revenue",
        value=f"${revenue:,.0f}",
        delta=f"${revenue*0.05:,.0f} (est. growth)" if revenue > 0 else None
    )

with col2:
    expenses = st.session_state.financial_data['expenses']
    st.metric(
        label="Monthly Expenses",
        value=f"${expenses:,.0f}",
        delta=f"-${expenses*0.03:,.0f} (target)" if expenses > 0 else None,
        delta_color="inverse"
    )

with col3:
    profit = revenue - expenses
    profit_color = "normal" if profit >= 0 else "inverse"
    st.metric(
        label="Monthly Profit",
        value=f"${profit:,.0f}",
        delta=f"{profit/revenue*100:.1f}%" if revenue > 0 else "0%",
        delta_color=profit_color
    )

with col4:
    runway = st.session_state.financial_data['runway']
    runway_status = "good" if runway >= 6 else "average" if runway >= 3 else "poor"
    status_icons = {"good": "✅", "average": "⚠️", "poor": "🚨"}
    st.metric(
        label="Runway",
        value=f"{runway:.1f} months",
        delta=status_icons[runway_status]
    )

# ========== CHAT INTERFACE - FIXED ==========
st.markdown("---")
st.markdown("### 💬 AI CFO Assistant")

# Display chat
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# CHAT INPUT - NOW VISIBLE AND THEMED
st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

# Custom chat input area
col1, col2, col3 = st.columns([1, 8, 1])
with col2:
    st.markdown("""
    <div style='background: #1e293b; padding: 0.5rem; border-radius: 15px; border: 2px solid #4f46e5;'>
    </div>
    """, unsafe_allow_html=True)
    
    # The actual chat input - styled to match
    if prompt := st.chat_input("💭 Ask your AI CFO about cash flow, runway, or financial strategy...", key="main_input"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("🔍 Analyzing your finances..."):
                response = ask_cfo_assistant(prompt, st.session_state.financial_data)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

# ========== QUICK ACTIONS ==========
st.markdown("---")
st.markdown("### 🚀 Quick Analysis Actions")

action_cols = st.columns(4)
with action_cols[0]:
    if st.button("📊 Cash Flow Analysis", use_container_width=True):
        st.session_state.messages.append({
            "role": "user", 
            "content": "Provide a detailed cash flow analysis and recommendations"
        })
        st.rerun()

with action_cols[1]:
    if st.button("🛡️ Runway Check", use_container_width=True):
        st.session_state.messages.append({
            "role": "user", 
            "content": f"Analyze my {runway:.1f} month runway and suggest improvements"
        })
        st.rerun()

with action_cols[2]:
    if st.button("💰 Profitability", use_container_width=True):
        st.session_state.messages.append({
            "role": "user", 
            "content": f"Analyze my profitability with {profit_margin:.1f}% margin"
        })
        st.rerun()

with action_cols[3]:
    if st.button("📈 Growth Plan", use_container_width=True):
        st.session_state.messages.append({
            "role": "user", 
            "content": "Create a 6-month growth plan based on current metrics"
        })
        st.rerun()

# ========== SAMPLE GRAPH ==========
st.markdown("---")
st.markdown("### 📊 Sample Financial Visualization")

# Create tabs for different views
tab1, tab2, tab3 = st.tabs(["Cash Flow Forecast", "Expense Breakdown", "Monthly Trends"])

with tab1:
    st.markdown('<div class="graph-container">', unsafe_allow_html=True)
    # Sample cash flow chart
    months = list(range(1, 13))
    cash_forecast = [50000 + i*3000 for i in range(12)]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months, y=cash_forecast,
        mode='lines+markers',
        name='Cash Forecast',
        line=dict(color='#60a5fa', width=4),
        marker=dict(size=8, color='#1d4ed8')
    ))
    
    fig.update_layout(
        title="💰 12-Month Cash Flow Projection",
        xaxis_title="Months",
        yaxis_title="Cash Balance ($)",
        template="plotly_dark",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f8fafc'),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ========== FOOTER ==========
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem 0; color: #94a3b8;">
    <p style="margin: 0.5rem 0; font-size: 1.1rem;">
        <strong>UXXCA AI CFO Assistant</strong> • Making Business Finance Effortless
    </p>
    <p style="margin: 0.5rem 0; font-size: 0.9rem;">
        This tool provides AI-powered insights. Always consult with financial professionals for major decisions.
    </p>
    <div style="display: flex; justify-content: center; gap: 2rem; margin-top: 1rem;">
        <span>🔒 Local Data Only</span>
        <span>📊 Real-time Analysis</span>
        <span>💡 Actionable Insights</span>
    </div>
</div>
""", unsafe_allow_html=True)
