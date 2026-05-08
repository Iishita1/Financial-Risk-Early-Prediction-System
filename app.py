"""
FINANCIAL HEALTH CHECK APP
Simple consumer app - no jargon, just results
"""

from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime
import pickle
import numpy as np

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

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

calc = FinancialHealthCalculator()

# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/calculate', methods=['POST'])
def calculate_risk():
    """
    Receive user data and return financial health assessment
    """
    try:
        data = request.get_json()
        result = calc.calculate_score(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/sample-data')
def get_sample_data():
    """Return sample data for demo"""
    return jsonify({
        'monthly_income': 5000,
        'monthly_expenses': 3200,
        'savings': 15000,
        'debts': 25000,
        'credit_score': 720,
        'employment_type': 'employed',
        'dependents': 1
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
