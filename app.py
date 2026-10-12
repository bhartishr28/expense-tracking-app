import streamlit as st
import pandas as pd
import plotly.express as px

import os
from dotenv import load_dotenv
from supabase import create_client

from excel_report import create_excel_report

from database import get_categories,get_payment_methods,add_expenses,get_expenses,update_expenses,delete_expenses
from datetime import date

load_dotenv()

st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💰",
    layout="wide"
)


# Read configuration from .env locally or Streamlit Secrets online
def get_setting(name):
    value = os.getenv(name)

    if value:
        return value

    try:
        return st.secrets[name]
    except Exception:
        return None


supabase_url = get_setting("SUPABASE_URL")
supabase_key = get_setting("SUPABASE_KEY")

#st.write("URL being used:", repr(supabase_url))

app_username = get_setting("APP_USERNAME")
auth_email = get_setting("SUPABASE_AUTH_EMAIL")



# Require login before displaying the application
if not st.session_state.get("authenticated", False):

    st.title("💰 Expense Tracker Login")
    st.write("Please log in to continue.")

    if not all([supabase_url, supabase_key, app_username, auth_email]):
        st.error(
            "Login configuration is incomplete. "
            "Check your .env file and Streamlit Cloud Secrets."
        )
        st.stop()

    with st.form("login_form"):

        username = st.text_input("Username")
        password = st.text_input(
            "Password",
            type="password"
        )

        submitted = st.form_submit_button(
            "Login",
            use_container_width=True
        )

    if submitted:

        if username.strip() != app_username:
            st.error("Invalid username or password.")

        else:
            try:
                supabase_client = create_client(
                    supabase_url,
                    supabase_key
                )

                supabase_client.auth.sign_in_with_password({
                    "email": auth_email,
                    "password": password
                })

                st.session_state.authenticated = True
                st.session_state.page = "Dashboard"

                st.rerun()

            except Exception as e:
                st.error(
                    f"Login failed: {e}"
                )

    st.stop()


# Main application — visible only after login
st.title("Expense Tracker")
st.sidebar.title("💰 Expense Tracker")

if st.sidebar.button("🚪 Log out", use_container_width=True):
    st.session_state.authenticated = False
    st.session_state.page = "Dashboard"
    st.rerun()

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"


if st.sidebar.button("📊 Dashboard", use_container_width=True):
    st.session_state.page = "Dashboard"

if st.sidebar.button("➕ Add Expense", use_container_width=True):
    st.session_state.page = "Add Expense"

if st.sidebar.button("📋 View Expenses", use_container_width=True):
    st.session_state.page = "View Expenses"

if st.sidebar.button("✏️ Update Expense", use_container_width=True):
    st.session_state.page = "Update Expense"

if st.sidebar.button("🗑️ Delete Expense", use_container_width=True):
    st.session_state.page = "Delete Expense"

if st.sidebar.button("📄 Reports", use_container_width=True):
    st.session_state.page = "Reports"


option = st.session_state.page

categories = get_categories()
payment_methods = get_payment_methods()
expenses = get_expenses()

# Dashboard
if option == "Dashboard":

    st.subheader("Expense Dashboard")

    # Date range
    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input(
            "From Date",
            value=date(2026, 10, 1)
        )

    with col2:
        end_date = st.date_input(
            "To Date"
        )

    # Filter expenses
    filtered_expenses = []

    for expense in expenses:

        if start_date <= expense[1] <= end_date:
            filtered_expenses.append(expense)

    # Total expenses
    total_expenses = 0

    for expense in filtered_expenses:
        total_expenses = total_expenses + float(expense[4])

    # Number of expenses
    number_of_expenses = len(filtered_expenses)

    if number_of_expenses > 0:
        average_expense = total_expenses / number_of_expenses
    else:
        average_expense = 0

    # KPI cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Expenses",
            f"₹{total_expenses:,.2f}"
        )

    with col2:
        st.metric(
            "Number of Expenses",
            number_of_expenses
        )

    with col3:
        st.metric(
            "Average Expense",
            f"₹{average_expense:,.2f}"
        )

    # Expense table
    st.subheader("Expenses")

    columns = [
        "ID",
        "Date",
        "Category",
        "Description",
        "Amount",
        "Payment Method",
        "Notes"
    ]

    df = pd.DataFrame(
        filtered_expenses,
        columns=columns
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    # Expenses by category
    st.subheader("Expenses by Category")

    category_totals = {}

    for expense in filtered_expenses:

        category = expense[2]
        amount = float(expense[4])

        if category in category_totals:
            category_totals[category] = (
                category_totals[category] + amount
            )
        else:
            category_totals[category] = amount

    category_df = pd.DataFrame(
        category_totals.items(),
        columns=["Category", "Total Expense"]
    )

    fig = px.bar(
        category_df,
        x="Category",
        y="Total Expense",
        title="Expenses by Category"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
    # Monthly spending trend

    # Prepare date-based data for charts
    trend_data = []

    for expense in filtered_expenses:
        expense_date = pd.to_datetime(expense[1]).date()

        trend_data.append({
            "Date": expense_date,
            "Amount": float(expense[4])
        })

    trend_df = pd.DataFrame(trend_data)

    # Daily Spending Trend
    st.subheader("Daily Spending Trend")

    if not trend_df.empty:
        daily_df = (
            trend_df.groupby("Date", as_index=False)["Amount"]
            .sum()
            .sort_values("Date")
        )

        fig = px.line(
            daily_df,
            x="Date",
            y="Amount",
            title="Daily Spending Trend",
            markers=True,
            labels={
                "Date": "Date",
                "Amount": "Total Spending (₹)"
            }
        )

        fig.update_xaxes(
            tickformat="%d %b",
            title="Date",
            tickangle=-45
        )

        fig.update_layout(
            hovermode="x unified"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )
    else:
        st.info("No expenses found for the selected date range.")

    # Monthly Spending Trend
    st.subheader("Monthly Spending Trend")

    if not trend_df.empty:
        trend_df["Month"] = pd.to_datetime(
            trend_df["Date"]
        ).dt.to_period("M").astype(str)

        monthly_df = (
            trend_df.groupby("Month", as_index=False)["Amount"]
            .sum()
            .sort_values("Month")
        )

        fig = px.bar(
            monthly_df,
            x="Month",
            y="Amount",
            title="Monthly Spending Trend",
            labels={
                "Month": "Month",
                "Amount": "Total Spending (₹)"
            }
        )

        fig.update_xaxes(
            tickformat="%b %Y",
            title="Month",
            type="category"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )
    else:
        st.info("No expenses found for the selected date range.")


# Add Expenses
elif option == "Add Expense":

    st.subheader("Add Expense")

    with st.form("expense_form"):

        col1, col2 = st.columns(2)

        with col1:
            expense_date = st.date_input("Expense Date")

        with col2:
            category = st.selectbox(
                "Category",
                categories,
                format_func=lambda x: x[1]
            )

        col1, col2 = st.columns(2)

        with col1:
            description = st.text_input("Description")

        with col2:
            amount = st.number_input(
                "Amount",
                min_value=0.01,
                step=0.01
            )

        col1, col2 = st.columns(2)

        with col1:
            payment_method = st.selectbox(
                "Payment Method",
                payment_methods,
                format_func=lambda x: x[1]
            )

        with col2:
            notes = st.text_input("Notes")

        submitted = st.form_submit_button("Add Expense")

    if submitted:

        category_id = category[0]
        payment_method_id = payment_method[0]

        expense_id = add_expenses(
            expense_date,
            category_id,
            description,
            amount,
            payment_method_id,
            notes
        )

        st.success(
            f"Expense added successfully! ID: {expense_id}"
        )

elif option == "View Expenses":

    st.subheader("View Expenses")

    expenses = get_expenses()

    columns = [
        "ID",
        "Date",
        "Category",
        "Description",
        "Amount",
        "Payment Method",
        "Notes"
    ]

    df = pd.DataFrame(expenses, columns=columns)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

elif option == "Update Expense":

    st.subheader("Update Expense")

    expense = st.selectbox(
        "Select Expense",
        expenses,
        format_func=lambda x: (
            f"ID: {x[0]} | "
            f"Date: {x[1]} | "
            f"Category: {x[2]} | "
            f"Description: {x[3]} | "
            f"Amount: ₹{x[4]} | "
            f"Payment: {x[5]} | "
            f"Notes: {x[6]}"
        )
    )

    with st.form("edit_expense_form"):

        col1, col2 = st.columns(2)

        with col1:
            expense_date = st.date_input(
                "Expense Date",
                value=expense[1]
            )

        with col2:
            category_names = []

            for c in categories:
                category_names.append(c[1])

            category = st.selectbox(
                "Category",
                category_names,
                index=category_names.index(expense[2])
            )

        col1, col2 = st.columns(2)

        with col1:
            description = st.text_input(
                "Description",
                value=expense[3]
            )

        with col2:
            amount = st.number_input(
                "Amount",
                min_value=0.01,
                value=float(expense[4]),
                step=0.01
            )

        col1, col2 = st.columns(2)

        with col1:
            payment_method_names = []

            for p in payment_methods:
                payment_method_names.append(p[1])

            payment_method = st.selectbox(
                "Payment Method",
                payment_method_names,
                index=payment_method_names.index(expense[5])
            )

        with col2:
            notes = st.text_input(
                "Notes",
                value=expense[6] or ""
            )

        update = st.form_submit_button("Update Expense")

    if update:

        category_id = None

        for c in categories:
            if c[1] == category:
                category_id = c[0]

        payment_method_id = None

        for p in payment_methods:
            if p[1] == payment_method:
                payment_method_id = p[0]

        update_expenses(
            expense[0],
            expense_date,
            category_id,
            description,
            amount,
            payment_method_id,
            notes
        )

        st.success("Expense updated successfully!")

elif option == "Delete Expense":

    st.subheader("Delete Expense")

    expense = st.selectbox(
        "Select Expense",
        expenses,
        format_func=lambda x: (
            f"ID: {x[0]} | "
            f"Date: {x[1]} | "
            f"Category: {x[2]} | "
            f"Description: {x[3]} | "
            f"Amount: ₹{x[4]} | "
            f"Payment: {x[5]}"
        )
    )

    confirm = st.checkbox(
        "I want to delete this expense"
    )

    if st.button("Delete Expense"):

        if confirm:
            delete_expenses(expense[0])
            st.success("Expense deleted successfully!")

        else:
            st.warning(
                "Please confirm before deleting."
            )

elif option == "Reports":

    st.subheader("Expense Report")

    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input("From Date")

    with col2:
        end_date = st.date_input("To Date")

    filtered_expenses = []

    for expense in expenses:
        if start_date <= expense[1] <= end_date:
            filtered_expenses.append(expense)

    st.write(
        f"Number of Expenses: {len(filtered_expenses)}"
    )

    if st.button("Generate Excel Report"):

        import tempfile

        with tempfile.NamedTemporaryFile(
            suffix=".xlsx",
            delete=False
        ) as temp_file:

            file_path = temp_file.name

        create_excel_report(
            filtered_expenses,
            file_path
        )

        with open(file_path, "rb") as file:

            st.download_button(
                label="Download Excel Report",
                data=file,
                file_name="expense_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )