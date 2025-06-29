import streamlit as st
import pandas as pd
import pickle as pkl
import matplotlib.pyplot as plt

# Load model
gb = pkl.load(open('gb.pkl', 'rb'))

# Configure page
st.set_page_config(page_title="Loan Prediction", layout="wide")

# CSS for centering button
st.markdown("""
    <style>
        .centered-button button {
            display: block;
            margin: 2rem auto;
            padding: 0.6rem 2rem;
            font-size: 18px;
            background-color: #4CAF50 !important;
            color: white !important;
            border: none;
            border-radius: 8px;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "predict_clicked" not in st.session_state:
    st.session_state.predict_clicked = False
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Applicant"
if "started" not in st.session_state:
    st.session_state.started = False

# ------------------------- Welcome Page -------------------------
if not st.session_state.started:
    st.title("🏦 Loan Approval Prediction")
    st.markdown("""
        <h2 style='text-align: center; color: #4CAF50;'>Welcome to Loan Approval Prediction</h2>
        <p style='text-align: center;'>Check your loan eligibility in seconds using our smart prediction system.</p>
    """, unsafe_allow_html=True)

    st.markdown('<div class="centered-button">', unsafe_allow_html=True)
    if st.button("🚀 Start"):
        st.session_state.started = True
        st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------- Main App -------------------------
if st.session_state.started:
    def switch_tab(tab_name):
        st.session_state.active_tab = tab_name

    tab_names = ["📝 Applicant Info", "📊 Loan Result"]
    tabs = st.tabs(tab_names)

    # ------------------------- Input Tab -------------------------
    with tabs[0]:
        st.header("Enter Applicant Information")

        with st.expander("🧍 Personal Information", expanded=True):
            col1, col2 = st.columns(2)
            age = col1.number_input("Age", min_value=18.0, step=1.0, key="age")
            income = col2.number_input("Income (Rs)", min_value=0.0, step=0.01, key="income")

            col3, col4 = st.columns(2)
            emp_exp = col3.number_input("Employment Experience (years)", min_value=0.0, step=0.1, key="emp_exp")
            credit_score = col4.number_input("Credit Score", min_value=300.0, max_value=900.0, step=1.0, key="credit_score")

            cred_hist_len = st.number_input("Credit History Length (years)", min_value=0.0, step=0.1, key="cred_hist_len")

            gender = st.selectbox("Gender", ['Male', 'Female'], key="gender")
            education = st.selectbox("Education Level", ['Master', 'High School', 'Bachelor', 'Associate', 'Doctorate'], key="education")
            ownership = st.selectbox("Home Ownership", ['RENT', 'OWN', 'MORTGAGE', 'OTHER'], key="ownership")

        with st.expander("💸 Loan Details", expanded=True):
            col5, col6 = st.columns(2)
            loan_amt = col5.number_input("Loan Amount Requested (Rs)", min_value=0.0, step=0.01, key="loan_amt")
            int_rate = col6.number_input("Interest Rate (%)", min_value=0.0, step=0.01, key="int_rate")

            percent_income = st.number_input("Loan as % of Income", min_value=0.0, step=0.01, key="percent_income")
            purpose = st.selectbox("Loan Purpose",
                                ['PERSONAL', 'EDUCATION', 'MEDICAL', 'VENTURE', 'HOMEIMPROVEMENT', 'DEBTCONSOLIDATION'],
                                key="purpose")

            previous_loan_default = st.selectbox("Previous Loan Defaults", ['Yes', 'No'], key="previous_loan_default")

        if st.button("🚀 Predict Loan Approval"):
            st.session_state.predict_clicked = True
            switch_tab("Result")

    # ------------------------- Encoding -------------------------
    gender_code = 1 if gender == "Male" else 0
    education_map = {'Doctorate': 0, 'Associate': 1, 'Bachelor': 2, 'High School': 3, 'Master': 4}
    education_code = education_map[education]
    purpose_map = {'DEBTCONSOLIDATION': 0, 'EDUCATION': 1, 'HOMEIMPROVEMENT': 2, 'MEDICAL': 3, 'PERSONAL': 4, 'VENTURE': 5}
    purpose_code = purpose_map[purpose]
    ownership_map = {'MORTGAGE': 0, 'OTHER': 1, 'OWN': 2, 'RENT': 3}
    ownership_code = ownership_map[ownership]
    previous_loan_default_code = 1 if previous_loan_default == "Yes" else 0

    # ------------------------- Prediction Tab -------------------------
    with tabs[1]:
        st.header("Prediction Result")

        if st.session_state.predict_clicked:
            pred_data = pd.DataFrame([[age, income, emp_exp, loan_amt, int_rate, percent_income, cred_hist_len, credit_score,
                                    gender_code, education_code, purpose_code, ownership_code, previous_loan_default_code]],
                                    columns=['person_age', 'person_income', 'person_emp_exp', 'loan_amnt', 'loan_int_rate',
                                            'loan_percent_income', 'cb_person_cred_hist_length', 'credit_score',
                                            'Gender_Encoded', 'person_education_Encoded', 'loan_intent_Encoded',
                                            'person_home_ownership_Encoded', 'previous_loan_defaults_on_file_Encoded'])

            predict = gb.predict(pred_data)[0]

            st.markdown("---")

            if predict == 1:
                st.success("✅ **Loan Approved**")
            else:
                st.error("❌ **Loan Rejected**")

            with st.expander("📋 Applicant Summary", expanded=True):
                st.markdown(f"""
                **🧑 Gender:** {gender}  
                **🎓 Education:** {education}  
                **🏠 Home Ownership:** {ownership}  
                **💳 Credit Score:** {credit_score}  
                **💼 Experience:** {emp_exp} years  
                **📜 Credit History:** {cred_hist_len} years  
                **⚠️ Previous Defaults:** {previous_loan_default}
                """)

            with st.expander("💼 Loan Summary", expanded=True):
                st.markdown(f"""
                **💰 Loan Amount:** ₹{loan_amt:,.2f}  
                **💸 Income:** ₹{income:,.2f}  
                **📈 Interest Rate:** {int_rate:.2f}%  
                **📊 Loan % of Income:** {percent_income:.2f}%  
                **🎯 Purpose:** {purpose.title()}
                """)

            with st.expander("🔍 Credit Score Analysis"):
                if credit_score >= 750:
                    credit_level = "Excellent"
                elif credit_score >= 700:
                    credit_level = "Good"
                elif credit_score >= 650:
                    credit_level = "Fair"
                else:
                    credit_level = "Poor"

                st.info(f"Your credit score of **{credit_score}** is considered **{credit_level}**.")

            with st.expander("📉 Loan-to-Income Visualization"):
                fig, ax = plt.subplots(figsize=(4, 2))
                ax.barh(['Loan Amount', 'Monthly Income'], [loan_amt, income], color=['orange', 'green'])
                ax.set_xlabel('Amount (Rs)')
                ax.set_title('Loan vs Income Comparison')
                st.pyplot(fig)

            with st.expander("💡 Suggestion"):
                if predict == 0:
                    st.warning("Consider reducing the loan amount or improving your credit score to increase approval chances.")
                else:
                    st.success("Your profile looks strong for this loan request.")
