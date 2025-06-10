import streamlit as st

# Light mode CSS with full enforcement
st.markdown("""
<style>
/* Global page background */
body {
    background-color: #f9fafc !important;
    color: #222222 !important;
    font-family: "Segoe UI", "Roboto", "Helvetica Neue", Arial, sans-serif !important;
}

/* All headings */
h1, h2, h3, h4, h5, h6 {
    color: #111111 !important;
    font-weight: 700 !important;
}

/* General text */
p, span, div, label, li, a {
    color: #222222 !important;
    font-size: 16px !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #f9fafc !important;
    color: #222222 !important;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h4,
section[data-testid="stSidebar"] h5,
section[data-testid="stSidebar"] h6,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label {
    color: #111111 !important;
    font-weight: 600 !important;
}

/* Tabs (Login/Register) */
button[role="tab"] {
    background-color: #f5f7fa !important;
    color: #222222 !important;
    border: 1px solid #ccd6e2 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding: 10px 20px !important;
    margin-right: 5px !important;
    cursor: pointer !important;
    transition: all 0.2s ease-in-out !important;
}

button[role="tab"]:hover {
    background-color: #e9eff5 !important;
    color: #111111 !important;
}

/* Main buttons */
div.stButton > button {
    background-color: #f5f7fa !important;
    color: #222222 !important;
    border: 1px solid #ccd6e2 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding: 10px 20px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
    cursor: pointer !important;
    transition: all 0.2s ease-in-out !important;
}

div.stButton > button:hover {
    background-color: #e9eff5 !important;
    color: #111111 !important;
    box-shadow: 0 4px 8px rgba(0,0,0,0.15) !important;
}

/* Input fields (Text, Number, Password, Textarea) */
input, textarea {
    background-color: #ffffff !important;
    color: #222222 !important;
    border: 1px solid #ccd6e2 !important;
    border-radius: 6px !important;
    padding: 8px !important;
    font-size: 15px !important;
}

/* Selectbox */
div[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    color: #222222 !important;
    border: 1px solid #ccd6e2 !important;
    border-radius: 6px !important;
}

/* Metric cards */
.metric-card {
    background-color: #ffffff !important;
    color: #222222 !important;
    border-radius: 8px !important;
    padding: 1rem !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
    font-weight: 600 !important;
}

/* Forms */
.stForm {
    background-color: #ffffff !important;
    color: #222222 !important;
    border-radius: 8px !important;
    padding: 1rem !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
}

/* DataFrame */
.stDataFrame {
    background-color: #ffffff !important;
    color: #222222 !important;
}

/* Main title */
.stTitle {
    color: #111111 !important;
    font-weight: 700 !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------
# Sample app content
# ---------------------

# Sidebar
st.sidebar.title("Navigation")
st.sidebar.write("Choose your page.")

# Main page
st.title("Welcome to Finora Wealth Management")
st.write("Please log in or register below:")

# Tabs for Login and Register
tab1, tab2 = st.tabs(["Login", "Register"])

# Login Tab
with tab1:
    st.subheader("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    login_btn = st.button("Login")
    if login_btn:
        st.success(f"Welcome back, {username}!")

# Register Tab
with tab2:
    st.subheader("Register")
    new_username = st.text_input("Choose a Username", key="register_username")
    new_password = st.text_input("Choose a Password", type="password", key="register_password")
    register_btn = st.button("Register")
    if register_btn:
        st.success(f"Account created for {new_username}!")

# Sample Metrics Section
st.header("Our Performance Metrics")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("AUM", "₹500 Cr", "+5%")
with col2:
    st.metric("Clients", "10,000+", "+10%")
with col3:
    st.metric("Satisfaction", "98%", "↑")
