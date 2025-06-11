import streamlit as st
import pandas as pd
from datetime import date

# Set page config (must be first Streamlit command)
st.set_page_config(page_title="Student Budget Tracker", layout="centered")

# Title
st.title("📘 Student Budget Manager")

# Initialize session state
if "expenses" not in st.session_state:
    st.session_state.expenses = []

# Input: Monthly pocket money
pocket_money = st.number_input("Enter your monthly pocket money (₹):", min_value=0, step=100)

# Add expenses
st.subheader("Add Your Expenses")
with st.form("expense_form"):
    category = st.text_input("Expense Category")
    amount = st.number_input("Amount (₹)", min_value=0, step=10)
    expense_date = st.date_input("Date", value=date.today())
    submitted = st.form_submit_button("Add Expense")

    if submitted:
        st.session_state.expenses.append({
            "category": category,
            "amount": amount,
            "date": expense_date
        })
        st.success("Expense added!")

# Show expenses
if st.session_state.expenses:
    df = pd.DataFrame(st.session_state.expenses)
    st.subheader("All Expenses")
    st.dataframe(df)

    # Total calculations
    total_expense = df["amount"].sum()
    savings = pocket_money - total_expense

    st.subheader("Summary")
    st.metric("Total Expenses", f"₹{total_expense}")
    st.metric("Remaining Savings", f"₹{savings}")

    # Pie chart
    st.subheader("Expense Breakdown")
    pie_data = df.groupby("category")["amount"].sum()
    st.pyplot(pie_data.plot.pie(autopct="%1.1f%%", figsize=(5, 5), title="Expenses by Category").get_figure())

    # Bar chart
    st.subheader("Bar Chart of Expenses")
    st.bar_chart(pie_data)

else:
    st.info("No expenses added yet.")

