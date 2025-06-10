# finora_budget_manager.py

import streamlit as st
import pandas as pd
import openai
import altair as alt
from datetime import date, datetime
import pickle
import os

openai.api_key = "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"
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[ ... ],
    max_tokens=300
    )
# ----------------- Helper Functions -----------------

# Load or initialize user database
if os.path.exists("users.pkl"):
    with open("users.pkl", "rb") as f:
        users = pickle.load(f)
else:
    users = {}

# Save user database
def save_users():
    with open("users.pkl", "wb") as f:
        pickle.dump(users, f)

# Register User
def register(username, name, email, password):
    if username in users:
        return False
    users[username] = {"name": name, "email": email, "password": password}
    save_users()
    return True

# Authenticate User
def authenticate(username, password):
    if username in users and users[username]["password"] == password:
        return True
    return False

# ----------------- App State -----------------

if "logged_in_user" not in st.session_state:
    st.session_state["logged_in_user"] = None
if "just_logged_in" not in st.session_state:
    st.session_state["just_logged_in"] = False
if "pocket_money" not in st.session_state:
    st.session_state["pocket_money"] = []
if "expenses" not in st.session_state:
    st.session_state["expenses"] = []

# ----------------- AI Advisor -----------------

def ask_ai_advisor(balance, expenses_summary):
    prompt = f"""
    I am a student. I have ₹{balance:.2f} left this month after expenses.
    My typical spending categories are: {expenses_summary}.
    Please suggest how I can utilize the remaining money wisely.
    Should I invest? How much should I keep as buffer? Give practical advice in simple terms suitable for a student.
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a smart financial advisor for students."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300
    )

    return response.choices[0].message.content

# ----------------- UI -----------------

st.set_page_config(page_title="FINORA - Student Budget Manager", layout="wide")

st.title("💸 FINORA - Student Budget Manager App")

# ----------------- Auth Section -----------------

if st.session_state["logged_in_user"] is None:

    auth_choice = st.sidebar.radio("Login/Register", ["Login", "Register"])

    if auth_choice == "Login":
        st.header("🔐 Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if authenticate(username, password):
                st.session_state["logged_in_user"] = username
                st.session_state["just_logged_in"] = True
                st.success(f"Welcome {users[username]['name']}! You are logged in.")
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
                st.success("Registration successful! You are now logged in.")
                st.session_state["logged_in_user"] = reg_username
                st.session_state["just_logged_in"] = True
            else:
                st.error("Username already exists. Please choose another.")

# ----------------- Main App -----------------

else:

    username = st.session_state["logged_in_user"]

    if st.session_state.get("just_logged_in", False):
        st.sidebar.success(f"✅ Welcome {users[username]['name']}! Navigate from sidebar.")
        st.session_state["just_logged_in"] = False

    nav_choice = st.sidebar.radio("Go to", ["🏠 Dashboard", "💰 Set Pocket Money", "➕ Add Expense", "📊 Monthly Summary", "🤖 AI Advisor", "🎓 Learn Finance", "🚪 Logout"])

    # Dashboard
    if nav_choice == "🏠 Dashboard":
        st.header(f"🏠 Welcome, {users[username]['name']}!")

        pm_df = pd.DataFrame(st.session_state["pocket_money"])
        pm_df = pm_df[pm_df["username"] == username]

        if not pm_df.empty:
            latest_pm = pm_df.sort_values(by="date", ascending=False).iloc[0]
            st.metric("Current Month Pocket Money", f"₹{latest_pm['amount']:.2f}")

            exp_df = pd.DataFrame(st.session_state["expenses"])
            exp_df = exp_df[exp_df["username"] == username]
            exp_df["month_year"] = exp_df["date"].apply(lambda x: f"{x.year}-{str(x.month).zfill(2)}")

            current_month = latest_pm["date"].year, latest_pm["date"].month
            exp_current_month = exp_df[(exp_df["date"].dt.year == current_month[0]) & (exp_df["date"].dt.month == current_month[1])]

            total_exp = exp_current_month["amount"].sum()
            balance_left = latest_pm["amount"] - total_exp

            st.metric("Total Expenses This Month", f"₹{total_exp:.2f}")
            st.metric("Balance Left", f"₹{balance_left:.2f}")

        else:
            st.info("Please set your pocket money for this month first!")

    # Set Pocket Money
    elif nav_choice == "💰 Set Pocket Money":
        st.header("💰 Set Monthly Pocket Money")
        amount = st.number_input("Enter Pocket Money Amount (₹)", min_value=0.0, step=100.0)
        date = st.date_input("Select Date", datetime.today())

        if st.button("Set Pocket Money"):
            st.session_state["pocket_money"].append({
                "username": username,
                "amount": amount,
                "date": pd.to_datetime(date),
                "month": date.month,
                "year": date.year
            })
            st.success("Pocket Money updated!")

    # Add Expense
    elif nav_choice == "➕ Add Expense":
        st.header("➕ Add Expense")
        category = st.selectbox("Expense Category", ["Food", "Transport", "Entertainment", "Shopping", "Others"])
        amount = st.number_input("Expense Amount (₹)", min_value=0.0, step=50.0)
        date = st.date_input("Expense Date", datetime.today())

        if st.button("Add Expense"):
            st.session_state["expenses"].append({
                "username": username,
                "category": category,
                "amount": amount,
                "date": pd.to_datetime(date),
                "month": date.month,
                "year": date.year
            })
            st.success("Expense added!")

    # Monthly Summary
    elif nav_choice == "📊 Monthly Summary":
        st.header("📊 Monthly Summary")

        pm_df = pd.DataFrame(st.session_state["pocket_money"])
        pm_df = pm_df[pm_df["username"] == username]
        if pm_df.empty:
            st.warning("No Pocket Money data!")
            st.stop()

        exp_df = pd.DataFrame(st.session_state["expenses"])
        exp_df = exp_df[exp_df["username"] == username]

        pm_df["month_year"] = pm_df["year"].astype(str) + "-" + pm_df["month"].astype(str).str.zfill(2)
        exp_df["month_year"] = exp_df["year"].astype(str) + "-" + exp_df["month"].astype(str).str.zfill(2)

        pm_summary = pm_df.groupby("month_year")["amount"].sum().reset_index(name="Pocket Money")
        exp_summary = exp_df.groupby("month_year")["amount"].sum().reset_index(name="Expenses")

        summary_df = pd.merge(pm_summary, exp_summary, on="month_year", how="left").fillna(0)
        summary_df["Savings"] = summary_df["Pocket Money"] - summary_df["Expenses"]

        st.dataframe(summary_df)

        summary_melt = summary_df.melt(id_vars=["month_year"], value_vars=["Pocket Money", "Expenses", "Savings"], var_name="Type", value_name="Amount")

        chart = alt.Chart(summary_melt).mark_bar().encode(
            x="month_year",
            y="Amount",
            color="Type",
            tooltip=["month_year", "Type", "Amount"]
        ).properties(width=800)

        st.altair_chart(chart)

        # Pie Chart
        st.subheader("Expense Distribution (Pie Chart)")

        if not exp_df.empty:
            selected_month = st.selectbox("Select Month-Year", exp_df["month_year"].unique())
            filtered_df = exp_df[exp_df["month_year"] == selected_month]

            cat_summary = filtered_df.groupby("category")["amount"].sum().reset_index()

            pie_chart = alt.Chart(cat_summary).mark_arc(innerRadius=50).encode(
                theta=alt.Theta(field="amount", type="quantitative"),
                color=alt.Color(field="category", type="nominal"),
                tooltip=["category", "amount"]
            ).properties(width=400, height=400)

            st.altair_chart(pie_chart)
        else:
            st.info("No expenses to display pie chart.")

    # AI Advisor
    elif nav_choice == "🤖 AI Advisor":
        st.header("🤖 AI Advisor")

        pm_df = pd.DataFrame(st.session_state["pocket_money"])
        pm_df = pm_df[pm_df["username"] == username]

        if pm_df.empty:
            st.warning("No Pocket Money data!")
            st.stop()

        latest_pm = pm_df.sort_values(by="date", ascending=False).iloc[0]
        current_month = latest_pm["date"].year, latest_pm["date"].month

        exp_df = pd.DataFrame(st.session_state["expenses"])
        exp_df = exp_df[exp_df["username"] == username]
        exp_df["month_year"] = exp_df["date"].apply(lambda x: f"{x.year}-{str(x.month).zfill(2)}")

        exp_current_month = exp_df[(exp_df["date"].dt.year == current_month[0]) & (exp_df["date"].dt.month == current_month[1])]

        total_exp = exp_current_month["amount"].sum()
        balance_left = latest_pm["amount"] - total_exp

        categories_used = exp_current_month["category"].unique().tolist()

        if st.button("Ask AI Advisor"):
            advice = ask_ai_advisor(balance_left, categories_used)
            st.success("AI Advisor Suggestion:")
            st.write(advice)

    # Learn Finance
    elif nav_choice == "🎓 Learn Finance":
        st.header("🎓 Learn Basic Finance & Investing")

        st.subheader("📌 What is a Stock?")
        st.write("""
        A stock represents a share in the ownership of a company. When you buy a stock, you become a part-owner of the company and can benefit from its growth in value.
        """)

        st.subheader("📌 Types of Stocks")
        st.write("""
        - **Large Cap Stocks** → Big, stable companies (eg. Reliance, TCS)
        - **Mid Cap Stocks** → Medium-sized companies with growth potential
        - **Small Cap Stocks** → Small companies with higher risk but higher potential returns
        """)

        st.subheader("📌 Mutual Funds vs Stocks")
        st.write("""
        - **Stocks** → You buy individual company shares.
        - **Mutual Funds** → You invest in a pool of stocks managed by a professional fund manager.
        - Mutual funds offer diversification and lower risk for beginners.
        """)

        st.subheader("📌 Simple Investing Tips for Students")
        st.write("""
        - Start small — even ₹500/month matters!
        - Invest for the long term.
        - Use SIPs (Systematic Investment Plans) in Mutual Funds.
        - Avoid trying to 'time the market' — stay consistent.
        """)

        st.subheader("📌 How to Allocate Pocket Money")
        st.write("""
        - Spend wisely — prioritize essentials.
        - Save at least 20-30% of your pocket money.
        - Start investing a small part regularly (₹100-₹500 per month).
        - Build financial discipline early!
        """)

        st.info("Disclaimer: This is basic educational information. Please do your own research or consult a financial advisor before investing.")

    # Logout
    elif nav_choice == "🚪 Logout":
        st.session_state["logged_in_user"] = None
        st.session_state["just_logged_in"] = False
