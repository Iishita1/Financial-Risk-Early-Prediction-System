"""
FINANCIAL HEALTH CHECK APP - Streamlit Version
Simple consumer app - no jargon, just results
Deployable on Streamlit Cloud
"""

import streamlit as st
import json
from datetime import datetime

# ============================================================================
# RISK CALCULATOR (Core Logic - No ML jargon)
# ============================================================================

class FinancialHealthCalculator:
    """
    Professional financial health assessment calculator.
    Evaluates spending, savings, debt, and credit metrics.
    """

    def __init__(self):
        self.risk_level_text = {
            'green': 'Strong Financial Position',
            'yellow': 'Moderate Concerns',
            'red': 'Action Required'
        }

    def calculate_score(self, user_data):
        """
        Calculate overall financial health score.
        Input: dict with user financial info
        Output: dict with score, category, and actionable insights
        """

        # Extract data
        monthly_income = float(user_data.get('monthly_income', 0))
        monthly_expenses = float(user_data.get('monthly_expenses', 0))
        savings = float(user_data.get('savings', 0))
        debts = float(user_data.get('debts', 0))
        credit_score = float(user_data.get('credit_score', 500))
        employment_type = user_data.get('employment_type', 'employed')
        dependents = int(user_data.get('dependents', 0))

        score = 100  # Start at perfect
        breakdown = {}
        issues = []

        # ──────────────────────────────────────────────────────────────
        # 1. SPENDING EFFICIENCY (30 points)
        # ──────────────────────────────────────────────────────────────
        if monthly_income > 0:
            expense_ratio = monthly_expenses / monthly_income
            savings_rate = (monthly_income - monthly_expenses) / monthly_income

            # Healthy if spending is 50-70% of income
            if expense_ratio > 0.8:
                deduction = 25
                issues.append("High expense-to-income ratio. Consider reviewing discretionary spending.")
            elif expense_ratio > 0.7:
                deduction = 15
                issues.append("Expense-to-income ratio is above optimal range. Target 50-70% of income.")
            elif expense_ratio < 0.3:
                deduction = 5
                issues.append("Expense data validation required. Unusually low spending relative to income.")
            else:
                deduction = 0
                issues.append("Spending is within optimal range relative to income.")

            score -= deduction
            breakdown['spending'] = 30 - deduction

        # ──────────────────────────────────────────────────────────────
        # 2. EMERGENCY FUND ADEQUACY (25 points)
        # ──────────────────────────────────────────────────────────────
        if monthly_income > 0:
            months_covered = savings / monthly_expenses if monthly_expenses > 0 else 0

            # Healthy: 3-6 months of expenses saved
            if months_covered >= 6:
                deduction = 0
                issues.append("Excellent emergency fund coverage (6+ months of expenses).")
            elif months_covered >= 3:
                deduction = 5
                issues.append("Adequate emergency fund in place (3-6 months coverage).")
            elif months_covered >= 1:
                deduction = 12
                issues.append("Emergency fund below recommended level. Target 3-6 months of expenses.")
            else:
                deduction = 25
                issues.append("Insufficient emergency savings. Priority: establish 3-month reserve.")

            score -= deduction
            breakdown['savings'] = 25 - deduction

        # ──────────────────────────────────────────────────────────────
        # 3. DEBT MANAGEMENT (25 points)
        # ──────────────────────────────────────────────────────────────
        if monthly_income > 0:
            debt_ratio = debts / monthly_income if monthly_income > 0 else 0

            # Healthy: < 1x income in debt
            if debt_ratio > 3:
                deduction = 25
                issues.append("Debt levels significantly exceed annual income. Debt reduction essential.")
            elif debt_ratio > 1.5:
                deduction = 15
                issues.append("Debt-to-income ratio elevated. Develop debt repayment strategy.")
            elif debt_ratio > 0.5:
                deduction = 7
                issues.append("Moderate debt levels. Consider accelerating repayment schedule.")
            else:
                deduction = 0
                issues.append("Debt levels well-managed relative to income.")

            score -= deduction
            breakdown['debt'] = 25 - deduction

        # ──────────────────────────────────────────────────────────────
        # 4. CREDITWORTHINESS (20 points)
        # ──────────────────────────────────────────────────────────────
        deduction = 0

        # Credit score assessment
        if credit_score < 300:
            deduction = 20
            issues.append("Credit score is critically low. Immediate action required for improvement.")
        elif credit_score < 600:
            deduction = 15
            issues.append("Credit score is subprime. This will impact loan rates and terms.")
        elif credit_score < 700:
            deduction = 8
            issues.append("Credit score is fair. Target score of 700+ for better loan terms.")
        elif credit_score >= 750:
            deduction = 0
            issues.append("Excellent credit profile with strong payment history.")

        # Employment stability modifier
        if employment_type == 'self_employed':
            deduction += 5
            issues.append("Self-employment status may impact lending qualification criteria.")

        score -= deduction
        breakdown['credit'] = 20 - deduction

        # ──────────────────────────────────────────────────────────────
        # 5. FAMILY FINANCIAL OBLIGATIONS
        # ──────────────────────────────────────────────────────────────
        if dependents > 0:
            dependents_per_income = dependents / (monthly_income / 1000) if monthly_income > 0 else 0
            if dependents_per_income > 2:
                issues.append("High dependent ratio relative to income. Ensure adequate insurance coverage.")

        # Clean up issues list
        issues = [i for i in issues if i is not None]

        # ──────────────────────────────────────────────────────────────
        # DETERMINE RISK LEVEL
        # ──────────────────────────────────────────────────────────────
        score = max(0, min(100, score))  # Clamp 0-100

        if score >= 70:
            risk_level = 'green'
            risk_text = 'Strong Financial Position'
        elif score >= 50:
            risk_level = 'yellow'
            risk_text = 'Moderate Concerns'
        else:
            risk_level = 'red'
            risk_text = 'Action Required'

        return {
            'score': int(score),
            'risk_level': risk_level,
            'risk_text': risk_text,
            'breakdown': breakdown,
            'issues': issues[:5],  # Top 5 findings
            'monthly_income': monthly_income,
            'monthly_expenses': monthly_expenses,
            'savings': savings,
            'debts': debts,
            'credit_score': credit_score,
            'suggested_actions': self._get_actions(score, risk_level, user_data)
        }

    def _get_actions(self, score, risk_level, user_data):
        """Return prioritized action items"""
        actions = []

        if risk_level == 'green':
            actions = [
                "Increase savings rate by 5-10% to accelerate wealth building",
                "Evaluate investment opportunities for long-term growth",
                "Review and optimize insurance coverage annually"
            ]
        elif risk_level == 'yellow':
            actions = [
                "Create detailed budget to track and categorize all spending",
                "Prioritize high-interest debt repayment in acceleration schedule",
                "Build emergency fund to 3-6 months of monthly expenses"
            ]
        else:  # red
            actions = [
                "Stop all non-essential spending and discretionary purchases immediately",
                "Suspend new debt accumulation; focus on existing obligations",
                "Consult with financial advisor or credit counselor for professional guidance",
                "Create aggressive debt reduction plan with specific payoff timeline"
            ]

        return actions

# ============================================================================
# STREAMLIT APP
# ============================================================================

def main():
    st.set_page_config(
        page_title="Financial Health Check",
        page_icon="💰",
        layout="wide"
    )

    st.title("💰 Financial Health Check")
    st.markdown("Get a quick assessment of your financial wellness. No jargon, just actionable insights.")

    # Initialize calculator
    calc = FinancialHealthCalculator()

    # Create two columns for input and results
    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("Your Financial Information")

        # Input fields
        monthly_income = st.number_input(
            "Monthly Income ($)",
            min_value=0.0,
            value=5000.0,
            step=100.0,
            help="Your total monthly take-home pay"
        )

        monthly_expenses = st.number_input(
            "Monthly Expenses ($)",
            min_value=0.0,
            value=3200.0,
            step=50.0,
            help="Total monthly spending on all expenses"
        )

        savings = st.number_input(
            "Emergency Savings ($)",
            min_value=0.0,
            value=15000.0,
            step=500.0,
            help="Money you can access quickly in an emergency"
        )

        debts = st.number_input(
            "Total Debts ($)",
            min_value=0.0,
            value=25000.0,
            step=1000.0,
            help="All outstanding loans, credit cards, etc."
        )

        credit_score = st.number_input(
            "Credit Score",
            min_value=300,
            max_value=850,
            value=720,
            step=1,
            help="Your current credit score (300-850)"
        )

        employment_type = st.selectbox(
            "Employment Type",
            options=['employed', 'self_employed', 'unemployed', 'retired'],
            index=0,
            help="Your current employment status"
        )

        dependents = st.number_input(
            "Number of Dependents",
            min_value=0,
            value=1,
            step=1,
            help="People who depend on you financially"
        )

        # Calculate button
        if st.button("Calculate My Financial Health", type="primary"):
            user_data = {
                'monthly_income': monthly_income,
                'monthly_expenses': monthly_expenses,
                'savings': savings,
                'debts': debts,
                'credit_score': credit_score,
                'employment_type': employment_type,
                'dependents': dependents
            }

            result = calc.calculate_score(user_data)

            # Store result in session state for display
            st.session_state.result = result

    with col2:
        st.header("Your Results")

        if 'result' in st.session_state:
            result = st.session_state.result

            # Score display
            score = result['score']
            risk_level = result['risk_level']

            # Color coding
            if risk_level == 'green':
                color = '🟢'
                bg_color = '#d4edda'
            elif risk_level == 'yellow':
                color = '🟡'
                bg_color = '#fff3cd'
            else:
                color = '🔴'
                bg_color = '#f8d7da'

            st.markdown(f"""
            <div style="background-color: {bg_color}; padding: 20px; border-radius: 10px; text-align: center;">
                <h2 style="color: #333; margin: 0;">{color} {result['risk_text']}</h2>
                <h1 style="color: #333; font-size: 48px; margin: 10px 0;">{score}/100</h1>
            </div>
            """, unsafe_allow_html=True)

            # Breakdown
            st.subheader("Score Breakdown")
            breakdown = result['breakdown']
            st.write(f"**Spending Efficiency:** {breakdown.get('spending', 0)}/30")
            st.write(f"**Emergency Savings:** {breakdown.get('savings', 0)}/25")
            st.write(f"**Debt Management:** {breakdown.get('debt', 0)}/25")
            st.write(f"**Credit Profile:** {breakdown.get('credit', 0)}/20")

            # Key Issues
            if result['issues']:
                st.subheader("Key Findings")
                for issue in result['issues']:
                    st.write(f"• {issue}")

            # Suggested Actions
            if result['suggested_actions']:
                st.subheader("Recommended Actions")
                for action in result['suggested_actions']:
                    st.write(f"• {action}")

        else:
            st.info("Enter your information and click 'Calculate' to see your financial health assessment.")

if __name__ == "__main__":
    main()