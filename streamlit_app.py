# finora_budget_manager.py

import streamlit as st
import pandas as pd
import altair as alt
from datetime import date

# Initialize session state
if 'pocket_money' not in st.session_state:
    st.session_state['pocket_money'] = 0.0
if 'expense_data' not in st.session_state:
    st.session_state['expense_data'] = []

# App Title
st.title("💰 FINORA - Student Budget Manager")

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Set Pocket Money", "Add Expenses", "View Summary & Graphs", "About"])

# Set Pocket Money
if page == "Set Pocket Money":
    st.header("Set Your Monthly Pocket Money")
    pocket_money_input = st.number_input("Enter your Pocket Money (₹)", min_value=0.0, format="%.2f")
    if st.button("Save Pocket Money"):
        st.session_state['pocket_money'] = pocket_money_input
        st.success(f"Pocket Money set to ₹{pocket_money_input:.2f}")

# Add Expenses
elif page == "Add Expenses":
    st.header("Add Your Monthly Expenses")

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

# View Summary & Graphs
elif page == "View Summary & Graphs":
    st.header("Summary of Your Pocket Money")

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

# About
elif page == "About":
    st.header("About FINORA")
    st.write("""
    **FINORA** is an advanced Student Budget & Pocket Money Manager app.
    
    Features:
    - Set your Monthly Pocket Money
    - Add Expenses with Category and Date
    - View Summary & Graphs
    - Analyze your Spending trends
    
    Stay financially smart with FINORA! 🚀
    """)

# Footer
st.markdown("---")
st.markdown("© 2025 FINORA Student Budget Manager App. All rights reserved.", unsafe_allow_html=True)
