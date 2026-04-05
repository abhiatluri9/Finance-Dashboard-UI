import streamlit as st
import pandas as pd
import numpy as np
import datetime
import plotly.express as px

st.set_page_config(page_title="Finance Dashboard", layout="wide")
# Mock data
def generate_mock_data():
    np.random.seed(42)
    dates = pd.date_range(datetime.date(2025, 1, 1), periods=90, freq="D")
    categories = ["Food", "Transport", "Shopping", "Bills", "Salary", "Entertainment", "Health"]
    types = ["Income", "Expense"]

    data = pd.DataFrame({
        "Date": np.random.choice(dates, 120),
        "Amount": np.random.randint(50, 1000, 120),
        "Category": np.random.choice(categories, 120),
        "Type": np.random.choice(types, 120, p=[0.3, 0.7])  # more expenses than income
    })
    return data.sort_values("Date")

if "transactions" not in st.session_state:
    st.session_state.transactions = generate_mock_data()
if "role" not in st.session_state:
    st.session_state.role = "Viewer"

transactions = st.session_state.transactions


st.sidebar.header("⚙️ Settings")
theme = st.sidebar.radio("Theme", ["Light", "Dark"])

if theme == "Dark":
    st.markdown(
        """
        <style>
        body { background-color: #121212; color: #f5f5f5; }
        .stMetric { background-color: #1e1e1e; border-radius: 8px; padding: 10px; }
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        """
        <style>
        body { background-color: #f9f9f9; color: #333; }
        .stMetric { background-color: #ffffff; border-radius: 8px; padding: 10px; }
        </style>
        """,
        unsafe_allow_html=True
    )


st.title("💰 Interactive Finance Dashboard")
role = st.selectbox("Select Role", ["Viewer", "Admin"])
st.session_state.role = role


income = transactions[transactions["Type"]=="Income"]["Amount"].sum()
expenses = transactions[transactions["Type"]=="Expense"]["Amount"].sum()
balance = income - expenses

col1, col2, col3 = st.columns(3)
col1.metric("Total Balance", f"${balance}")
col2.metric("Income", f"${income}")
col3.metric("Expenses", f"${expenses}")


st.subheader("📈 Balance Trend Over Time")
transactions["Net"] = transactions.apply(lambda row: row.Amount if row.Type=="Income" else -row.Amount, axis=1)
transactions["Cumulative"] = transactions["Net"].cumsum()
fig_balance = px.line(transactions, x="Date", y="Cumulative", title="Balance Trend", markers=True)
fig_balance.update_layout(template="plotly_dark" if theme=="Dark" else "plotly_white")
st.plotly_chart(fig_balance, use_container_width=True)

st.subheader("🍕 Spending Breakdown by Category")
expense_data = transactions[transactions["Type"]=="Expense"].groupby("Category")["Amount"].sum().reset_index()
fig_pie = px.pie(expense_data, names="Category", values="Amount", title="Spending Breakdown")
fig_pie.update_layout(template="plotly_dark" if theme=="Dark" else "plotly_white")
st.plotly_chart(fig_pie, use_container_width=True)


st.subheader("📋 Transactions")
col_search, col_sort = st.columns([2,1])
search = col_search.text_input("Search by category")
sort_option = col_sort.selectbox("Sort by", ["Date", "Amount"])

filtered = transactions[transactions["Category"].str.contains(search, case=False)] if search else transactions
filtered = filtered.sort_values(by=sort_option, ascending=True)
st.dataframe(filtered)

if role == "Admin":
    st.subheader("➕ Add Transaction")
    with st.form("add_txn"):
        date = st.date_input("Date")
        amount = st.number_input("Amount", min_value=1)
        category = st.selectbox("Category", ["Food", "Transport", "Shopping", "Bills", "Salary", "Entertainment", "Health"])
        txn_type = st.selectbox("Type", ["Income", "Expense"])
        submitted = st.form_submit_button("Add")
        if submitted:
            new_txn = pd.DataFrame({"Date":[date], "Amount":[amount], "Category":[category], "Type":[txn_type]})
            st.session_state.transactions = pd.concat([transactions, new_txn], ignore_index=True)
            st.success("Transaction added!")


st.subheader("🔍 Insights")
if not expense_data.empty:
    highest_category = expense_data.loc[expense_data["Amount"].idxmax(), "Category"]
    st.write(f"Highest spending category: **{highest_category}** (${expense_data['Amount'].max()})")
else:
    st.write("No expenses recorded yet.")

monthly = transactions.groupby(transactions["Date"].dt.month)["Amount"].sum().reset_index()
monthly["Month"] = monthly["Date"].apply(lambda x: datetime.date(2025, x, 1).strftime("%B"))
fig_monthly = px.bar(monthly, x="Month", y="Amount", title="Monthly Spending Comparison", color="Amount", text_auto=True)
fig_monthly.update_layout(template="plotly_dark" if theme=="Dark" else "plotly_white")
st.plotly_chart(fig_monthly, use_container_width=True)


avg_daily_expense = transactions[transactions["Type"]=="Expense"]["Amount"].mean()
projected_monthly_expense = avg_daily_expense * 30
st.info(f"📊 Based on current trends, your projected monthly expense is around **${int(projected_monthly_expense)}**.")

#Export Option
if st.sidebar.button("Export Transactions (CSV)"):
    st.sidebar.download_button("Download CSV", transactions.to_csv(index=False), "transactions.csv", "text/csv")
