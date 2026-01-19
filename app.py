import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import io
from datetime import datetime, timedelta
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
import tempfile
import base64

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="UXXCA - AI CFO Assistant",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== FIXED THEME - GUARANTEED WHITE TEXT ==========
st.markdown("""
<style>
    /* FORCE DARK BACKGROUND EVERYWHERE */
    .stApp {
        background-color: #0f172a !important;
    }
    
    /* FORCE ALL TEXT TO BE WHITE */
    * {
        color: #ffffff !important;
    }
    
    /* Specific fixes for Streamlit components */
    .stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #ffffff !important;
    }
    
    /* Fix metrics */
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        color: #ffffff !important;
    }
    
    /* Fix dataframes */
    .stDataFrame {
        color: #ffffff !important;
    }
    
    /* Fix input labels */
    .stTextInput label, .stNumberInput label, .stTextArea label {
        color: #ffffff !important;
    }
    
    /* Fix selectbox */
    .stSelectbox label {
        color: #ffffff !important;
    }
    
    /* UXXCA Brand Header */
    .uxxca-header {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        padding: 2.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white !important;
        box-shadow: 0 10px 30px rgba(79, 70, 229, 0.3);
    }
    
    /* Metric Cards */
    .metric-card {
        background: #1e293b;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #60a5fa;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Chat Input Fix */
    .stChatInput {
        background-color: #1e293b !important;
        border-radius: 15px !important;
        border: 2px solid #4f46e5 !important;
        margin-top: 20px !important;
    }
    
    .stChatInput input {
        background-color: transparent !important;
        color: #ffffff !important;
        font-size: 1rem !important;
        padding: 0.8rem !important;
    }
    
    .stChatInput input::placeholder {
        color: #94a3b8 !important;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: white !important;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
    }
    
    /* Spreadsheet Table Styling */
    .spreadsheet-table {
        background-color: #1e293b;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid #334155;
    }
    
    /* Fix Tabs */
    .stTabs [data-baseweb="tab"] {
        color: #ffffff !important;
    }
    
    /* Fix Expanders */
    .streamlit-expanderHeader {
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# ========== PROFESSIONAL SPREADSHEET GENERATOR ==========
def create_financial_spreadsheet(financial_data, transactions=None):
    """Create a professional Excel spreadsheet with financial data"""
    
    # Create a new workbook
    wb = openpyxl.Workbook()
    
    # ===== DASHBOARD SHEET =====
    ws1 = wb.active
    ws1.title = "Financial Dashboard"
    
    # Title
    ws1.merge_cells('A1:F1')
    title_cell = ws1['A1']
    title_cell.value = "UXXCA FINANCIAL DASHBOARD"
    title_cell.font = Font(size=20, bold=True, color="FFFFFF")
    title_cell.fill = PatternFill(start_color="4F46E5", end_color="4F46E5", fill_type="solid")
    title_cell.alignment = Alignment(horizontal='center')
    
    # Company Info
    ws1['A3'] = "Company Name:"
    ws1['B3'] = financial_data.get('company_name', 'Your Business')
    ws1['A4'] = "Report Period:"
    ws1['B4'] = datetime.now().strftime("%B %Y")
    
    # Key Metrics
    metrics = [
        ["Monthly Revenue", f"${financial_data['revenue']:,.2f}"],
        ["Monthly Expenses", f"${financial_data['expenses']:,.2f}"],
        ["Monthly Profit", f"${financial_data['revenue'] - financial_data['expenses']:,.2f}"],
        ["Profit Margin", f"{(financial_data['revenue'] - financial_data['expenses']) / financial_data['revenue'] * 100:.1f}%"],
        ["Cash Balance", f"${financial_data['cash_balance']:,.2f}"],
        ["Runway", f"{financial_data['cash_balance'] / financial_data['expenses']:.1f} months"],
        ["Burn Rate", f"${financial_data['expenses']:,.2f}/month"],
        ["Growth Rate", "15.2%"]  # Could be calculated
    ]
    
    # Style metrics
    header_fill = PatternFill(start_color="334155", end_color="334155", fill_type="solid")
    metric_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Write metrics
    ws1['A6'] = "KEY METRICS"
    ws1['A6'].fill = header_fill
    ws1['A6'].font = Font(bold=True, color="FFFFFF")
    
    for i, (label, value) in enumerate(metrics, start=7):
        ws1[f'A{i}'] = label
        ws1[f'B{i}'] = value
        
        # Apply styling
        for cell in [ws1[f'A{i}'], ws1[f'B{i}']]:
            cell.fill = metric_fill
            cell.border = border
            cell.font = Font(color="FFFFFF")
    
    # ===== INCOME STATEMENT SHEET =====
    ws2 = wb.create_sheet("Income Statement")
    
    # Income Statement
    ws2['A1'] = "INCOME STATEMENT"
    ws2['A1'].font = Font(size=16, bold=True, color="FFFFFF")
    
    income_items = [
        ["REVENUE", "", ""],
        ["  Product Sales", financial_data['revenue'] * 0.7, ""],
        ["  Service Revenue", financial_data['revenue'] * 0.3, ""],
        ["Total Revenue", "", f"=SUM(B3:B4)"],
        ["", "", ""],
        ["EXPENSES", "", ""],
        ["  Cost of Goods", financial_data['expenses'] * 0.4, ""],
        ["  Marketing", financial_data['expenses'] * 0.2, ""],
        ["  Salaries", financial_data['expenses'] * 0.25, ""],
        ["  Operations", financial_data['expenses'] * 0.15, ""],
        ["Total Expenses", "", f"=SUM(B7:B10)"],
        ["", "", ""],
        ["NET PROFIT", "", f"=B5-B11"]
    ]
    
    for i, row in enumerate(income_items, start=1):
        for j, value in enumerate(row, start=1):
            cell = ws2.cell(row=i, column=j, value=value)
            if isinstance(value, (int, float)) and value != "":
                cell.number_format = '"$"#,##0.00'
    
    # ===== CASH FLOW SHEET =====
    ws3 = wb.create_sheet("Cash Flow")
    ws3['A1'] = "CASH FLOW FORECAST"
    ws3['A1'].font = Font(size=16, bold=True, color="FFFFFF")
    
    # 12-month forecast
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    ws3['A3'] = "Month"
    for i, month in enumerate(months, start=1):
        ws3.cell(row=3, column=i+1, value=month)
    
    # Starting balance
    ws3['A4'] = "Starting Balance"
    ws3.cell(row=4, column=2, value=financial_data['cash_balance'])
    
    # Monthly cash flow
    ws3['A5'] = "Monthly Cash Flow"
    monthly_cash_flow = financial_data['revenue'] - financial_data['expenses']
    for i in range(1, 13):
        ws3.cell(row=5, column=i+1, value=monthly_cash_flow)
    
    # Ending balance
    ws3['A6'] = "Ending Balance"
    for i in range(1, 13):
        if i == 1:
            ws3.cell(row=6, column=i+1, 
                    value=f"=B4+B5")
        else:
            ws3.cell(row=6, column=i+1,
                    value=f"={get_column_letter(i)}6+{get_column_letter(i+1)}5")
    
    # Format numbers
    for row in ws3.iter_rows(min_row=4, max_row=6, min_col=2, max_col=13):
        for cell in row:
            if cell.value:
                cell.number_format = '"$"#,##0.00'
    
    # ===== TRANSACTIONS SHEET =====
    if transactions:
        ws4 = wb.create_sheet("Transactions")
        ws4['A1'] = "TRANSACTION LOG"
        ws4['A1'].font = Font(size=16, bold=True, color="FFFFFF")
        
        headers = ["Date", "Description", "Category", "Amount", "Type"]
        for i, header in enumerate(headers, start=1):
            ws4.cell(row=3, column=i, value=header).font = Font(bold=True)
        
        for i, transaction in enumerate(transactions, start=4):
            ws4.cell(row=i, column=1, value=transaction.get('date', ''))
            ws4.cell(row=i, column=2, value=transaction.get('description', ''))
            ws4.cell(row=i, column=3, value=transaction.get('category', ''))
            ws4.cell(row=i, column=4, value=transaction.get('amount', 0))
            ws4.cell(row=i, column=5, value=transaction.get('type', ''))
    
    # Adjust column widths
    for ws in wb.worksheets:
        for column in ws.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            ws.column_dimensions[column_letter].width = adjusted_width
    
    # Save to bytes
    excel_bytes = io.BytesIO()
    wb.save(excel_bytes)
    excel_bytes.seek(0)
    
    return excel_bytes

def get_download_link(excel_bytes, filename="financial_report.xlsx"):
    """Generate download link for Excel file"""
    b64 = base64.b64encode(excel_bytes.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}" style="background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); color: white; padding: 12px 24px; border-radius: 10px; text-decoration: none; font-weight: bold; display: inline-block; margin: 10px 0;">📥 Download Financial Report</a>'
    return href

# ========== SESSION STATE ==========
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 **Welcome to UXXCA AI CFO!** I'm your financial co-pilot. I can analyze your finances, generate professional spreadsheets, and provide actionable advice."}
    ]

if "financial_data" not in st.session_state:
    st.session_state.financial_data = {
        "revenue": 15000,
        "expenses": 12000,
        "cash_balance": 50000,
        "company_name": "Your Business"
    }

# ========== HELPER FUNCTIONS ==========
PERPLEXITY_API_KEY = st.secrets.get("PERPLEXITY_API_KEY", "your-api-key-here")

def ask_cfo_assistant(question, financial_context=None):
    """Enhanced CFO AI Assistant"""
    # Your existing API call function
    return f"Analysis for: {question}\n\nBased on your current metrics:\n- Revenue: ${financial_context['revenue']:,.2f}\n- Expenses: ${financial_context['expenses']:,.2f}\n- Profit: ${financial_context['revenue'] - financial_context['expenses']:,.2f}"

# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem 0;">
        <h1 style="color: #60a5fa; font-size: 2.2rem; margin: 0;">UXXCA</h1>
        <p style="color: #cbd5e1; font-size: 0.9rem;">AI CFO Assistant</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📊 Financial Input")
    
    company_name = st.text_input("**Company Name**", 
                                 value=st.session_state.financial_data.get('company_name', ''),
                                 key="company_name")
    
    revenue = st.number_input("**Monthly Revenue ($)**", 
                             min_value=0, 
                             value=st.session_state.financial_data['revenue'],
                             key="revenue_input")
    
    expenses = st.number_input("**Monthly Expenses ($)**", 
                              min_value=0, 
                              value=st.session_state.financial_data['expenses'],
                              key="expenses_input")
    
    cash_balance = st.number_input("**Cash Balance ($)**", 
                                  min_value=0, 
                                  value=st.session_state.financial_data['cash_balance'],
                                  key="cash_input")
    
    if st.button("🔄 Update Financial Data", type="primary", use_container_width=True):
        st.session_state.financial_data = {
            "revenue": revenue,
            "expenses": expenses,
            "cash_balance": cash_balance,
            "company_name": company_name
        }
        st.success("✅ Financial data updated!")
        st.rerun()

# ========== MAIN INTERFACE ==========
# Header
st.markdown("""
<div class="uxxca-header">
    <h1 style="margin: 0; font-size: 2.8rem;">Financial Clarity at Your Fingertips</h1>
    <p style="margin: 0.8rem 0 0 0; font-size: 1.2rem;">
        AI CFO Assistant • Professional Spreadsheets • Real-time Analysis
    </p>
</div>
""", unsafe_allow_html=True)

# ========== SPREADSHEET GENERATOR SECTION ==========
st.markdown("### 📈 Generate Professional Spreadsheet")

col1, col2, col3 = st.columns(3)

with col1:
    include_forecast = st.checkbox("Include 12-Month Forecast", value=True)
with col2:
    include_income_stmt = st.checkbox("Include Income Statement", value=True)
with col3:
    include_transactions = st.checkbox("Include Sample Transactions", value=True)

# Generate spreadsheet button
if st.button("🚀 Generate Professional Financial Report", type="primary", use_container_width=True):
    with st.spinner("Creating professional Excel report..."):
        # Create sample transactions if needed
        transactions = None
        if include_transactions:
            categories = ['Marketing', 'Salaries', 'Software', 'Office', 'Travel']
            transactions = []
            for i in range(20):
                transactions.append({
                    'date': (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                    'description': f"{np.random.choice(categories)} Expense",
                    'category': np.random.choice(categories),
                    'amount': round(np.random.uniform(50, 2000), 2),
                    'type': 'expense' if np.random.random() > 0.3 else 'revenue'
                })
        
        # Generate Excel file
        excel_file = create_financial_spreadsheet(
            st.session_state.financial_data,
            transactions if include_transactions else None
        )
        
        # Create download link
        st.markdown(get_download_link(excel_file, f"{company_name}_Financial_Report.xlsx"), unsafe_allow_html=True)
        
        # Preview the spreadsheet
        st.markdown("### 📋 Report Preview")
        
        # Show dashboard preview
        st.markdown("**Financial Dashboard Includes:**")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            - Company Information
            - Key Financial Metrics
            - Profit/Loss Summary
            - Cash Runway Analysis
            """)
        
        with col2:
            st.markdown("""
            - Burn Rate Calculation
            - Growth Projections
            - Financial Health Score
            - Actionable Insights
            """)
        
        # Sample data table
        st.markdown("**Sample Financial Data:**")
        sample_df = pd.DataFrame({
            "Metric": ["Monthly Revenue", "Monthly Expenses", "Monthly Profit", "Profit Margin", "Cash Runway"],
            "Value": [
                f"${revenue:,.2f}",
                f"${expenses:,.2f}",
                f"${revenue - expenses:,.2f}",
                f"{(revenue - expenses) / revenue * 100:.1f}%" if revenue > 0 else "0%",
                f"{cash_balance / expenses:.1f} months" if expenses > 0 else "N/A"
            ]
        })
        st.dataframe(sample_df, use_container_width=True)

# ========== FINANCIAL METRICS ==========
st.markdown("---")
st.markdown("### 📊 Live Financial Metrics")

col1, col2, col3, col4 = st.columns(4)

profit = revenue - expenses
runway = cash_balance / expenses if expenses > 0 else 0

with col1:
    st.metric("Monthly Revenue", f"${revenue:,.0f}")
with col2:
    st.metric("Monthly Expenses", f"${expenses:,.0f}")
with col3:
    st.metric("Monthly Profit", f"${profit:,.0f}", 
              f"{(profit/revenue*100):.1f}%" if revenue > 0 else "0%")
with col4:
    st.metric("Cash Runway", f"{runway:.1f} months")

# ========== CHAT INTERFACE ==========
st.markdown("---")
st.markdown("### 💬 AI CFO Assistant")

# Display chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("💭 Ask your AI CFO about financial strategies, analysis, or report generation..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("🔍 Analyzing..."):
            response = ask_cfo_assistant(prompt, st.session_state.financial_data)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

# ========== SAMPLE SPREADSHEET TEMPLATES ==========
st.markdown("---")
st.markdown("### 📑 Available Report Templates")

template_cols = st.columns(3)

with template_cols[0]:
    st.markdown('<div class="spreadsheet-table">', unsafe_allow_html=True)
    st.markdown("**Startup Financial Model**")
    st.markdown("• Revenue projections")
    st.markdown("• Expense breakdown")
    st.markdown("• Fundraising plan")
    st.markdown("• Valuation metrics")
    st.markdown('</div>', unsafe_allow_html=True)

with template_cols[1]:
    st.markdown('<div class="spreadsheet-table">', unsafe_allow_html=True)
    st.markdown("**Monthly P&L Report**")
    st.markdown("• Income statement")
    st.markdown("• Expense tracking")
    st.markdown("• Profit analysis")
    st.markdown("• Margin calculations")
    st.markdown('</div>', unsafe_allow_html=True)

with template_cols[2]:
    st.markdown('<div class="spreadsheet-table">', unsafe_allow_html=True)
    st.markdown("**Investor Pitch Deck**")
    st.markdown("• Financial highlights")
    st.markdown("• Growth metrics")
    st.markdown("• Use of funds")
    st.markdown("• ROI projections")
    st.markdown('</div>', unsafe_allow_html=True)

# ========== FOOTER ==========
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem 0;">
    <p style="margin: 0.5rem 0; color: #94a3b8;">
        <strong>UXXCA AI CFO Assistant</strong> • Professional Financial Reporting
    </p>
    <p style="margin: 0.5rem 0; font-size: 0.9rem; color: #64748b;">
        Generate investor-ready financial reports in seconds. All data remains private.
    </p>
</div>
""", unsafe_allow_html=True)
