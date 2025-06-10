# finora_budget_manager.py

import streamlit as st
import pandas as pd
from openai import OpenAI
import altair as alt
from datetime import date, datetime
import pickle


openai.api_key = "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"
response = client.chat.completions.create(
    model="gpt-4o",   # or "gpt-4-turbo" or "gpt-3.5-turbo"
    messages=[
        {"role": "system", "content": "You are a smart financial advisor for students."},
        {"role": "user", "content": prompt}
    ],
    max_tokens=400
)

advice = response.choices[0].message.content
# --- Initialize session state ---
if 'users' not in st.session_state:
    st.session_state['users'] = {}
if 'logged_in_user' not in st.session_state:
    st.session_state['logged_in_user'] = None
if 'expenses' not in st.session_state:
    st.session_state['expenses'] = []
if 'pocket_money' not in st.session_state:
    st.session_state['pocket_money'] = []

# --- Helper functions ---
def login(username, password):
    user = st.session_state['users'].get(username)
    if user and user['password'] == password:
        st.session_state['logged_in_user'] = username
        return True
    return False

def register(username, name, email, password):
    if username in st.session_state['users']:
        return False
    st.session_state['users'][username] = {
        'name': name,
        'email': email,
        'password': password
    }
    return True

def ask_ai_advisor(balance, expenses_summary):
    prompt = f"""
    I am a student. I have ₹{balance:.2f} left this month after expenses.
    My typical spending categories are: {expenses_summary}.
    Please suggest how I can utilize the remaining money wisely.
    Should I invest? How much should I keep as buffer? Give practical advice in simple terms suitable for a student.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a smart financial advisor for students."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300
    )

    return response['choices'][0]['message']['content']

# --- Styling ---
st.markdown("""
    <style>
    body {
        font-family: 'Arial', sans-serif;
        color: #222;
        background-color: #fafafa;
    }
    .main {
        background-color: #fafafa;
        color: #222;
    }
    h1, h2, h3 {
        font-weight: bold;
        color: #222;
    }
    </style>
""", unsafe_allow_html=True)

# --- App Title ---
st.title("💸 FINORA - Student Budget Manager")

# --- Auth flow ---
if st.session_state['logged_in_user'] is None:

    auth_choice = st.sidebar.radio("Login / Register", ["Login", "Register"])

    if auth_choice == "Login":
        st.header("🔑 Login")
        login_username = st.text_input("Username")
        login_password = st.text_input("Password", type="password")

        if st.button("Login"):
            if login(login_username, login_password):
                st.success(f"Welcome {st.session_state['users'][login_username]['name']}! You are logged in.")
            else:
                st.error("Invalid username or password.")

    elif auth_choice == "Register":
        st.header("📝 Register")
        reg_name = st.text_input("Name")
        reg_email = st.text_input("Email")
        reg_username = st.text_input("Username")
        reg_password = st.text_input("Password", type="password")

        if st.button("Register"):
            if register(reg_username, reg_name, reg_email, reg_password):
                st.success("Registration successful! You can now login.")
            else:
                st.error("Username already exists. Please choose another.")
else:
    # --- Dashboard Layout ---
    st.sidebar.header("Navigation")
    nav_choice = st.sidebar.radio("Go to", ["🏠 Dashboard", "💰 Set Pocket Money", "➕ Add Expense", "📊 Monthly Summary", "🤖 AI Advisor", "🚪 Logout"])

    username = st.session_state['logged_in_user']
    name = st.session_state['users'][username]['name']

    if nav_choice == "🏠 Dashboard":
        st.header(f"Welcome {name} 👋")
        st.subheader("Current Month Summary")

        today = date.today()
        current_month = today.month
        current_year = today.year

        # Get pocket money for this month
        pm_records = [pm for pm in st.session_state['pocket_money'] if pm['username']==username and pm['month']==current_month and pm['year']==current_year]
        pm_amount = pm_records[0]['amount'] if pm_records else 0.0

        # Total expenses this month
        month_expenses = [exp for exp in st.session_state['expenses'] if exp['username']==username and exp['date'].month==current_month and exp['date'].year==current_year]
        total_expenses = sum([exp['amount'] for exp in month_expenses])

        balance_left = pm_amount - total_expenses

        st.metric(label="Pocket Money", value=f"₹{pm_amount:.2f}")
        st.metric(label="Total Expenses", value=f"₹{total_expenses:.2f}")
        st.metric(label="Balance Left", value=f"₹{balance_left:.2f}")

    elif nav_choice == "💰 Set Pocket Money":
        st.header("💰 Set Pocket Money for Month")

        today = date.today()
        default_month = today.month
        default_year = today.year

        month = st.selectbox("Month", list(range(1,13)), index=default_month-1)
        year = st.number_input("Year", min_value=2020, max_value=2100, value=default_year)

        pm_amount = st.number_input("Pocket Money Amount (₹)", min_value=0.0, format="%.2f")

        if st.button("Save Pocket Money"):
            # Remove existing record if exists
            st.session_state['pocket_money'] = [pm for pm in st.session_state['pocket_money'] if not (pm['username']==username and pm['month']==month and pm['year']==year)]

            st.session_state['pocket_money'].append({
                'username': username,
                'month': month,
                'year': year,
                'amount': pm_amount
            })

            st.success(f"Pocket money ₹{pm_amount:.2f} saved for {year}-{month}.")

    elif nav_choice == "➕ Add Expense":
        st.header("➕ Add New Expense")

        exp_desc = st.text_input("Description")
        exp_amt = st.number_input("Amount (₹)", min_value=0.0, format="%.2f")
        exp_cat = st.selectbox("Category", ["Food", "Transport", "Entertainment", "Education", "Others"])
        exp_date = st.date_input("Date", value=date.today())

        if st.button("Add Expense"):
            st.session_state['expenses'].append({
                'username': username,
                'description': exp_desc,
                'amount': exp_amt,
                'category': exp_cat,
                'date': exp_date
            })
            st.success("Expense added successfully.")

    elif nav_choice == "📊 Monthly Summary":
        st.header("📊 Monthly Summary (Pocket Money vs Expenses)")

        # Prepare monthly data
        pm_df = pd.DataFrame([pm for pm in st.session_state['pocket_money'] if pm['username']==username])
        exp_df = pd.DataFrame([{
            'month': exp['date'].month,
            'year': exp['date'].year,
            'amount': exp['amount']
        } for exp in st.session_state['expenses'] if exp['username']==username])

        if not pm_df.empty:
            pm_df['month_year'] = pm_df['year'].astype(str) + '-' + pm_df['month'].astype(str).zfill(2)
            pm_grouped = pm_df.groupby('month_year')['amount'].sum().reset_index()
            pm_grouped = pm_grouped.rename(columns={'amount':'Pocket Money'})

            if not exp_df.empty:
                exp_df['month_year'] = exp_df['year'].astype(str) + '-' + exp_df['month'].astype(str).zfill(2)
                exp_grouped = exp_df.groupby('month_year')['amount'].sum().reset_index()
                exp_grouped = exp_grouped.rename(columns={'amount':'Expenses'})

                # Merge
                summary_df = pd.merge(pm_grouped, exp_grouped, on='month_year', how='left')
                summary_df['Expenses'] = summary_df['Expenses'].fillna(0.0)
            else:
                summary_df = pm_grouped.copy()
                summary_df['Expenses'] = 0.0

            summary_df['Savings'] = summary_df['Pocket Money'] - summary_df['Expenses']

            # Display table
            st.dataframe(summary_df)

            # Plot graph
            summary_melt = summary_df.melt(id_vars='month_year', value_vars=['Pocket Money','Expenses','Savings'], var_name='Metric', value_name='Amount')

            chart = alt.Chart(summary_melt).mark_bar().encode(
                x=alt.X('month_year:N', title='Month'),
                y=alt.Y('Amount:Q', title='Amount ₹'),
                color=alt.Color('Metric:N'),
                tooltip=['month_year','Metric','Amount']
            ).properties(width=700, height=400)

            st.altair_chart(chart)

        else:
            st.info("No pocket money data available. Please add pocket money first.")

    elif nav_choice == "🤖 AI Advisor":
        st.header("🤖 Ask AI Financial Advisor")

        # Prepare balance and expenses summary
        today = date.today()
        current_month = today.month
        current_year = today.year

        # Pocket Money
        pm_records = [pm for pm in st.session_state['pocket_money'] if pm['username']==username and pm['month']==current_month and pm['year']==current_year]
        pm_amount = pm_records[0]['amount'] if pm_records else 0.0

        # Expenses
        month_expenses = [exp for exp in st.session_state['expenses'] if exp['username']==username and exp['date'].month==current_month and exp['date'].year==current_year]
        total_expenses = sum([exp['amount'] for exp in month_expenses])

        balance_left = pm_amount - total_expenses
        categories_used = ", ".join(set([exp['category'] for exp in month_expenses]))

        # User Input
        user_question = st.text_input("Ask your question to the AI Advisor:")

        if st.button("Get Advice"):
            advice = ask_ai_advisor(balance_left, categories_used)
            st.markdown(f"**AI Advisor:** {advice}")

    elif nav_choice == "🚪 Logout":
        st.session_state['logged_in_user'] = None
        st.success("You have been logged out.")

# --- Footer ---
st.markdown("---")
st.markdown("© 2025 FINORA Student Budget Manager App with AI Advisor. All rights reserved.", unsafe_allow_html=True)
