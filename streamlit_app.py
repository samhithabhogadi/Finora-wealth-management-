# streamlit_app.py

import streamlit as st
import pandas as pd
import altair as alt
from datetime import date

# Initialize session state
if 'users' not in st.session_state:
    st.session_state['users'] = {}
if 'logged_in_user' not in st.session_state:
    st.session_state['logged_in_user'] = None
if 'pocket_money' not in st.session_state:
    st.session_state['pocket_money'] = 0.0
if 'expense_data' not in st.session_state:
    st.session_state['expense_data'] = []
if 'page_flow' not in st.session_state:
    st.session_state['page_flow'] = "Register"

# App Title
st.title("💰 FINORA - Student Budget Manager")

# Sidebar Navigation (disabled control — shows current page only)
st.sidebar.title("Navigation")
st.sidebar.markdown(f"Current Page: **{st.session_state['page_flow']}**")

# Handle pages
page = st.session_state['page_flow']

# Page 1 - Registration
if page == "Register":
    st.header("Register New Account")

    reg_name = st.text_input("Name")
    reg_email = st.text_input("Email")
    reg_username = st.text_input("Username")
    reg_password = st.text_input("Password", type="password")

    if st.button("Register"):
        if reg_username in st.session_state['users']:
            st.error("Username already exists! Try another.")
        else:
            st.session_state['users'][reg_username] = {
                'name': reg_name,
                'email': reg_email,
                'password': reg_password
            }
            st.success("Registration successful!")
            if st.button("Go to Login"):
                st.session_state['page_flow'] = "Login"

# Page 2 - Login
elif page == "Login":
    st.header("Login to FINORA")

    login_username = st.text_input("Username")
    login_password = st.text_input("Password", type="password")

    if st.button("Login"):
        user_data = st.session_state['users'].get(login_username)
        if user_data and user_data['password'] == login_password:
            st.session_state['logged_in_user'] = login_username
            st.success(f"Welcome, {user_data['name']}!")
            if st.button("Enter App"):
                st.session_state['page_flow'] = "FINORA App"
        else:
            st.error("Invalid login.")

# Page 3 - Main App
elif page == "FINORA App":
    if st.session_state['logged_in_user'] is None:
        st.warning("Please log in first.")
        st.session_state['page_flow'] = "Login"
    else:
        logged_user = st.session_state['logged_in_user']
        name = st.session_state['users'][logged_user]['name']

        st.header(f"Welcome, {name}! 🎓")

        subpage = st.radio("Choose Action", ["Set Pocket Money", "Add Expenses", "View Summary & Graphs", "Logout"])

        if subpage == "Set Pocket Money":
            pm = st.number_input("Enter Monthly Pocket Money (₹)", min_value=0.0, format="%.2f")
            if st.button("Save Pocket Money"):
                st.session_state['pocket_money'] = pm
                st.success("Pocket money saved.")

        elif subpage == "Add Expenses":
            desc = st.text_input("Description")
            amt = st.number_input("Amount (₹)", min_value=0.0, format="%.2f")
            cat = st.selectbox("Category", ["Food", "Transport", "Education", "Entertainment", "Others"])
            dt = st.date_input("Date", value=date.today())

            if st.button("Add Expense"):
                st.session_state['expense_data'].append({
                    'description': desc,
                    'amount': amt,
                    'category': cat,
                    'date': dt
                })
                st.success("Expense added.")

        elif subpage == "View Summary & Graphs":
            st.subheader("Pocket Money Summary")

            total_spent = sum([e['amount'] for e in st.session_state['expense_data']])
            balance = st.session_state['pocket_money'] - total_spent

            st.metric("Total Pocket Money", f"₹{st.session_state['pocket_money']:.2f}")
            st.metric("Total Spent", f"₹{total_spent:.2f}")
            st.metric("Balance Left", f"₹{balance:.2f}")

            if st.session_state['expense_data']:
                df = pd.DataFrame(st.session_state['expense_data'])
                st.dataframe(df)

                # Pie Chart
                cat_df = df.groupby("category")["amount"].sum().reset_index()
                pie = alt.Chart(cat_df).mark_arc(innerRadius=50).encode(
                    theta="amount:Q",
                    color="category:N",
                    tooltip=["category", "amount"]
                ).properties(width=400, height=400)
                st.altair_chart(pie)

                # Line Chart
                time_df = df.groupby("date")["amount"].sum().reset_index()
                line = alt.Chart(time_df).mark_line(point=True).encode(
                    x="date:T",
                    y="amount:Q",
                    tooltip=["date", "amount"]
                ).properties(width=600, height=300)
                st.altair_chart(line)
            else:
                st.info("No expenses yet.")

        elif subpage == "Logout":
            st.session_state['logged_in_user'] = None
            st.session_state['page_flow'] = "Login"
            st.success("Logged out. Click below to go to login.")
            if st.button("Go to Login"):
                pass

# Page 4 - About
elif page == "About":
    st.header("Key Features of FINORA")
    st.markdown("""
    **FINORA** is a modern student budgeting app designed for simplicity and financial awareness.

    ### 🔑 Features:
    - Student-first interface for tracking monthly income and expenses.
    - Clean visual insights via pie & line charts.
    - Mobile-ready, light theme, easy-to-use experience.
    - Data stays local (session only) for security and privacy.

    Start your financial journey with FINORA.
    """)

# Footer
st.markdown("---")
st.markdown("© 2025 FINORA | Built for students, by students.", unsafe_allow_html=True)
