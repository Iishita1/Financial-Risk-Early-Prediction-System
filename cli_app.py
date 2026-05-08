#!/usr/bin/env python3
"""
Financial Health Check - CLI Version (No Web UI)
Simple text-based tool for quick assessment
"""

from datetime import datetime

class FinancialHealthCLI:
    """Simple CLI version of financial health calculator"""
    
    def __init__(self):
        self.results = {}
    
    def clear_screen(self):
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        print("\n" + "="*60)
        print("  💰 FINANCIAL HEALTH CHECK (CLI Edition)")
        print("="*60)
        print("\nEnter your financial information below.")
        print("(Press Enter with no input to use sample data)\n")
    
    def get_input(self, prompt, default=None, input_type=float):
        """Get user input with optional default"""
        while True:
            try:
                user_input = input(prompt + ": ").strip()
                if not user_input and default is not None:
                    return default
                if not user_input:
                    print("  Please enter a value or use defaults")
                    continue
                return input_type(user_input)
            except ValueError:
                print(f"  Invalid input. Please enter a valid {input_type.__name__}")
    
    def get_sample_data(self):
        """Return sample data for demo"""
        return {
            'monthly_income': 5000,
            'monthly_expenses': 3200,
            'savings': 15000,
            'debts': 25000,
            'credit_score': 720,
            'employment_type': 'employed',
            'dependents': 1
        }
    
    def collect_data(self):
        """Collect user data"""
        print("INCOME & EXPENSES")
        print("-" * 40)
        monthly_income = self.get_input("  Monthly Income (take-home)", 5000)
        monthly_expenses = self.get_input("  Monthly Expenses", 3200)
        
        print("\nSAVINGS & DEBT")
        print("-" * 40)
        savings = self.get_input("  Savings/Emergency Fund", 15000)
        debts = self.get_input("  Total Debts", 25000)
        
        print("\nCREDIT & EMPLOYMENT")
        print("-" * 40)
        credit_score = self.get_input("  Credit Score (300-850)", 720)
        dependents = self.get_input("  Number of Dependents", 1, int)
        
        return {
            'monthly_income': monthly_income,
            'monthly_expenses': monthly_expenses,
            'savings': savings,
            'debts': debts,
            'credit_score': credit_score,
            'employment_type': 'employed',
            'dependents': dependents
        }
    
    def calculate_score(self, data):
        """Calculate financial health score"""
        score = 100
        issues = []
        
        monthly_income = data['monthly_income']
        monthly_expenses = data['monthly_expenses']
        savings = data['savings']
        debts = data['debts']
        credit_score = data['credit_score']
        dependents = data['dependents']
        
        # SPENDING (30 points)
        if monthly_income > 0:
            expense_ratio = monthly_expenses / monthly_income
            if expense_ratio > 0.8:
                score -= 25
                issues.append("💸 Spending is very high (>80% of income)")
            elif expense_ratio > 0.7:
                score -= 15
                issues.append("📊 Spending is above ideal (70-80% of income)")
            else:
                score -= 0
                issues.append("✅ Spending is in healthy range")
        
        # SAVINGS (25 points)
        if monthly_expenses > 0:
            months_covered = savings / monthly_expenses
            if months_covered >= 6:
                score -= 0
                issues.append("✅ Excellent savings (6+ months)")
            elif months_covered >= 3:
                score -= 5
                issues.append("👍 Good emergency fund (3-6 months)")
            elif months_covered >= 1:
                score -= 12
                issues.append("⚠️  Low savings (1-3 months) - build it up")
            else:
                score -= 25
                issues.append("🚨 Almost no savings - emergency fund needed")
        
        # DEBT (25 points)
        if monthly_income > 0:
            debt_ratio = debts / monthly_income
            if debt_ratio > 3:
                score -= 25
                issues.append("🔴 Very high debt (>3x income)")
            elif debt_ratio > 1.5:
                score -= 15
                issues.append("⚠️  Debt is moderate-high - pay it down")
            elif debt_ratio > 0.5:
                score -= 7
                issues.append("💭 Debt is manageable but could be lower")
            else:
                score -= 0
                issues.append("✅ Low debt relative to income")
        
        # CREDIT (20 points)
        if credit_score >= 750:
            score -= 0
            issues.append("✅ Excellent credit score (750+)")
        elif credit_score >= 700:
            score -= 8
            issues.append("👍 Good credit score (700-750)")
        elif credit_score >= 600:
            score -= 15
            issues.append("⚠️  Fair credit score - work on improving it")
        else:
            score -= 20
            issues.append("🚨 Poor credit score - major focus area")
        
        score = max(0, min(100, score))
        
        if score >= 70:
            status = 'GOOD'
            emoji = '🟢'
        elif score >= 50:
            status = 'FAIR'
            emoji = '🟡'
        else:
            status = 'AT RISK'
            emoji = '🔴'
        
        return {
            'score': score,
            'status': status,
            'emoji': emoji,
            'issues': issues,
            'data': data
        }
    
    def print_results(self, result):
        """Print results in nice format"""
        data = result['data']
        
        print("\n" + "="*60)
        print(f"  {result['emoji']} YOUR FINANCIAL HEALTH SCORE: {result['score']}/100")
        print(f"  Status: {result['status']}")
        print("="*60)
        
        print("\n📋 KEY FINDINGS")
        print("-" * 60)
        for i, issue in enumerate(result['issues'], 1):
            print(f"  {i}. {issue}")
        
        print("\n📊 YOUR NUMBERS")
        print("-" * 60)
        print(f"  Monthly Income:      ${data['monthly_income']:,.0f}")
        print(f"  Monthly Expenses:    ${data['monthly_expenses']:,.0f}")
        surplus = data['monthly_income'] - data['monthly_expenses']
        print(f"  Monthly Surplus:     ${surplus:,.0f}")
        print(f"  Savings:             ${data['savings']:,.0f}")
        
        if data['monthly_expenses'] > 0:
            months = data['savings'] / data['monthly_expenses']
            print(f"  Months of Savings:   {months:.1f} months")
        
        print(f"  Total Debt:          ${data['debts']:,.0f}")
        print(f"  Credit Score:        {data['credit_score']:.0f}")
        print(f"  Dependents:          {data['dependents']}")
        
        print("\n🎯 SUGGESTED ACTIONS")
        print("-" * 60)
        if result['score'] >= 70:
            actions = [
                "Increase monthly savings by 5-10%",
                "Consider investing for long-term growth",
                "Review and update insurance coverage"
            ]
        elif result['score'] >= 50:
            actions = [
                "Create a budget and track spending",
                "Pay down high-interest debt first",
                "Build emergency fund to 3-6 months of expenses"
            ]
        else:
            actions = [
                "Stop taking on new debt immediately",
                "Cut non-essential spending right away",
                "Consider speaking with a financial advisor",
                "Review all subscriptions and cancel unused ones"
            ]
        
        for i, action in enumerate(actions, 1):
            print(f"  {i}. {action}")
        
        print("\n" + "="*60)
        print("  💡 Tip: This is a general assessment tool.")
        print("  For personalized advice, consult a professional.")
        print("="*60 + "\n")
    
    def run(self):
        """Main run loop"""
        self.clear_screen()
        self.print_header()
        
        print("\nCalculating your financial health...\n")
        result = self.calculate_score(data)
        
        self.print_results(result)
        
        again = input("Check another scenario? (y/n): ").strip().lower()
        if again == 'y':
            self.run()
        else:
            print("Thank you for using Financial Health Check! 👋\n")

if __name__ == '__main__':
    app = FinancialHealthCLI()
    app.run()
