import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
import pickle
import openai

# ---------------- CONFIG ----------------
st.set_page_config(page_title="FINORA - Student Budget Manager", page_icon="💰", layout="wide")

# ---------------- API SETUP (AI Advisor) ----------------
openai.api_key = st.secrets["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"]  # Store API key in Streamlit secrets

def ask_ai_advisor(balance_left, categories_used):
    prompt = f"""
    I am a student and I have Rs.{balance_left} left after monthly expenses.
    I usually spend on: {', '.join(categories_used)}.
    Suggest smart and simple ways to invest or save this remaining money.
    Keep advice beginner-friendly and actionable.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        return "Unable to get advice currently. Please try later."

# ---------------- User Auth ----------------
def load_user_data():
    if os.path.exists("users.pkl"):
        with open("users.pkl", "rb") as f:
            return pickle.load(f)
    return {}

def save_user_data(data):
    with open("users.pkl", "wb") as f:
        pickle.dump(data, f)

users = load_user_data()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'username' not in st.session_state:
    st.session_state.username = ''

# ---------------- Registration ----------------
if not st.session_state.logged_in:
    menu = st.sidebar.radio("Login / Register", ["Login", "Register"])
    if menu == "Register":
        st.title("👥 Register")
        new_user = st.text_input("Choose a username")
        new_pass = st.text_input("Choose a password", type="password")
        if st.button("Register"):
            if new_user in users:
                st.warning("Username already exists")
            else:
                users[new_user] = {'password': new_pass, 'data': []}
                save_user_data(users)
                st.success("Registered! Please login.")

    if menu == "Login":
        st.title("🔐 Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username in users and users[username]['password'] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome, {username}!")
            else:
                st.error("Invalid credentials")

# ---------------- App Dashboard ----------------
if st.session_state.logged_in:
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose", ["Dashboard", "AI Advisor", "Finance Basics", "Logout"])

    if page == "Logout":
        st.session_state.logged_in = False
        st.session_state.username = ''
        st.experimental_rerun()

    if page == "Dashboard":
        st.title("📊 Budget Dashboard")
        user_data = users[st.session_state.username]['data']

        with st.form("data_form"):
            month = st.selectbox("Month", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
            year = st.selectbox("Year", list(range(2023, datetime.now().year + 1)))
            income = st.number_input("Monthly Pocket Money (Rs.)", min_value=0)
            expenses = st.text_area("Enter expenses (e.g. Food:200, Travel:100)")
            submitted = st.form_submit_button("Add")

        if submitted:
            expense_dict = {}
            try:
                for item in expenses.split(','):
                    cat, amt = item.strip().split(':')
                    expense_dict[cat.strip()] = int(amt.strip())
                user_data.append({
                    'month': month,
                    'year': year,
                    'income': income,
                    'expenses': expense_dict,
                    'timestamp': datetime.now()
                })
                users[st.session_state.username]['data'] = user_data
                save_user_data(users)
                st.success("Data saved!")
            except:
                st.error("Format error. Please follow: Category:Amount")

        if user_data:
            df = pd.DataFrame(user_data)
            df['total_expense'] = df['expenses'].apply(lambda x: sum(x.values()))
            df['savings'] = df['income'] - df['total_expense']

            monthly_summary = df.groupby(['year', 'month']).agg({
                'income': 'sum',
                'total_expense': 'sum',
                'savings': 'sum'
            }).reset_index()

            st.subheader("📅 Monthly Summary")
            st.dataframe(monthly_summary)

            st.subheader("📊 Expense Breakdown (Pie Chart)")
            last_expense = user_data[-1]['expenses']
            fig, ax = plt.subplots()
            ax.pie(last_expense.values(), labels=last_expense.keys(), autopct='%1.1f%%')
            ax.axis('equal')
            st.pyplot(fig)

    elif page == "AI Advisor":
        st.title("🤖 AI Investment Advisor")
        user_data = users[st.session_state.username]['data']
        if not user_data:
            st.warning("Add data in Dashboard first.")
        else:
            last_entry = user_data[-1]
            balance_left = last_entry['income'] - sum(last_entry['expenses'].values())
            categories_used = list(last_entry['expenses'].keys())
            st.info(f"You have Rs.{balance_left} left this month.")
            advice = ask_ai_advisor(balance_left, categories_used)
            st.markdown(f"**AI Advice:**\n{advice}")

    elif page == "Finance Basics":
        st.title("📈 Finance Education")
        st.markdown("""
        ### Basics of Investing

        **1. What are Stocks?**
        Stocks represent ownership in a company. When you buy a stock, you become a part-owner of that company.

        **2. Types of Stocks:**
        - Large Cap: Stable, established companies (e.g., Infosys, TCS)
        - Mid Cap: Medium-sized, growth companies
        - Small Cap: High-risk, high-reward, newer companies

        **3. Where to Start?**
        - Start with Index Funds or Mutual Funds
        - Use trusted platforms (Zerodha, Groww, Kuvera)

        **4. Golden Rule:**
        Invest small, consistently. Don’t invest in what you don’t understand.

        **5. Emergency Fund:**
        Always save at least 3 months' expenses before you begin risky investments.
        """)

