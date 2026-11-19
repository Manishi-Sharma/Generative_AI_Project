"""
Page: Financial Data Management
Handles manual ledger entry, CSV bulk uploads with schema validation,
historical review, and financial metrics calculations.
"""

from typing import Any
import streamlit as st
import pandas as pd
from database.connection import get_db_context
from modules.financial_data import (
    get_financial_dataframe,
    add_financial_record,
    import_financial_csv,
)
from modules.authentication import check_permission
from utils.calculations import format_currency


def render_financial_records_page(current_user: Any, current_org: Any) -> None:
    st.markdown("## 📊 Financial Data Management")
    st.markdown(f"**Entity:** `{current_org.name}` | Isolated Ledger Records")

    with get_db_context() as db:
        df_fin = get_financial_dataframe(db, current_org.id)

    tab_view, tab_add, tab_upload = st.tabs([
        "📋 Historical Ledger & Ratios",
        "➕ Manual Period Entry",
        "📤 Bulk CSV Import"
    ])

    with tab_view:
        if df_fin.empty:
            st.info("No records recorded yet. Enter a record manually or upload a CSV file.")
        else:
            st.markdown(f"**{len(df_fin)} Historical Financial Periods Recorded**")
            
            # Format display dataframe
            display_df = df_fin.copy()
            display_df["Period"] = [f"Q{int(q)} {int(y)}" for y, q in zip(display_df["year"], display_df["quarter"])]
            
            currency = current_org.currency
            format_cols = [
                "revenue", "operating_expenses", "operating_profit", "net_profit",
                "cash_reserves", "assets", "liabilities"
            ]
            for col in format_cols:
                if col in display_df.columns:
                    display_df[col] = display_df[col].apply(lambda x: format_currency(x, currency))

            display_df["profit_margin"] = display_df["profit_margin"].apply(lambda x: f"{x:.1f}%")
            display_df["current_ratio"] = display_df["current_ratio"].apply(lambda x: f"{x:.2f}x")
            display_df["debt_ratio"] = display_df["debt_ratio"].apply(lambda x: f"{x:.2f}")

            cols_to_show = [
                "Period", "revenue", "operating_expenses", "operating_profit",
                "net_profit", "profit_margin", "cash_reserves", "current_ratio", "debt_ratio"
            ]
            st.dataframe(display_df[cols_to_show], use_container_width=True)

            # Export raw CSV
            csv_data = df_fin.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Export Ledger to CSV",
                data=csv_data,
                file_name=f"{current_org.name.replace(' ', '_')}_financial_records.csv",
                mime="text/csv",
            )

    with tab_add:
        if not check_permission(current_user.role, "add_financial_record"):
            st.warning("Your role does not permit entering financial records. Financial Manager or Administrator role required.")
        else:
            st.markdown("### Record Financial Performance for Fiscal Period")
            with st.form("form_add_record"):
                c1, c2, c3 = st.columns(3)
                with c1:
                    year = st.number_input("Year", min_value=2000, max_value=2100, value=2026)
                    revenue = st.number_input("Gross Revenue (₹)", min_value=0.0, step=100000.0, value=30000000.0)
                    salaries = st.number_input("Salaries & Payroll (₹)", min_value=0.0, step=50000.0, value=9000000.0)
                    electricity = st.number_input("Utilities / Power (₹)", min_value=0.0, step=10000.0, value=1500000.0)
                    rd_exp = st.number_input("R&D Spending (₹)", min_value=0.0, step=50000.0, value=1200000.0)

                with c2:
                    quarter = st.selectbox("Quarter", options=[1, 2, 3, 4], index=0)
                    opex = st.number_input("Total Operating Expenses (₹)", min_value=0.0, step=100000.0, value=22000000.0)
                    prod_costs = st.number_input("Production / Operations (₹)", min_value=0.0, step=50000.0, value=8500000.0)
                    marketing = st.number_input("Sales & Marketing (₹)", min_value=0.0, step=50000.0, value=1200000.0)
                    admin_cost = st.number_input("Administration & Legal (₹)", min_value=0.0, step=50000.0, value=1000000.0)

                with c3:
                    investments = st.number_input("Investments Made (₹)", min_value=0.0, step=100000.0, value=3000000.0)
                    cash_reserves = st.number_input("Liquid Cash Reserves (₹)", min_value=0.0, step=100000.0, value=20000000.0)
                    assets = st.number_input("Total Assets (₹)", min_value=0.0, step=500000.0, value=125000000.0)
                    liabilities = st.number_input("Total Liabilities (₹)", min_value=0.0, step=500000.0, value=35000000.0)
                    taxes = st.number_input("Taxes (₹)", min_value=0.0, step=50000.0, value=1200000.0)
                    loan_pay = st.number_input("Loan / Debt Servicing (₹)", min_value=0.0, step=50000.0, value=800000.0)

                notes = st.text_input("Operational Notes", placeholder="e.g. Robust Q1 performance with higher OEM shipment volumes")
                submit_record = st.form_submit_button("Save Period Financial Record", type="primary")

                if submit_record:
                    record_data = {
                        "year": year,
                        "quarter": quarter,
                        "revenue": revenue,
                        "operating_expenses": opex,
                        "salaries": salaries,
                        "production_costs": prod_costs,
                        "electricity": electricity,
                        "marketing": marketing,
                        "administration": admin_cost,
                        "rd_expenses": rd_exp,
                        "investments": investments,
                        "assets": assets,
                        "liabilities": liabilities,
                        "cash_reserves": cash_reserves,
                        "taxes": taxes,
                        "loan_payments": loan_pay,
                        "notes": notes,
                    }
                    with get_db_context() as db:
                        success, rec, msg = add_financial_record(db, current_org.id, record_data)
                    if success:
                        st.success(f"Record for Q{quarter} {year} added successfully!")
                        st.rerun()
                    else:
                        st.error(msg)

    with tab_upload:
        if not check_permission(current_user.role, "upload_csv"):
            st.warning("Your role does not permit bulk CSV upload.")
        else:
            st.markdown("### Import Financial Data via CSV")
            st.write("Upload comma-separated values containing quarterly balance sheet and operating records.")

            # Sample CSV Download
            from config import DATA_DIR
            sample_file = DATA_DIR / "sample_financial_data.csv"
            if sample_file.exists():
                with open(sample_file, "r") as f:
                    st.download_button(
                        label="📄 Download Sample CSV Template",
                        data=f.read(),
                        file_name="financial_butterfly_sample_template.csv",
                        mime="text/csv",
                    )

            uploaded_file = st.file_uploader("Select Financial CSV File", type=["csv"])
            if uploaded_file:
                with get_db_context() as db:
                    success, count, errors = import_financial_csv(db, current_org.id, uploaded_file)
                if success:
                    st.success(f"Successfully imported {count} financial records into {current_org.name}!")
                    st.rerun()
                else:
                    st.error("Failed to import CSV:")
                    for err in errors:
                        st.write(f"- ❌ {err}")
