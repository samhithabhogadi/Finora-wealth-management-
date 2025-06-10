# finora_app.py

import streamlit as st
import pandas as pd
import altair as alt
from datetime import date

# --- Initialize session state ---
if 'users' not in st.session_state:
    st.session_state['users'] = {}
if 'logged_in_user' not in st.session_state:
    st.session_state['logged_in_user'] = None
if 'expenses' not in st.session_state:
    st.session_state['expenses'] = []

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
    nav_choice = st.sidebar.radio("Go to", ["🏠 Dashboard", "➕ Add Expense", "📊 Analytics", "🚪 Logout"])

    username = st.session_state['logged_in_user']
    name = st.session_state['users'][username]['name']

    if nav_choice == "🏠 Dashboard":
        st.header(f"Welcome {name} 👋")
        st.subheader("Your Financial Summary")

        total_expenses = sum([exp['amount'] for exp in st.session_state['expenses'] if exp['username'] == username])
        st.metric(label="Total Expenses", value=f"₹{total_expenses:.2f}")

        st.write("---")
        st.write("Latest Expenses")
        user_expenses = [exp for exp in st.session_state['expenses'] if exp['username'] == username]
        if user_expenses:
            df_exp = pd.DataFrame(user_expenses)
            df_exp['date'] = pd.to_datetime(df_exp['date'])
            df_exp = df_exp.sort_values(by='date', ascending=False)
            st.dataframe(df_exp[['date', 'category', 'description', 'amount']].head(10))
        else:
            st.info("No expenses recorded yet.")

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

    elif nav_choice == "📊 Analytics":
        st.header("📊 Expense Analytics")

        user_expenses = [exp for exp in st.session_state['expenses'] if exp['username'] == username]

        if user_expenses:
            df_exp = pd.DataFrame(user_expenses)
            df_exp['date'] = pd.to_datetime(df_exp['date'])

            # Expenses over time
            st.subheader("Expenses Over Time")
            time_df = df_exp.groupby('date')['amount'].sum().reset_index()

            line_chart = alt.Chart(time_df).mark_line(point=True).encode(
                x='date:T',
                y='amount:Q',
                tooltip=['date', 'amount']
            ).properties(width=700, height=400)

            st.altair_chart(line_chart)

            # Expenses by category
            st.subheader("Expenses by Category")
            cat_df = df_exp.groupby('category')['amount'].sum().reset_index()

            pie_chart = alt.Chart(cat_df).mark_arc(innerRadius=50).encode(
                theta=alt.Theta(field='amount', type='quantitative'),
                color=alt.Color(field='category', type='nominal'),
                tooltip=['category', 'amount']
            ).properties(width=400, height=400)

            st.altair_chart(pie_chart)

        else:
            st.info("No expenses to analyze yet.")

    elif nav_choice == "🚪 Logout":
        st.session_state['logged_in_user'] = None
        st.success("You have been logged out.")

# --- Footer ---
st.markdown("---")
st.markdown("© 2025 FINORA Student Budget Manager App. All rights reserved.", unsafe_allow_html=True)
