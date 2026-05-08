# 💰 Financial Health Check App

A **simple, consumer-friendly app** that assesses your financial health in plain English. No jargon. Just honest feedback and actionable steps.

## What It Does

1. **You enter your info**: Income, expenses, savings, debts, credit score
2. **App calculates**: Overall financial health score (0-100)
3. **You get**: 
   - Health score with status (Good/Fair/At Risk)
   - Breakdown by category (spending, savings, debt, credit)
   - Specific issues found
   - Next steps to improve

## Installation

### Option 1: Quick Start (Windows)

```bash
# 1. Install Python dependencies
pip install -r requirements-app.txt

# 2. Run the app
python app.py

# 3. Open browser to: http://localhost:5000
```

### Option 2: Using conda/venv

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # Mac/Linux

# Install requirements
pip install -r requirements-app.txt

# Run app
python app.py
```

## Features

✅ **No financial jargon** - Plain English explanations  
✅ **Instant scoring** - Get results immediately  
✅ **Actionable insights** - Know exactly what to improve  
✅ **Color-coded status** - Green/Yellow/Red risk levels  
✅ **Sample data** - Load demo data to see how it works  
✅ **Mobile friendly** - Works on phone, tablet, desktop  
✅ **Privacy** - All calculations happen in your browser (no data saved)

## What Gets Scored

**Spending (30 points)**
- Do you spend 50-70% of income? (Healthy range)

**Savings (25 points)**
- Do you have 3-6 months of expenses saved?

**Debt (25 points)**
- Is your debt under control? (Less than 3x income)

**Credit (20 points)**
- Is your credit score 700+? (Good range)

## Example Scenarios

### 🟢 Good Health (Score 70+)
- Monthly income: $5,000
- Monthly expenses: $3,000
- Savings: $20,000
- Debts: $10,000
- Credit: 750+

### 🟡 Fair Health (Score 50-70)
- Spending is slightly high (70-80% of income)
- Savings are okay but could be higher
- Some debt but manageable

### 🔴 At Risk (Score <50)
- Spending exceeds 80% of income
- Little to no emergency savings
- High debt relative to income
- Low credit score (<650)

## Questions?

- **Privacy**: All data stays in your browser. Nothing is sent to any server except the calculation request.
- **Accuracy**: This is a general screening tool, not financial advice. See a professional for personalized guidance.
- **Data**: No personal information is stored or logged.

---

**Built from**: Financial Risk Early Warning System ML model  
**Simplified for**: Normal people who just want honest financial feedback
