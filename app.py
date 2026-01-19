import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import numpy as np
import os

# ========== PAGE CONFIG & THEME ==========
st.set_page_config(
    page_title="UXXCA - AI CFO Assistant",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== CUSTOM THEME (UXXCA Brand Colors) ==========
st.markdown("""
<style>
    /* Main Theme */
    .main {
        background-color: #0f172a;
    }
    
    /* UXXCA Brand Header */
    .uxxca-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    
    /* Custom Metric Cards */
    .metric-card {
        background: #1e293b;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #3b82f6;
        margin: 0.5rem 0;
    }
    
    /* Chat Bubbles */
    .stChatMessage {
        padding: 1rem;
        border-radius: 15px;
        margin-bottom: 1rem;
    }
    
    [data-testid="stChatMessage"] {
        padding: 1rem;
    }
    
    /* User message styling */
    [data-testid="stChatMessage"][aria-label="You"] {
        background-color: #1e3a8a;
        color: white;
    }
    
    /* Assistant message styling */
    [data-testid="stChatMessage"][aria-label="UXXCA AI"] {
        background-color: #1e293b;
        color: #e2e8f0;
        border: 1px solid #334155;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #0f172a;
    }
    
    /* Graph containers */
    .graph-container {
        background: #1e293b;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    /* Custom tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b;
        border-radius: 5px 5px 0 0;
        padding: 10px 20px;
        color: #94a3b8;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# ========== SESSION STATE INITIALIZATION ==========
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Welcome to **UXXCA AI CFO**! I'm your financial co-pilot. I can analyze your finances, plot insights, and provide actionable advice. Let's start by setting up your financial dashboard."}
    ]

if "financial_data" not in st.session_state:
    st.session_state.financial_data = {
        "revenue": 0,
        "expenses": 0,
        "cash_balance": 0,
        "profit_margin": 0,
        "runway": 0
    }

if "transactions" not in st.session_state:
    st.session_state.transactions = []

if "show_financial_input" not in st.session_state:
    st.session_state.show_financial_input = True

# ========== API CONFIGURATION ==========
PERPLEXITY_API_KEY = st.secrets.get("PERPLEXITY_API_KEY", "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")
PERPLEXITY_API_URL = 'https://api.perplexity.ai/chat/completions'

# ========== HELPER FUNCTIONS ==========
def ask_cfo_assistant(question, financial_context=None):
    """Enhanced CFO AI Assistant with financial context"""
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Build context string
    if financial_context:
        revenue = financial_context.get('revenue', 0)
        expenses = financial_context.get('expenses', 0)
        cash_balance = financial_context.get('cash_balance', 0)
        profit = revenue - expenses
        runway = cash_balance / expenses if expenses > 0 else 0
        
        context_str = f"""
        You are analyzing a business with these metrics:
        - Monthly Revenue: ${revenue:,.2f}
        - Monthly Expenses: ${expenses:,.2f}
        - Monthly Profit/Loss: ${profit:,.2f}
        - Current Cash Balance: ${cash_balance:,.2f}
        - Runway (months): {runway:.1f}
        - Profit Margin: {(profit/revenue*100 if revenue>0 else 0):.1f}%
        """
    else:
        context_str = "You are UXXCA's AI CFO assistant. Ask for specific financial data if needed."
    
    system_prompt = f"""You are UXXCA's AI CFO - an expert, actionable financial co-pilot for founders.
    {context_str}
    
    GUIDELINES:
    1. Be SPECIFIC and DATA-DRIVEN. Reference the numbers provided.
    2. Explain the 'why' behind financial concepts.
    3. Provide 2-3 actionable recommendations.
    4. Identify risks and opportunities.
    5. Use bullet points for clarity when listing items.
    6. Keep responses concise but comprehensive.
    7. Always end with a clear next step question.
    
    FORMAT:
    - Start with a 1-sentence summary
    - Break down key metrics
    - Provide actionable insights
    - End with a suggested next action
    """
    
    data = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        "max_tokens": 800,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(PERPLEXITY_API_URL, json=data, headers=headers, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        return "⚠️ Unable to fetch analysis. Please try again."
    except Exception:
        return "🔧 Service temporarily unavailable. Please check your connection."

def generate_sample_data():
    """Generate sample transaction data for demo"""
    categories = ['Marketing', 'Salaries', 'Software', 'Office', 'Travel', 'Services']
    dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
    
    transactions = []
    for i in range(30):
        category = np.random.choice(categories)
        amount = np.random.uniform(50, 2000)
        transaction_type = 'expense' if np.random.random() > 0.3 else 'revenue'
        
        if transaction_type == 'revenue':
            amount = np.random.uniform(1000, 10000)
            category = 'Client Payment'
        
        transactions.append({
            'date': dates[i],
            'description': f'{category} Transaction',
            'amount': round(amount, 2),
            'type': transaction_type,
            'category': category
        })
    
    return pd.DataFrame(transactions)

# ========== GRAPH PLOTTING FUNCTIONS ==========
def plot_cash_flow_forecast(revenue, expenses, cash_balance, months=12):
    """Plot cash flow forecast"""
    months_list = list(range(1, months + 1))
    forecast = []
    current_cash = cash_balance
    
    for month in months_list:
        current_cash += (revenue - expenses)
        forecast.append(current_cash)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=months_list,
        y=forecast,
        mode='lines+markers',
        name='Cash Forecast',
        line=dict(color='#3b82f6', width=3),
        marker=dict(size=8)
    ))
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.5)
    
    fig.update_layout(
        title="💰 12-Month Cash Flow Forecast",
        xaxis_title="Months",
        yaxis_title="Cash Balance ($)",
        template="plotly_dark",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        hovermode='x unified'
    )
    
    return fig

def plot_expense_breakdown():
    """Plot expense breakdown from transactions"""
    if len(st.session_state.transactions) == 0:
        df = generate_sample_data()
    else:
        df = pd.DataFrame(st.session_state.transactions)
    
    expense_df = df[df['type'] == 'expense']
    
    if len(expense_df) == 0:
        return None
    
    category_totals = expense_df.groupby('category')['amount'].sum().reset_index()
    
    fig = px.pie(
        category_totals,
        values='amount',
        names='category',
        title='📊 Expense Breakdown by Category',
        hole=0.3,
        color_discrete_sequence=px.colors.sequential.Plasma
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(line=dict(color='#1e293b', width=2))
    )
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    
    return fig

def plot_monthly_trend():
    """Plot monthly revenue vs expenses trend"""
    if len(st.session_state.transactions) == 0:
        df = generate_sample_data()
    else:
        df = pd.DataFrame(st.session_state.transactions)
    
    df['month'] = pd.to_datetime(df['date']).dt.to_period('M').astype(str)
    
    monthly_data = df.groupby(['month', 'type']).agg({'amount': 'sum'}).reset_index()
    
    # Create pivot table
    pivot_data = monthly_data.pivot(index='month', columns='type', values='amount').fillna(0)
    
    fig = go.Figure()
    
    if 'revenue' in pivot_data.columns:
        fig.add_trace(go.Bar(
            x=pivot_data.index,
            y=pivot_data['revenue'],
            name='Revenue',
            marker_color='#10b981'
        ))
    
    if 'expense' in pivot_data.columns:
        fig.add_trace(go.Bar(
            x=pivot_data.index,
            y=pivot_data['expense'],
            name='Expenses',
            marker_color='#ef4444'
        ))
    
    fig.update_layout(
        title="📈 Monthly Revenue vs Expenses",
        xaxis_title="Month",
        yaxis_title="Amount ($)",
        barmode='group',
        template="plotly_dark",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        hovermode='x unified'
    )
    
    return fig

def plot_runway_analysis(cash_balance, monthly_expenses):
    """Plot runway analysis with scenarios"""
    if monthly_expenses == 0:
        return None
    
    current_runway = cash_balance / monthly_expenses
    
    # Create scenarios
    scenarios = {
        'Current': current_runway,
        'Reduce 10%': cash_balance / (monthly_expenses * 0.9),
        'Reduce 20%': cash_balance / (monthly_expenses * 0.8),
        'Increase Cash 20%': (cash_balance * 1.2) / monthly_expenses
    }
    
    fig = go.Figure()
    
    colors = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6']
    
    for i, (scenario, runway) in enumerate(scenarios.items()):
        fig.add_trace(go.Bar(
            x=[scenario],
            y=[runway],
            name=scenario,
            marker_color=colors[i],
            text=[f'{runway:.1f} months'],
            textposition='outside'
        ))
    
    # Add target line (6 months recommended)
    fig.add_hline(y=6, line_dash="dash", line_color="green", 
                  annotation_text="Recommended Minimum", 
                  annotation_position="top right")
    
    fig.update_layout(
        title="🛡️ Runway Analysis - Different Scenarios",
        yaxis_title="Months of Runway",
        showlegend=False,
        template="plotly_dark",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    return fig

# ========== SIDEBAR ==========
with st.sidebar:
    # UXXCA Logo Section
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h1 style="color: #667eea; font-size: 2rem; margin: 0;">UXXCA</h1>
        <p style="color: #94a3b8; font-size: 0.9rem;">AI CFO Assistant</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Financial Input Section
    with st.expander("📊 **Input Financial Data**", expanded=st.session_state.show_financial_input):
        revenue = st.number_input("Monthly Revenue ($)", 
                                 min_value=0, 
                                 value=15000,
                                 help="Total monthly income")
        
        expenses = st.number_input("Monthly Expenses ($)", 
                                  min_value=0, 
                                  value=12000,
                                  help="Total monthly costs")
        
        cash_balance = st.number_input("Current Cash Balance ($)", 
                                      min_value=0, 
                                      value=50000,
                                      help="Available cash in bank")
        
        if st.button("Update Financial Dashboard", type="primary", use_container_width=True):
            st.session_state.financial_data = {
                "revenue": revenue,
                "expenses": expenses,
                "cash_balance": cash_balance,
                "profit_margin": ((revenue - expenses) / revenue * 100) if revenue > 0 else 0,
                "runway": cash_balance / expenses if expenses > 0 else 0
            }
            st.success("✅ Dashboard updated!")
            st.session_state.show_financial_input = False
            st.rerun()
    
    st.markdown("---")
    
    # Quick Analysis Buttons
    st.subheader("🚀 Quick Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Cash Flow", use_container_width=True):
            st.session_state.messages.append({
                "role": "user", 
                "content": "Analyze my cash flow and provide recommendations"
            })
            st.rerun()
    
    with col2:
        if st.button("Runway", use_container_width=True):
            st.session_state.messages.append({
                "role": "user", 
                "content": "Analyze my financial runway and suggest improvements"
            })
            st.rerun()
    
    if st.button("Profitability", use_container_width=True):
        st.session_state.messages.append({
            "role": "user", 
            "content": "Analyze my profitability and margins"
        })
        st.rerun()
    
    if st.button("Risk Assessment", use_container_width=True):
        st.session_state.messages.append({
            "role": "user", 
            "content": "What are my top 3 financial risks?"
        })
        st.rerun()
    
    st.markdown("---")
    
    # Graph Selection
    st.subheader("📈 Generate Graphs")
    
    graph_options = st.multiselect(
        "Select visualizations:",
        ["Cash Flow Forecast", "Expense Breakdown", "Monthly Trend", "Runway Analysis"],
        default=["Cash Flow Forecast"]
    )
    
    if st.button("Generate Selected Graphs", use_container_width=True):
        st.session_state.selected_graphs = graph_options
        st.rerun()
    
    st.markdown("---")
    
    # Data Management
    st.subheader("⚙️ Data")
    
    if st.button("Load Sample Data", use_container_width=True):
        st.session_state.transactions = generate_sample_data().to_dict('records')
        st.success("📁 Sample data loaded!")
        st.rerun()
    
    if st.button("Clear Chat", use_container_width=True, type="secondary"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Chat cleared! Ready for your next financial analysis."}
        ]
        st.rerun()

# ========== MAIN INTERFACE ==========
# Header Section
st.markdown("""
<div class="uxxca-header">
    <h1 style="margin: 0; font-size: 2.5rem;">Financial Clarity at Your Fingertips</h1>
    <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;">
        Your AI CFO Assistant • Real-time Analysis • Actionable Insights
    </p>
</div>
""", unsafe_allow_html=True)

# Dashboard Metrics
st.subheader("📊 Live Financial Dashboard")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="margin: 0; color: #94a3b8; font-size: 0.9rem;">Monthly Revenue</h3>
        <h2 style="margin: 0; color: #10b981;">${st.session_state.financial_data['revenue']:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="margin: 0; color: #94a3b8; font-size: 0.9rem;">Monthly Expenses</h3>
        <h2 style="margin: 0; color: #ef4444;">${st.session_state.financial_data['expenses']:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

with col3:
    profit = st.session_state.financial_data['revenue'] - st.session_state.financial_data['expenses']
    profit_color = "#10b981" if profit >= 0 else "#ef4444"
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="margin: 0; color: #94a3b8; font-size: 0.9rem;">Monthly Profit</h3>
        <h2 style="margin: 0; color: {profit_color};">${profit:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

with col4:
    runway = st.session_state.financial_data['runway']
    runway_color = "#10b981" if runway >= 6 else "#f59e0b" if runway >= 3 else "#ef4444"
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="margin: 0; color: #94a3b8; font-size: 0.9rem;">Runway</h3>
        <h2 style="margin: 0; color: {runway_color};">{runway:.1f} months</h2>
    </div>
    """, unsafe_allow_html=True)

# Chat Interface Section
st.subheader("💬 AI CFO Assistant")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask your AI CFO about your finances..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate AI response with financial context
    with st.chat_message("assistant"):
        with st.spinner("🔍 Analyzing your finances..."):
            response = ask_cfo_assistant(prompt, st.session_state.financial_data)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

# ========== GRAPH VISUALIZATION SECTION ==========
st.markdown("---")
st.subheader("📈 Interactive Financial Visualizations")

# Check if graphs are selected, otherwise show default
selected_graphs = getattr(st.session_state, 'selected_graphs', ["Cash Flow Forecast"])

# Create tabs for different graphs
if selected_graphs:
    tabs = st.tabs(selected_graphs)
    
    for i, graph_type in enumerate(selected_graphs):
        with tabs[i]:
            if graph_type == "Cash Flow Forecast":
                fig = plot_cash_flow_forecast(
                    st.session_state.financial_data['revenue'],
                    st.session_state.financial_data['expenses'],
                    st.session_state.financial_data['cash_balance']
                )
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Add insights
                    with st.expander("💡 Cash Flow Insights"):
                        st.markdown("""
                        **Key Takeaways:**
                        - This forecast assumes consistent revenue and expenses
                        - The red line indicates zero cash balance (critical point)
                        - Consider seasonality and one-time costs in real scenarios
                        
                        **Action Items:**
                        1. Update with actual monthly variations
                        2. Factor in planned investments
                        3. Set cash buffer targets
                        """)
            
            elif graph_type == "Expense Breakdown":
                fig = plot_expense_breakdown()
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show expense data
                    if len(st.session_state.transactions) > 0:
                        expense_df = pd.DataFrame(st.session_state.transactions)
                        expense_df = expense_df[expense_df['type'] == 'expense']
                        if len(expense_df) > 0:
                            st.dataframe(
                                expense_df[['date', 'category', 'amount']].sort_values('amount', ascending=False),
                                use_container_width=True
                            )
            
            elif graph_type == "Monthly Trend":
                fig = plot_monthly_trend()
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Add trend analysis
                    with st.expander("📊 Trend Analysis"):
                        st.markdown("""
                        **How to Read This Chart:**
                        - **Green bars** = Revenue
                        - **Red bars** = Expenses
                        - **Ideal pattern**: Green consistently higher than red
                        
                        **Growth Indicators:**
                        - Increasing revenue trend
                        - Controlled expense growth
                        - Expanding profit margins
                        """)
            
            elif graph_type == "Runway Analysis":
                fig = plot_runway_analysis(
                    st.session_state.financial_data['cash_balance'],
                    st.session_state.financial_data['expenses']
                )
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Runway recommendations
                    with st.expander("🛡️ Runway Recommendations"):
                        current_runway = st.session_state.financial_data['runway']
                        
                        if current_runway < 3:
                            st.error("🚨 **CRITICAL**: Runway below 3 months. Immediate action required!")
                            st.markdown("""
                            **Emergency Actions:**
                            1. Cut all non-essential expenses immediately
                            2. Accelerate accounts receivable collection
                            3. Explore emergency funding options
                            4. Consider owner salary reduction
                            """)
                        elif current_runway < 6:
                            st.warning("⚠️ **WARNING**: Runway below 6-month safety net")
                            st.markdown("""
                            **Recommended Actions:**
                            1. Reduce discretionary spending by 20%
                            2. Renegotiate vendor contracts
                            3. Delay non-critical hires
                            4. Focus on high-margin products/services
                            """)
                        else:
                            st.success("✅ **HEALTHY**: Runway above 6 months")
                            st.markdown("""
                            **Strategic Actions:**
                            1. Reinvest in growth opportunities
                            2. Build cash reserves
                            3. Consider strategic acquisitions
                            4. Invest in team development
                            """)

# ========== FOOTER ==========
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 2rem 0;">
    <p style="margin: 0.5rem 0;">💰 <strong>UXXCA AI CFO Assistant</strong> • Making Business Finance Effortless</p>
    <p style="margin: 0.5rem 0; font-size: 0.9rem;">This tool provides AI-powered insights. Always consult with financial professionals for major decisions.</p>
    <p style="margin: 0.5rem 0; font-size: 0.8rem; opacity: 0.7;">Data is stored locally in your session • No information is permanently saved</p>
</div>
""", unsafe_allow_html=True)
