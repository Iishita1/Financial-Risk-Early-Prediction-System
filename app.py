import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Financial Health Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CUSTOM CSS FOR STYLING
# ==========================================
st.markdown("""
<style>
    /* Global styles and background */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
        font-family: 'Inter', sans-serif;
    }
    
    /* Metrics Cards */
    div[data-testid="metric-container"] {
        background-color: #1E212B;
        border: 1px solid #333;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* Headings */
    h1, h2, h3 {
        color: #FFFFFF;
        font-weight: 600;
    }
    
    /* Alerts and Warnings */
    .alert-box {
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
        font-weight: 500;
    }
    .alert-danger {
        background-color: rgba(255, 75, 75, 0.2);
        border-left: 5px solid #ff4b4b;
        color: #ff4b4b;
    }
    .alert-warning {
        background-color: rgba(255, 164, 33, 0.2);
        border-left: 5px solid #ffa421;
        color: #ffa421;
    }
    .alert-success {
        background-color: rgba(33, 195, 84, 0.2);
        border-left: 5px solid #21c354;
        color: #21c354;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# RULE-BASED CALCULATION ENGINE
# ==========================================
def calculate_risk(income, expenses, debt, discretionary, spikes, missed_payments):
    """
    Simulates the logic from the FREWS notebook.
    Outputs a score between 0 and 1. (0 = Excellent, 1 = High Risk)
    """
    score = 0.0
    
    # 1. Savings Rate: (Income - Expenses) / Income
    savings = income - expenses
    savings_rate = savings / income if income > 0 else 0
    if savings_rate < 0.05:
        score += 0.30
    elif savings_rate < 0.15:
        score += 0.15
        
    # 2. Debt-to-Income Ratio (DTI)
    dti = debt / income if income > 0 else 0
    if dti > 0.40:
        score += 0.25
    elif dti > 0.25:
        score += 0.15
        
    # 3. Discretionary Ratio: Discretionary / Expenses
    disc_ratio = discretionary / expenses if expenses > 0 else 0
    if disc_ratio > 0.50:
        score += 0.10
        
    # 4. Spending Spikes
    if spikes:
        score += 0.15
        
    # 5. Missed Payments (Strong Signal)
    if missed_payments:
        score += 0.20
        
    # Ensure score bounds
    return max(0.0, min(1.0, score))


def get_gauge_chart(score, title="Financial Risk Score"):
    """Returns a Plotly gauge chart for the risk score"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score * 100,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'size': 24, 'color': 'white'}},
        number = {'suffix': "%", 'font': {'color': 'white'}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "rgba(0,0,0,0)"},  # Hidden bar, using steps instead
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 30], 'color': '#21c354'},    # Green
                {'range': [30, 70], 'color': '#ffa421'},   # Yellow
                {'range': [70, 100], 'color': '#ff4b4b'}   # Red
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': score * 100
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': "white", 'family': "Inter"},
        height=300,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig


# ==========================================
# MAIN APP
# ==========================================
def main():
    st.title("📊 Personal Financial Health Dashboard")
    st.markdown("### Early Warning System & Simulation Engine")
    st.write("Understand your financial standing, detect risks early, and simulate how life changes affect your wallet.")
    st.markdown("---")
    
    # -------------------------
    # SIDEBAR INPUTS
    # -------------------------
    st.sidebar.header("📝 Enter Your Details")
    st.sidebar.write("Input your current monthly financials.")
    
    current_income = st.sidebar.number_input("Monthly Income ($)", min_value=0, value=5000, step=100)
    current_debt = st.sidebar.number_input("Monthly Debt Payments ($) (e.g. Loans, Credit Cards)", min_value=0, value=1000, step=50)
    current_expenses = st.sidebar.number_input("Total Monthly Expenses ($) (including debt)", min_value=0, value=3500, step=100)
    current_disc = st.sidebar.number_input("Of which: Discretionary Spend ($) (e.g. Dining, Hobbies)", min_value=0, value=800, step=50)
    
    st.sidebar.markdown("### Behavioral Indicators")
    spikes = st.sidebar.checkbox("Recent sudden spikes in spending?")
    missed = st.sidebar.checkbox("Any missed/late payments recently?")
    
    # -------------------------
    # CURRENT STATUS SECTION
    # -------------------------
    # Calculate Current Score
    base_score = calculate_risk(current_income, current_expenses, current_debt, current_disc, spikes, missed)
    
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        st.plotly_chart(get_gauge_chart(base_score, "Current Risk Level"), use_container_width=True)
    
    with col2:
        st.subheader("💡 Financial Health Analysis")
        
        # Savings Rate logic
        savings_rate = (current_income - current_expenses) / current_income if current_income > 0 else 0
        if savings_rate >= 0.15:
            st.markdown(f'<div class="alert-box alert-success">✅ <b>Great Savings Rate!</b> You are saving {savings_rate*100:.1f}% of your income. Keep it up!</div>', unsafe_allow_html=True)
        elif savings_rate > 0:
            st.markdown(f'<div class="alert-box alert-warning">⚠️ <b>Low Savings Rate.</b> You are saving only {savings_rate*100:.1f}%. Aim for at least 15%.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="alert-box alert-danger">🚨 <b>Deficit Warning!</b> You are spending more than you earn.</div>', unsafe_allow_html=True)
            
        # DTI logic
        dti = current_debt / current_income if current_income > 0 else 0
        if dti <= 0.25:
            st.markdown(f'<div class="alert-box alert-success">✅ <b>Healthy Debt Levels.</b> Your Debt-to-Income ratio is {dti*100:.1f}%.</div>', unsafe_allow_html=True)
        elif dti <= 0.40:
            st.markdown(f'<div class="alert-box alert-warning">⚠️ <b>Elevated Debt Levels.</b> Your Debt-to-Income ratio is {dti*100:.1f}%. Monitor this closely.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="alert-box alert-danger">🚨 <b>High Debt Burden!</b> Your Debt-to-Income ratio is {dti*100:.1f}%. Consider paying down principal quickly.</div>', unsafe_allow_html=True)
            
        if missed:
            st.markdown(f'<div class="alert-box alert-danger">🚨 <b>Credit Impact.</b> Missed payments significantly impact your financial stability. Try to automate payments.</div>', unsafe_allow_html=True)

    # Key Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Income", f"${current_income:,.0f}")
    m2.metric("Expenses", f"${current_expenses:,.0f}")
    m3.metric("Free Cash Flow", f"${current_income - current_expenses:,.0f}")
    m4.metric("DTI Ratio", f"{dti*100:.1f}%")

    st.markdown("---")
    
    # -------------------------
    # WHAT-IF SIMULATOR
    # -------------------------
    st.subheader("🔮 What-If Simulation Engine")
    st.write("Use the sliders below to see how changes in your life could impact your financial risk level.")
    
    sim_col1, sim_col2 = st.columns([1, 1])
    
    with sim_col1:
        st.markdown("**Simulate Income Changes**")
        sim_income_change = st.slider("Income Change (%)", min_value=-50, max_value=50, value=0, step=5)
        
        st.markdown("**Simulate Expense Changes**")
        sim_expense_change = st.slider("Expense Change (%)", min_value=-50, max_value=50, value=0, step=5)
        
    with sim_col2:
        # Calculate Simulated values
        sim_income = current_income * (1 + (sim_income_change / 100))
        sim_expenses = current_expenses * (1 + (sim_expense_change / 100))
        # Keep debt constant for simulation unless explicitly changed, assume disc changes proportionally
        sim_disc = current_disc * (1 + (sim_expense_change / 100))
        
        sim_score = calculate_risk(sim_income, sim_expenses, current_debt, sim_disc, spikes, missed)
        
        # Display Gauge
        st.plotly_chart(get_gauge_chart(sim_score, "Simulated Risk Level"), use_container_width=True)

    # Simulation Summary
    score_diff = sim_score - base_score
    if score_diff > 0.05:
        st.error(f"⚠️ These changes would **INCREASE** your risk by {(score_diff*100):.1f} percentage points. Please be cautious.")
    elif score_diff < -0.05:
        st.success(f"✅ These changes would **DECREASE** your risk by {abs(score_diff*100):.1f} percentage points. Excellent plan!")
    else:
        st.info("ℹ️ These changes have a minimal impact on your overall risk profile.")

    # Footer
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: #888;'>Powered by Behavior-Driven Financial Risk Analytics</p>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
