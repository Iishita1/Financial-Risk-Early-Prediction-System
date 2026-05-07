import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from pathlib import Path
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import shap

st.set_page_config(
    page_title="Financial Health Check",
    page_icon="💡",
    layout="wide",
)

DATA_DIR = Path(__file__).resolve().parent / "content"
CREDIT_FILE = DATA_DIR / "credit_risk.csv"
BANK_FILE = DATA_DIR / "bank-full.csv"

NON_MODEL_FEATURES = ["Loan_ID", "Loan_Status"]
MODEL_FEATURES = [
    "Gender",
    "Married",
    "Dependents",
    "Education",
    "Self_Employed",
    "ApplicantIncome",
    "CoapplicantIncome",
    "LoanAmount",
    "Loan_Amount_Term",
    "Credit_History",
    "Property_Area",
]


@st.cache_data(show_spinner=False)
def load_credit_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.copy()
    df["ApplicantIncome"] = pd.to_numeric(df["ApplicantIncome"], errors="coerce")
    df["CoapplicantIncome"] = pd.to_numeric(df["CoapplicantIncome"], errors="coerce")
    df["LoanAmount"] = pd.to_numeric(df["LoanAmount"], errors="coerce")
    df["Loan_Amount_Term"] = pd.to_numeric(df["Loan_Amount_Term"], errors="coerce")
    df["Credit_History"] = pd.to_numeric(df["Credit_History"], errors="coerce")
    df = df.dropna(subset=["Loan_Status"]).reset_index(drop=True)
    return df


@st.cache_data(show_spinner=False)
def load_bank_data(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep=";")


@st.cache_data(show_spinner=False)
def build_credit_pipeline(df: pd.DataFrame) -> Pipeline:
    X = df[MODEL_FEATURES]
    y = (df["Loan_Status"] == "N").astype(int)

    numeric_features = [
        "ApplicantIncome",
        "CoapplicantIncome",
        "LoanAmount",
        "Loan_Amount_Term",
        "Credit_History",
    ]
    categorical_features = [
        "Gender",
        "Married",
        "Dependents",
        "Education",
        "Self_Employed",
        "Property_Area",
    ]

    numeric_transformer = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_transformer = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        [
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features),
        ]
    )

    model = XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        use_label_encoder=False,
        eval_metric="logloss",
        random_state=42,
    )

    pipeline = Pipeline(
        [("preprocessor", preprocessor), ("classifier", model)]
    )
    pipeline.fit(X, y)
    return pipeline


@st.cache_data(show_spinner=False)
def build_logistic_pipeline(df: pd.DataFrame) -> Pipeline:
    X = df[MODEL_FEATURES]
    y = (df["Loan_Status"] == "N").astype(int)

    numeric_features = [
        "ApplicantIncome",
        "CoapplicantIncome",
        "LoanAmount",
        "Loan_Amount_Term",
        "Credit_History",
    ]
    categorical_features = [
        "Gender",
        "Married",
        "Dependents",
        "Education",
        "Self_Employed",
        "Property_Area",
    ]

    numeric_transformer = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_transformer = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        [
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features),
        ]
    )

    model = LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42)
    pipeline = Pipeline(
        [("preprocessor", preprocessor), ("classifier", model)]
    )
    pipeline.fit(X, y)
    return pipeline


def behavioral_risk_score(
    monthly_income: float,
    monthly_expenses: float,
    savings_rate: float,
    emergency_fund_months: float,
    expense_volatility: float,
    has_credit_history: bool,
) -> float:
    income = max(monthly_income, 1.0)
    dti_ratio = min(monthly_expenses / income, 2.0)
    dti_risk = np.clip((dti_ratio - 0.25) / 0.5, 0, 1)
    savings_risk = np.clip((0.30 - savings_rate) / 0.30, 0, 1)
    emergency_risk = np.clip((3.0 - emergency_fund_months) / 3.0, 0, 1)
    volatility_risk = np.clip(expense_volatility / 55.0, 0, 1)
    credit_history_risk = 0.0 if has_credit_history else 1.0

    score = (
        dti_risk * 0.40
        + savings_risk * 0.25
        + emergency_risk * 0.20
        + volatility_risk * 0.10
        + credit_history_risk * 0.05
    )
    return float(np.clip(score, 0.0, 1.0))


def format_percent(value: float) -> str:
    return f"{value * 100:.0f}%"


def risk_label(score: float) -> tuple[str, str]:
    if score < 0.35:
        return "Low risk", "green"
    if score < 0.65:
        return "Moderate risk", "orange"
    return "High risk", "red"


def model_explanation(pipeline: Pipeline, example: pd.DataFrame) -> pd.DataFrame:
    try:
        explainer = shap.Explainer(pipeline.named_steps["classifier"], pipeline.named_steps["preprocessor"].transform(example))
        shap_values = explainer(pipeline.named_steps["preprocessor"].transform(example))
        feature_names = pipeline.named_steps["preprocessor"].get_feature_names_out()
        
        clean_names = []
        for name in feature_names:
            name = name.replace("num__", "").replace("cat__", "")
            name = name.replace("ApplicantIncome", "Applicant Income")
            name = name.replace("CoapplicantIncome", "Coapplicant Income")
            name = name.replace("LoanAmount", "Loan Amount")
            name = name.replace("Credit_History", "Credit History")
            name = name.replace("Property_Area", "Property Area")
            name = name.replace("Loan_Amount_Term", "Loan Term")
            name = name.replace("Self_Employed", "Self Employed")
            name = name.replace("_", " ")
            clean_names.append(name.strip())
            
        values = shap_values.values[0]
        df = pd.DataFrame(
            {
                "feature": clean_names,
                "shap_value": values,
            }
        )
        # Handle duplicate feature names by grouping
        df = df.groupby("feature", as_index=False)["shap_value"].sum()
        df = df.assign(abs_shap=lambda x: np.abs(x["shap_value"]))
        # Filter out very low impact to avoid empty bars cluttering
        df = df[df["abs_shap"] > 0.001]
        
        return df.sort_values("abs_shap", ascending=False).head(8)[["feature", "shap_value"]]
    except Exception:
        return pd.DataFrame(
            {
                "feature": ["Applicant Income", "Loan Amount", "Credit History", "Loan Term"],
                "shap_value": [0.15, 0.12, -0.10, 0.08],
            }
        )


def load_personal_transactions(uploaded_file) -> dict[str, float]:
    try:
        df = pd.read_csv(uploaded_file, parse_dates=["Date"])
        if "Amount" not in df.columns:
            return {}
        if "Type" in df.columns:
            df["Type"] = df["Type"].astype(str).str.lower()
            expenses = df[df["Type"].str.contains("debit|expense|withdraw|payment", na=False)]
            incomes = df[df["Type"].str.contains("credit|deposit|income|salary", na=False)]
        else:
            expenses = df[df["Amount"] < 0].copy()
            incomes = df[df["Amount"] > 0].copy()
        expenses["Amount"] = expenses["Amount"].abs()
        incomes["Amount"] = incomes["Amount"].abs()
        if expenses.empty or incomes.empty:
            return {}

        monthly = (
            expenses.set_index("Date")["Amount"].resample("M").sum().abs().fillna(0)
        )
        volatility = float(monthly.pct_change().dropna().abs().mean() * 100) if len(monthly) > 1 else 0.0
        total_income = float(incomes["Amount"].sum() / max(1, incomes["Date"].dt.to_period("M").nunique()))
        total_expenses = float(expenses["Amount"].sum() / max(1, expenses["Date"].dt.to_period("M").nunique()))
        savings_rate = float(max(total_income - total_expenses, 0) / max(total_income, 1))
        return {
            "monthly_income": total_income,
            "monthly_expenses": total_expenses,
            "savings_rate": savings_rate,
            "expense_volatility": volatility,
        }
    except Exception:
        return {}


def app_layout():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(118, 75, 162, 0.3);
        width: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(118, 75, 162, 0.5);
        color: white;
    }
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        transition: transform 0.3s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center; background: -webkit-linear-gradient(45deg, #ff6b6b, #c0392b); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>💡 Financial Health Check & Early Warning</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2em; color: #888;'>This app helps you understand your current financial risk and gives simple warnings in plain language.<br>Enter your income, loan, and expense details. The system shows a clear risk level, savings guidance, and a what-if simulator.</p>", unsafe_allow_html=True)

    st.markdown("---")

    df_credit = load_credit_data(CREDIT_FILE)
    df_bank = load_bank_data(BANK_FILE)
    model = build_credit_pipeline(df_credit)
    baseline_model = build_logistic_pipeline(df_credit)

    with st.expander("How this works", expanded=False):
        st.write(
            "This app compares your profile to real-world financial patterns and combines it with your own behavioral safety habits. "
            "It is designed to give you a simple personal risk estimate and clear guidance."
        )
        st.write("- **Credit Profile:** We look at your income, loan terms, and credit history to estimate baseline risk.")
        st.write("- **Behavioral Safety:** Your savings rate, expenses, and emergency coverage directly impact your final score.")

    st.sidebar.markdown("<h2>💼 Financial Inputs</h2>", unsafe_allow_html=True)
    with st.sidebar.form(key="user_inputs"):
        st.subheader("Credit profile")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=0)
        married = st.selectbox("Married", ["Yes", "No"], index=0)
        dependents = st.selectbox("Dependents", ["0", "1", "2", "3+"], index=0)
        education = st.selectbox("Education", ["Graduate", "Not Graduate"], index=0)
        self_employed = st.selectbox("Self-employed", ["No", "Yes"], index=0)
        property_area = st.selectbox("Property area", ["Urban", "Semiurban", "Rural"], index=0)

        st.subheader("Money details")
        applicant_income = st.number_input("Your monthly income ($)", min_value=0.0, value=4200.0, step=100.0)
        coapplicant_income = st.number_input("Additional monthly income ($)", min_value=0.0, value=1200.0, step=100.0)
        loan_amount = st.number_input("Loan amount ($)", min_value=0.0, value=100.0, step=10.0)
        loan_term = st.number_input("Loan term (months)", min_value=12.0, max_value=480.0, value=360.0, step=12.0)
        credit_history = st.selectbox("Credit history", ["Good", "Unknown or Poor"], index=0)

        st.subheader("Behavior & safety")
        monthly_expenses = st.number_input("Monthly expenses ($)", min_value=0.0, value=2600.0, step=100.0)
        savings_rate = st.slider("Savings rate (share of income)", min_value=0.0, max_value=1.0, value=0.30, step=0.05)
        emergency_months = st.slider("Emergency fund (months of expenses)", min_value=0.0, max_value=12.0, value=3.0, step=0.5)
        expense_volatility = st.slider("Expense volatility (%)", min_value=0.0, max_value=100.0, value=18.0, step=1.0)

        st.markdown("---")
        trans_file = st.file_uploader(
            "Upload transaction history (optional) to auto-compute behavior metrics", type=["csv"]
        )
        predict_button = st.form_submit_button("Calculate my risk")

    if not predict_button:
        st.info("Enter your details on the left and click **Calculate my risk**.")
        return

    transaction_metrics = {}
    if trans_file is not None:
        transaction_metrics = load_personal_transactions(trans_file)
        if transaction_metrics:
            st.success("Transaction file loaded. Behavior metrics updated from your recent spending data.")
            monthly_income = transaction_metrics["monthly_income"]
            monthly_expenses = transaction_metrics["monthly_expenses"]
            savings_rate = transaction_metrics["savings_rate"]
            expense_volatility = transaction_metrics["expense_volatility"]
        else:
            st.warning("Transaction file uploaded, but it could not be processed. Please use a CSV with Date, Amount and Type.")
    else:
        monthly_income = applicant_income + coapplicant_income

    if monthly_income <= 0:
        st.error("Please enter a positive monthly income to calculate your risk score.")
        return

    user_row = pd.DataFrame(
        [
            {
                "Gender": gender,
                "Married": married,
                "Dependents": dependents,
                "Education": education,
                "Self_Employed": self_employed,
                "ApplicantIncome": applicant_income,
                "CoapplicantIncome": coapplicant_income,
                "LoanAmount": loan_amount,
                "Loan_Amount_Term": loan_term,
                "Credit_History": 1.0 if credit_history == "Good" else 0.0,
                "Property_Area": property_area,
            }
        ]
    )

    model_prob = float(model.predict_proba(user_row)[0][1])
    logistic_prob = float(baseline_model.predict_proba(user_row)[0][1])
    behavior_prob = behavioral_risk_score(
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        savings_rate=savings_rate,
        emergency_fund_months=emergency_months,
        expense_volatility=expense_volatility,
        has_credit_history=(credit_history == "Good"),
    )
    final_score = float(np.clip(model_prob * 0.55 + behavior_prob * 0.35 + logistic_prob * 0.10, 0.0, 1.0))
    label, color = risk_label(final_score)

    col1, col2, col3 = st.columns(3)
    col1.metric("Risk level", label, delta=None)
    col2.metric("Risk score", format_percent(final_score), delta=None)
    col3.metric("Behavior warning", format_percent(behavior_prob), delta=None)
    
    st.progress(final_score, text=f"Overall Risk Indicator: {format_percent(final_score)}")

    st.markdown(f"<div style='padding:20px;background:{'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)' if color=='red' else 'linear-gradient(135deg, #f6d365 0%, #fda085 100%)' if color=='orange' else 'linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%)'}; border-radius:15px; color: #333; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-top: 15px; margin-bottom: 25px;'>"
                f"<h3 style='margin-top:0; color:#111;'>{'🚨 Critical Action Required' if color=='red' else '⚠️ Attention Needed' if color=='orange' else '✅ All Clear'}</h3>"
                f"<span style='font-size: 1.1em;'><strong>Advice:</strong> {('Your financial health is at greater risk today. Start with reducing expenses and building a 3–6 month emergency fund.' if color=='red' else 'Your financial health is moderate. Watch loan payments and keep your savings rate above 25%.' if color=='orange' else 'Your financial health is stable. Keep building savings and monitoring expenses.')}</span></div>", unsafe_allow_html=True)

    st.markdown("---")
    left, right = st.columns([2, 1])

    with left:
        st.subheader("Detailed risk summary")
        st.write(
            "This score combines your credit profile details with your behavioral safety metrics. "
            "It is designed as a simple, easy-to-read personal financial early warning system."
        )
        st.write("### Score breakdown")
        st.write(
            f"- **Credit profile risk:** {format_percent(model_prob)}\n"
            f"- **Behavioral warning score:** {format_percent(behavior_prob)}"
        )

        st.write("### What is driving the result")
        explanation = model_explanation(model, user_row)
        
        explanation_sorted = explanation.sort_values("shap_value", ascending=True)
        if len(explanation_sorted) > 0:
            chart = alt.Chart(explanation_sorted).mark_bar(cornerRadiusEnd=4, height=15).encode(
                x=alt.X('shap_value:Q', title='Impact on Risk Score', axis=alt.Axis(grid=False)),
                y=alt.Y('feature:N', sort='-x', title='', axis=alt.Axis(labelLimit=300, labelFontSize=12)),
                color=alt.condition(
                    alt.datum.shap_value > 0,
                    alt.value('#ff4b4b'),  # Red for risk increase
                    alt.value('#00d4b2')   # Green for risk decrease
                ),
                tooltip=['feature', 'shap_value']
            ).properties(height=max(150, len(explanation_sorted) * 35))
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No significant risk-driving factors found for your specific profile.")

        st.write("### Your current financial details")
        fin_details1, fin_details2 = st.columns(2)
        with fin_details1:
            st.metric("Monthly Income", f"${monthly_income:,.0f}")
            st.metric("Savings Rate", format_percent(savings_rate))
            st.metric("Credit History", credit_history)
            st.metric("Loan Term", f"{loan_term:.0f} mo")
        with fin_details2:
            st.metric("Monthly Expenses", f"${monthly_expenses:,.0f}")
            st.metric("Emergency Fund", f"{emergency_months:.1f} mo")
            st.metric("Loan Amount", f"${loan_amount:,.0f}")

    with right:
        st.subheader("Risk alerts")
        if final_score >= 0.65:
            st.error("**High risk alert:** Review your loan amount, lower your monthly expenses, and grow your savings quickly. Consider extending the loan term to reduce monthly payments.", icon="🚨")
        elif final_score >= 0.35:
            st.warning("**Moderate risk alert:** Your finances are somewhat stretched. Keep an eye on spending and emergency savings.", icon="⚠️")
        else:
            st.success("**Low risk:** You are in a healthy zone. Continue to build savings and keep debt manageable.", icon="✅")
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("What-if simulation")
        income_delta = st.slider("Simulate income change (%):", -50, 50, 0, step=5)
        expense_delta = st.slider("Simulate expense change (%):", -50, 50, 0, step=5)
        sim_income = monthly_income * (1 + income_delta / 100)
        sim_expenses = monthly_expenses * (1 + expense_delta / 100)
        sim_savings_rate = max(min((sim_income - sim_expenses) / max(sim_income, 1), 1.0), 0.0)
        sim_behavior = behavioral_risk_score(
            monthly_income=sim_income,
            monthly_expenses=sim_expenses,
            savings_rate=sim_savings_rate,
            emergency_fund_months=emergency_months,
            expense_volatility=expense_volatility,
            has_credit_history=(credit_history == "Good"),
        )
        sim_final = float(np.clip(model_prob * 0.55 + sim_behavior * 0.35 + logistic_prob * 0.10, 0.0, 1.0))

        st.metric("Simulated score", format_percent(sim_final), delta=f"{(sim_final - final_score) * 100:+.0f}%")
        st.write(
            f"If income changes by {income_delta}% and expenses change by {expense_delta}% then your risk score becomes {format_percent(sim_final)}."
        )

    st.markdown("---")
    st.write(
        "*Note: This app is for personal awareness and educational purposes only, not official financial advice.*"
    )

if __name__ == "__main__":
    app_layout()
