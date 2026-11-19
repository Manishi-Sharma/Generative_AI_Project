"""
Page: Financial Predictions & Anomaly Detection
Uses Scikit-learn Linear Regression and Random Forest Regressors for multi-period forecasting,
and Isolation Forest for identifying irregular transactions and financial anomalies.
"""

from typing import Any
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from database.connection import get_db_context
from modules.financial_data import get_financial_dataframe
from modules.ai_prediction import train_forecast_models, detect_financial_anomalies
from utils.calculations import format_currency


def render_predictions_page(current_user: Any, current_org: Any) -> None:
    st.markdown("## 🔮 Machine Learning Financial Forecasting & Anomaly Detection")
    st.markdown(f"**Entity:** `{current_org.name}` | Statistical Trajectory Modelling")

    with get_db_context() as db:
        df_fin = get_financial_dataframe(db, current_org.id)

    if df_fin.empty:
        st.warning("Insufficient financial data to train forecasting models. Record at least 3-4 historical periods.")
        return

    currency = current_org.currency

    tab_forecast, tab_anomaly = st.tabs([
        "📈 Predictive Trajectory Models",
        "🚨 Isolation Forest Anomaly Detection"
    ])

    with tab_forecast:
        st.markdown("### Quarterly Financial Forecasting Engine")
        
        target_metric = st.selectbox(
            "Select Forecast Target",
            options=["revenue", "operating_expenses", "cash_reserves"],
            format_func=lambda x: x.replace("_", " ").title()
        )
        quarters_ahead = st.slider("Forecast Horizon (Quarters Ahead)", min_value=1, max_value=8, value=4)

        with st.spinner("Training Scikit-learn Regression Models..."):
            forecast_results = train_forecast_models(
                df=df_fin,
                target_column=target_metric,
                forecast_quarters=quarters_ahead,
            )

        if forecast_results["status"] == "insufficient_data":
            st.warning(forecast_results["message"])
        else:
            if forecast_results.get("is_limited_sample"):
                st.info(f"ℹ️ **Baseline Notice:** Sample contains {forecast_results['sample_size']} historical periods. Models use transparent baseline extrapolation.")

            # Metric Performance Cards
            m = forecast_results["metrics"]
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.metric("Linear Regression MAE", format_currency(m["linear_regression"]["mae"], currency, abbreviate=True))
            with col_m2:
                st.metric("Linear Regression RMSE", format_currency(m["linear_regression"]["rmse"], currency, abbreviate=True))
            with col_m3:
                r2_val = m["linear_regression"].get("r2", 1.0)
                st.metric("Coefficient of Determination (R²)", f"{r2_val:.3f}")

            # Plot Forecast vs History
            df_hist = df_fin.sort_values(by=["year", "quarter"]).reset_index(drop=True)
            hist_periods = [f"Q{int(q)} {int(y)}" for y, q in zip(df_hist["year"], df_hist["quarter"])]
            hist_vals = df_hist[target_metric].tolist()

            fc_table = forecast_results["forecast_table"]
            fc_periods = fc_table["Period"].tolist()
            fc_ensemble = fc_table["Ensemble Forecast (₹)"].tolist()

            fig = go.Figure()
            # Historical trace
            fig.add_trace(go.Scatter(
                x=hist_periods,
                y=hist_vals,
                mode="lines+markers",
                name="Historical Actuals",
                line=dict(color="#38bdf8", width=3),
                marker=dict(size=8, color="#38bdf8"),
            ))
            # Connecting link from last actual to first forecast
            conn_x = [hist_periods[-1]] + fc_periods
            conn_y = [hist_vals[-1]] + fc_ensemble
            fig.add_trace(go.Scatter(
                x=conn_x,
                y=conn_y,
                mode="lines+markers",
                name="Ensemble Forecast (LR + RF)",
                line=dict(color="#10b981", width=3, dash="dash"),
                marker=dict(size=8, color="#10b981"),
            ))

            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e2e8f0"),
                title=f"<b>Historical Actuals vs ML Projected {forecast_results['target_metric']}</b>",
                xaxis=dict(showgrid=False, title="Fiscal Period", color="#94a3b8"),
                yaxis=dict(showgrid=True, gridcolor="#273549", title=f"Amount ({currency})", color="#94a3b8"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=40, r=40, t=50, b=40),
            )
            st.plotly_chart(fig, use_container_width=True)

            # Table of Projected Values
            disp_fc = fc_table.copy()
            for col in ["Linear Regression (₹)", "Random Forest (₹)", "Ensemble Forecast (₹)"]:
                disp_fc[col] = disp_fc[col].apply(lambda x: format_currency(x, currency))
            st.dataframe(disp_fc, use_container_width=True)

    with tab_anomaly:
        st.markdown("### Isolation Forest Anomaly Detection")
        st.write("Identifies uncharacteristic surges in operational expenditures, sudden margin contractions, or anomalous balance sheet shifts.")

        df_anomalies = detect_financial_anomalies(df_fin)
        anomaly_count = int(df_anomalies["is_anomaly"].sum())

        if anomaly_count == 0:
            st.success("✅ **No Anomalous Transactions Detected.** All recorded financial quarters conform to expected variance bounds.")
        else:
            st.warning(f"⚠️ **{anomaly_count} Anomalous Financial Periods Identified by Isolation Forest.** Review flagged quarters below:")

        disp_ano = df_anomalies.copy()
        disp_ano["Period"] = [f"Q{int(q)} {int(y)}" for y, q in zip(disp_ano["year"], disp_ano["quarter"])]
        disp_ano["Status"] = disp_ano["is_anomaly"].apply(lambda x: "🚨 ANOMALY" if x else "Normal")
        
        for c in ["revenue", "operating_expenses", "cash_reserves"]:
            disp_ano[c] = disp_ano[c].apply(lambda x: format_currency(x, currency))

        cols = ["Period", "revenue", "operating_expenses", "cash_reserves", "anomaly_score", "Status"]
        st.dataframe(disp_ano[cols], use_container_width=True)
