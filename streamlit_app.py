# finora_budget_manager_with_login.py

import streamlit as st
import pandas as pd
import altair as alt
from datetime import date

# Initialize session state
if 'users' not in st.session_state:
    st.session_state['users'] = {}  # username: {name, email, password}
if 'logged_in_user' not in st.session_state:
    st.session_state['logged_in_user'] = None
if 'pocket_money' not in st.session_state:
    st.session_state['pocket_money'] = 0.0
if 'expense_data' not in st.session_state:
    st.session_state['expense_data'] = []

# App Title
st.title("💰 FINORA - Student Budget Manager")

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Login", "Register", "FINORA App", "About"])

# Registration Page
if page == "Register":
    st.header("Register New Account")

    reg_name = st.text_input("Name")
    reg_email = st.text_input("Email")
    reg_username = st.text_input("Username")
    reg_password = st.text_input("Password", type="password")

    if st.button("Register"):
        if reg_username in st.session_state['users']:
            st.error("Username already exists! Please choose another one.")
        else:
            st.session_state['users'][reg_username] = {
                'name': reg_name,
                'email': reg_email,
                'password': reg_password
            }
            st.success(f"User {reg_username} registered successfully! Please log in.")

# Login Page
elif page == "Login":
    st.header("Login to FINORA")

    login_username = st.text_input("Username")
    login_password = st.text_input("Password", type="password")

    if st.button("Login"):
        user_data = st.session_state['users'].get(login_username)
        if user_data and user_data['password'] == login_password:
            st.session_state['logged_in_user'] = login_username
            st.success(f"Welcome, {user_data['name']}!")
        else:
            st.error("Invalid username or password.")

# FINORA App (main app after login)
elif page == "FINORA App":
    if st.session_state['logged_in_user'] is None:
        st.warning("Please log in to access the FINORA app.")
    else:
        logged_in_username = st.session_state['logged_in_user']
        logged_in_name = st.session_state['users'][logged_in_username]['name']

        st.header(f"Welcome {logged_in_name} to FINORA! 🎓")

        finora_subpage = st.radio("Select Page", ["Set Pocket Money", "Add Expenses", "View Summary & Graphs"])

        if finora_subpage == "Set Pocket Money":
            st.subheader("Set Your Monthly Pocket Money")
            pocket_money_input = st.number_input("Enter your Pocket Money (₹)", min_value=0.0, format="%.2f")
            if st.button("Save Pocket Money"):
                st.session_state['pocket_money'] = pocket_money_input
                st.success(f"Pocket Money set to ₹{pocket_money_input:.2f}")

        elif finora_subpage == "Add Expenses":
            st.subheader("Add Your Monthly Expenses")

            expense_desc = st.text_input("Expense Description")
            expense_amt = st.number_input("Expense Amount (₹)", min_value=0.0, format="%.2f")
            expense_category = st.selectbox("Expense Category", ["Food", "Transport", "Entertainment", "Education", "Others"])
            expense_date = st.date_input("Date of Expense", value=date.today())

            if st.button("Add Expense"):
                st.session_state['expense_data'].append({
                    "description": expense_desc,
                    "amount": expense_amt,
                    "category": expense_category,
                    "date": expense_date
                })
                st.success(f"Added Expense: {expense_desc} - ₹{expense_amt} [{expense_category}] on {expense_date}")

        elif finora_subpage == "View Summary & Graphs":
            st.subheader("Summary of Your Pocket Money")

            total_expenses = sum([item['amount'] for item in st.session_state['expense_data']])
            balance_left = st.session_state['pocket_money'] - total_expenses

            st.subheader(f"Total Pocket Money: ₹{st.session_state['pocket_money']:.2f}")
            st.subheader(f"Total Expenses: ₹{total_expenses:.2f}")
            st.subheader(f"Balance Left: ₹{balance_left:.2f}")

            st.markdown("---")

            # Display Expense Details
            st.subheader("Expense Details")
            if st.session_state['expense_data']:
                df_expense = pd.DataFrame(st.session_state['expense_data'])
                st.dataframe(df_expense)

                # Pie Chart by Category
                st.subheader("Expense Breakdown by Category")
                category_df = df_expense.groupby('category')['amount'].sum().reset_index()

                pie_chart = alt.Chart(category_df).mark_arc(innerRadius=50).encode(
                    theta=alt.Theta(field="amount", type="quantitative"),
                    color=alt.Color(field="category", type="nominal"),
                    tooltip=["category", "amount"]
                ).properties(width=400, height=400)

                st.altair_chart(pie_chart)

                # Line Chart over Time
                st.subheader("Spending Over Time")
                time_df = df_expense.groupby('date')['amount'].sum().reset_index()

                line_chart = alt.Chart(time_df).mark_line(point=True).encode(
                    x=alt.X('date:T', title='Date'),
                    y=alt.Y('amount:Q', title='Amount Spent'),
                    tooltip=["date", "amount"]
                ).properties(width=700, height=400)

                st.altair_chart(line_chart)

            else:
                st.write("No expenses recorded yet.")

# About Page
elif page == "About":
    st.header("About FINORA")
    st.write("""
    **FINORA** is an advanced Student Budget & Pocket Money Manager app with Login & Registration.
    
    Features:
    - User Registration & Login
    - Set your Monthly Pocket Money
    - Add Expenses with Category and Date
    - View Summary & Graphs
    - Analyze your Spending trends
    
    Stay financially smart with FINORA! 🚀
    """)

# Footer
st.markdown("---")
st.markdown("© 2025 FINORA Student Budget Manager App. All rights reserved.", unsafe_allow_html=True)
