/**
 * Financial Health Check - Frontend Logic
 */

const form = document.getElementById('healthForm');
const resultsSection = document.getElementById('resultsSection');
const formSection = document.querySelector('.form-section');
const resetBtn = document.getElementById('resetBtn');

// ============================================================================
// EVENT LISTENERS
// ============================================================================

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    await submitForm();
});

resetBtn.addEventListener('click', resetForm);

// ============================================================================
// FUNCTIONS
// ============================================================================

async function submitForm() {
    // Get form data
    const formData = new FormData(form);
    const userData = {
        monthly_income: parseFloat(formData.get('monthly_income')),
        monthly_expenses: parseFloat(formData.get('monthly_expenses')),
        savings: parseFloat(formData.get('savings')),
        debts: parseFloat(formData.get('debts')),
        credit_score: parseFloat(formData.get('credit_score')),
        employment_type: formData.get('employment_type'),
        dependents: parseInt(formData.get('dependents'))
    };

    try {
        // Send to backend
        const response = await fetch('/api/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });

        if (!response.ok) {
            throw new Error('Failed to calculate health score');
        }

        const result = await response.json();
        displayResults(result);

    } catch (error) {
        alert('Error: ' + error.message);
    }
}

function displayResults(result) {
    // Hide form, show results
    formSection.style.display = 'none';
    resultsSection.style.display = 'block';

    // SCORE
    const scoreValue = document.getElementById('scoreValue');
    const scoreCircle = document.getElementById('scoreCircle');
    const riskText = document.getElementById('riskText');
    const riskDescription = document.getElementById('riskDescription');

    scoreValue.textContent = result.score;
    scoreCircle.className = 'score-circle ' + result.risk_level + '-level';
    riskText.textContent = result.risk_text;
    riskDescription.textContent = getRiskDescription(result.risk_level);

    // BREAKDOWN
    const breakdownGrid = document.getElementById('breakdownGrid');
    breakdownGrid.innerHTML = '';

    const categories = [
        { key: 'spending', label: 'Spending' },
        { key: 'savings', label: 'Savings' },
        { key: 'debt', label: 'Debt' },
        { key: 'credit', label: 'Credit' }
    ];

    categories.forEach(cat => {
        const value = result.breakdown[cat.key] || 0;
        const item = document.createElement('div');
        item.className = 'breakdown-item';
        item.innerHTML = `
            <span class="breakdown-label">${cat.label}</span>
            <span class="breakdown-value">${value}/25</span>
        `;
        breakdownGrid.appendChild(item);
    });

    // ISSUES
    const issuesList = document.getElementById('issuesList');
    issuesList.innerHTML = '';
    result.issues.forEach(issue => {
        const li = document.createElement('li');
        li.textContent = issue;
        issuesList.appendChild(li);
    });

    // ACTIONS
    const actionsList = document.getElementById('actionsList');
    actionsList.innerHTML = '';
    result.suggested_actions.forEach(action => {
        const li = document.createElement('li');
        li.textContent = action;
        actionsList.appendChild(li);
    });

    // STATS
    document.getElementById('statIncome').textContent = '$' + formatNumber(result.monthly_income);
    document.getElementById('statExpenses').textContent = '$' + formatNumber(result.monthly_expenses);
    
    const surplus = result.monthly_income - result.monthly_expenses;
    document.getElementById('statSurplus').textContent = '$' + formatNumber(surplus);
    
    const months = result.monthly_expenses > 0 ? 
        (result.savings / result.monthly_expenses).toFixed(1) : 
        '0';
    document.getElementById('statMonths').textContent = months + ' months';

    // Scroll to results
    setTimeout(() => {
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }, 100);
}

function getRiskDescription(level) {
    const descriptions = {
        'green': 'Your financial position is solid. Continue maintaining healthy spending habits, strong emergency reserves, and manageable debt levels. Focus on optimizing your investment strategy for long-term growth.',
        'yellow': 'Your finances show some areas requiring attention. Review your spending patterns, prioritize debt reduction, and strengthen your emergency fund. These improvements will enhance your overall financial stability.',
        'red': 'Your financial situation requires immediate action. High spending relative to income, insufficient savings, or significant debt levels are creating financial vulnerability. Implement changes now to prevent further deterioration.'
    };
    return descriptions[level] || '';
}

function formatNumber(num) {
    return Math.floor(num).toLocaleString('en-US');
}

function resetForm() {
    form.reset();
    formSection.style.display = 'block';
    resultsSection.style.display = 'none';
    window.scrollTo({ top: 0, behavior: 'smooth' });
}
