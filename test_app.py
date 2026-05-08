#!/usr/bin/env python3
"""
Test script to verify the financial health calculator works
"""

import sys
import json

# Import the calculator from app.py
sys.path.insert(0, '.')
from app import FinancialHealthCalculator

def test_calculator():
    """Test the financial health calculator"""
    
    calc = FinancialHealthCalculator()
    
    print("\n" + "="*70)
    print("  TESTING FINANCIAL HEALTH CALCULATOR")
    print("="*70)
    
    # Test Case 1: Good Financial Health
    print("\n\n✅ TEST 1: Good Financial Health")
    print("-" * 70)
    
    test_case_1 = {
        'monthly_income': 5000,
        'monthly_expenses': 2500,
        'savings': 25000,
        'debts': 5000,
        'credit_score': 780,
        'employment_type': 'employed',
        'dependents': 1
    }
    
    result_1 = calc.calculate_score(test_case_1)
    print(f"Score: {result_1['score']}/100")
    print(f"Status: {result_1['risk_level']} ({result_1['risk_text']})")
    print(f"Breakdown: {result_1['breakdown']}")
    print(f"Issues found: {len(result_1['issues'])}")
    for issue in result_1['issues'][:3]:
        print(f"  • {issue}")
    print(f"Suggested actions: {len(result_1['suggested_actions'])}")
    
    assert result_1['score'] >= 70, "Score should be 70+ for good health"
    assert result_1['risk_level'] == 'green', "Risk level should be green"
    print("✓ Test 1 PASSED")
    
    # Test Case 2: Fair Financial Health
    print("\n\n⚠️  TEST 2: Fair Financial Health")
    print("-" * 70)
    
    test_case_2 = {
        'monthly_income': 4000,
        'monthly_expenses': 2800,
        'savings': 8000,
        'debts': 15000,
        'credit_score': 680,
        'employment_type': 'employed',
        'dependents': 2
    }
    
    result_2 = calc.calculate_score(test_case_2)
    print(f"Score: {result_2['score']}/100")
    print(f"Status: {result_2['risk_level']} ({result_2['risk_text']})")
    print(f"Breakdown: {result_2['breakdown']}")
    print(f"Issues found: {len(result_2['issues'])}")
    for issue in result_2['issues'][:3]:
        print(f"  • {issue}")
    
    assert 50 <= result_2['score'] < 70, "Score should be 50-70 for fair health"
    assert result_2['risk_level'] == 'yellow', "Risk level should be yellow"
    print("✓ Test 2 PASSED")
    
    # Test Case 3: Poor Financial Health
    print("\n\n❌ TEST 3: Poor Financial Health")
    print("-" * 70)
    
    test_case_3 = {
        'monthly_income': 3000,
        'monthly_expenses': 2700,
        'savings': 1000,
        'debts': 50000,
        'credit_score': 520,
        'employment_type': 'self_employed',
        'dependents': 3
    }
    
    result_3 = calc.calculate_score(test_case_3)
    print(f"Score: {result_3['score']}/100")
    print(f"Status: {result_3['risk_level']} ({result_3['risk_text']})")
    print(f"Breakdown: {result_3['breakdown']}")
    print(f"Issues found: {len(result_3['issues'])}")
    for issue in result_3['issues'][:3]:
        print(f"  • {issue}")
    
    assert result_3['score'] < 50, "Score should be <50 for poor health"
    assert result_3['risk_level'] == 'red', "Risk level should be red"
    print("✓ Test 3 PASSED")
    
    # Test Case 4: Edge Case - Zero Income
    print("\n\n🔧 TEST 4: Edge Case - Zero/Low Values")
    print("-" * 70)
    
    test_case_4 = {
        'monthly_income': 0,
        'monthly_expenses': 1000,
        'savings': 5000,
        'debts': 20000,
        'credit_score': 600,
        'employment_type': 'employed',
        'dependents': 0
    }
    
    result_4 = calc.calculate_score(test_case_4)
    print(f"Score: {result_4['score']}/100")
    print(f"Status: {result_4['risk_level']} ({result_4['risk_text']})")
    print("✓ Test 4 PASSED (handled edge case)")
    
    # Summary
    print("\n" + "="*70)
    print("  ALL TESTS PASSED ✓")
    print("="*70)
    print(f"""
Calculator is working correctly!

Test Results Summary:
  • Test 1 (Good): Score {result_1['score']}/100 - {result_1['risk_text']}
  • Test 2 (Fair): Score {result_2['score']}/100 - {result_2['risk_text']}
  • Test 3 (Poor): Score {result_3['score']}/100 - {result_3['risk_text']}
  • Test 4 (Edge): Score {result_4['score']}/100 - {result_4['risk_text']}

Ready to deploy!
""")
    
    return True

if __name__ == '__main__':
    try:
        test_calculator()
        print("\n✅ All tests completed successfully!\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test failed: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
