"""
Plotly visualization engine with a bespoke Deep Navy / Emerald Green / Gold luxury theme.
Generates interactive charts for the Financial Butterfly Effect application.
"""

from typing import Dict, List, Any, Optional
import networkx as nx
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Theme Colors
BG_DARK = "#0b132b"
CARD_BG = "#1c2541"
TEXT_COLOR = "#e2e8f0"
TEXT_MUTED = "#94a3b8"
EMERALD = "#10b981"
EMERALD_LIGHT = "#34d399"
GOLD = "#f59e0b"
GOLD_LIGHT = "#fbbf24"
CYAN = "#06b6d4"
ROSE = "#f43f5e"
PURPLE = "#a855f7"

COMMON_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=TEXT_COLOR, family="Segoe UI, Inter, sans-serif"),
    margin=dict(l=40, r=40, t=50, b=40),
    hoverlabel=dict(bgcolor=CARD_BG, font_color=TEXT_COLOR, bordercolor=GOLD),
)


def plot_revenue_vs_expenses(df: pd.DataFrame) -> go.Figure:
    """Line and bar chart comparing historical revenue vs operating expenses and net profit."""
    fig = go.Figure()

    if df.empty:
        fig.add_annotation(text="No Financial Records Available", showarrow=False, font=dict(size=14, color=TEXT_MUTED))
        fig.update_layout(**COMMON_LAYOUT)
        return fig

    # Period labels
    periods = [f"Q{int(q)} {int(y)}" for y, q in zip(df["year"], df["quarter"])]

    fig.add_trace(go.Bar(
        x=periods,
        y=df["revenue"],
        name="Revenue",
        marker=dict(color=EMERALD, opacity=0.85),
    ))

    fig.add_trace(go.Bar(
        x=periods,
        y=df["operating_expenses"],
        name="Operating Expenses",
        marker=dict(color=ROSE, opacity=0.85),
    ))

    if "net_profit" in df.columns:
        fig.add_trace(go.Scatter(
            x=periods,
            y=df["net_profit"],
            name="Net Profit",
            mode="lines+markers",
            line=dict(color=GOLD, width=3),
            marker=dict(size=8, color=GOLD_LIGHT),
        ))

    fig.update_layout(
        **COMMON_LAYOUT,
        title="<b>Revenue vs Operating Expenses & Net Profit</b>",
        barmode="group",
        xaxis=dict(showgrid=False, title="Fiscal Period", color=TEXT_MUTED),
        yaxis=dict(showgrid=True, gridcolor="#273549", title="Amount (₹)", color=TEXT_MUTED),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def plot_expense_distribution(record: Dict[str, float]) -> go.Figure:
    """Donut chart showing operational cost breakdown across key departments and lines."""
    categories = [
        ("Salaries", record.get("salaries", 0.0)),
        ("Production Costs", record.get("production_costs", 0.0)),
        ("R&D", record.get("rd_expenses", 0.0)),
        ("Marketing", record.get("marketing", 0.0)),
        ("Administration", record.get("administration", 0.0)),
        ("Electricity & Utilities", record.get("electricity", 0.0)),
    ]
    # Filter non-zero
    labels = [c[0] for c in categories if c[1] > 0]
    values = [c[1] for c in categories if c[1] > 0]

    if not values:
        fig = go.Figure()
        fig.add_annotation(text="No Expense Details Available", showarrow=False, font=dict(size=14, color=TEXT_MUTED))
        fig.update_layout(**COMMON_LAYOUT)
        return fig

    palette = [EMERALD, GOLD, CYAN, ROSE, PURPLE, "#38bdf8"]
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker=dict(colors=palette[:len(labels)]),
        textinfo="label+percent",
        textfont=dict(color=TEXT_COLOR, size=12),
    )])

    fig.update_layout(
        **COMMON_LAYOUT,
        title="<b>Operating Expense Allocation Breakdown</b>",
        showlegend=True,
        legend=dict(orientation="v", x=1.05, y=0.5, font=dict(color=TEXT_MUTED)),
    )
    return fig


def plot_investment_allocation(investments_df: pd.DataFrame) -> go.Figure:
    """Pie/Donut chart illustrating portfolio allocation across asset classes."""
    if investments_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No Active Investments", showarrow=False, font=dict(size=14, color=TEXT_MUTED))
        fig.update_layout(**COMMON_LAYOUT)
        return fig

    grouped = investments_df.groupby("category")["amount"].sum().reset_index()

    fig = go.Figure(data=[go.Pie(
        labels=grouped["category"],
        values=grouped["amount"],
        hole=0.5,
        marker=dict(colors=[EMERALD, GOLD, CYAN, PURPLE, ROSE, "#3b82f6"]),
        textinfo="label+percent",
    )])

    fig.update_layout(
        **COMMON_LAYOUT,
        title="<b>Investment Portfolio Allocation by Category</b>",
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
    )
    return fig


def plot_network_dependency_graph(
    G: nx.DiGraph,
    impact_deltas: Optional[Dict[str, float]] = None
) -> go.Figure:
    """
    Renders an interactive NetworkX Directed Financial Dependency Graph in Plotly.
    Nodes are colored based on positive/negative ripple impact deltas if provided.
    Edges show directional causal dependencies with weights.
    """
    fig = go.Figure()

    # Pre-calculated layout positions (Spring / Shell / Circular layout)
    pos = nx.spring_layout(G, seed=42, k=1.8, iterations=60)

    # Edge traces
    edge_x = []
    edge_y = []
    edge_text = []

    for u, v, data in G.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        weight = data.get("weight", 0.0)
        desc = data.get("description", "")
        edge_text.append(f"{u} → {v}<br>Sensitivity: {weight:+.2f}<br>{desc}")

    fig.add_trace(go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=1.5, color="rgba(148, 163, 184, 0.4)"),
        hoverinfo="none",
        mode="lines",
        name="Dependencies",
    ))

    # Node coordinates, sizes, and colors
    node_x = []
    node_y = []
    node_text = []
    node_colors = []
    node_sizes = []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

        delta = (impact_deltas or {}).get(node, 0.0)
        
        # Color nodes: green for positive ripple, red for negative ripple, gold for original shock, cyan default
        if impact_deltas:
            if abs(delta) < 0.001:
                color = CYAN
            elif delta > 0:
                color = EMERALD
            else:
                color = ROSE
        else:
            color = CYAN

        node_colors.append(color)
        node_sizes.append(34)
        node_text.append(f"<b>{node}</b><br>Ripple Impact: {delta:+.2%}" if impact_deltas else f"<b>{node}</b>")

    fig.add_trace(go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=[n.replace(" ", "<br>") for n in G.nodes()],
        textposition="top center",
        hoverinfo="text",
        hovertext=node_text,
        textfont=dict(color=TEXT_COLOR, size=11, family="Inter, sans-serif"),
        marker=dict(
            size=node_sizes,
            color=node_colors,
            line=dict(color=CARD_BG, width=3),
            opacity=0.95
        ),
        name="Financial Nodes",
    ))

    fig.update_layout(
        **COMMON_LAYOUT,
        title="<b>The Financial Butterfly Effect: Directed Dependency Network</b>",
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    )
    return fig


def plot_multi_stage_butterfly_ripple(
    periods: List[str],
    node_trajectories: Dict[str, List[float]]
) -> go.Figure:
    """
    Plots multi-period ripple effects for key nodes across time steps (T+1 to T+5).
    """
    fig = go.Figure()

    palette = [EMERALD, GOLD, CYAN, ROSE, PURPLE, "#38bdf8", "#f472b6", "#a3e635"]
    
    for i, (node, trajectory) in enumerate(node_trajectories.items()):
        color = palette[i % len(palette)]
        fig.add_trace(go.Scatter(
            x=periods,
            y=[val * 100 for val in trajectory],  # Convert to percentage delta
            mode="lines+markers",
            name=node,
            line=dict(color=color, width=2.5),
            marker=dict(size=7, color=color),
        ))

    fig.update_layout(
        **COMMON_LAYOUT,
        title="<b>Multi-Period Ripple Trajectory (% Cumulative Change)</b>",
        xaxis=dict(title="Simulation Period", showgrid=False, color=TEXT_MUTED),
        yaxis=dict(title="Cumulative Delta (%)", showgrid=True, gridcolor="#273549", color=TEXT_MUTED),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
    )
    return fig


def plot_scenario_comparison(scenarios: Dict[str, Dict[str, float]]) -> go.Figure:
    """
    Bar chart comparing key financial outcomes (Revenue, Cash Reserves, Net Profit)
    across Baseline, Optimistic, and Pessimistic scenarios.
    """
    fig = go.Figure()

    scenario_names = list(scenarios.keys())
    metrics = ["Revenue", "Net Profit", "Cash Reserves", "Liquidity Ratio"]

    colors = [CYAN, EMERALD, GOLD, ROSE]

    for i, metric in enumerate(metrics):
        values = [scenarios[sc].get(metric, 0.0) for sc in scenario_names]
        fig.add_trace(go.Bar(
            name=metric,
            x=scenario_names,
            y=values,
            marker_color=colors[i % len(colors)],
        ))

    fig.update_layout(
        **COMMON_LAYOUT,
        title="<b>Strategic Scenario Comparison (Projected Outcomes)</b>",
        barmode="group",
        xaxis=dict(showgrid=False, color=TEXT_MUTED),
        yaxis=dict(showgrid=True, gridcolor="#273549", color=TEXT_MUTED),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def plot_monte_carlo_distribution(
    simulated_values: List[float],
    baseline_value: float,
    metric_name: str = "Net Profit"
) -> go.Figure:
    """
    Histogram and KDE distribution for Monte Carlo simulation outcomes.
    Highlights 5th percentile (VaR), 50th percentile (Median), and 95th percentile.
    """
    fig = go.Figure()

    sim_array = np.array(simulated_values)
    p5 = np.percentile(sim_array, 5)
    p50 = np.percentile(sim_array, 50)
    p95 = np.percentile(sim_array, 95)

    fig.add_trace(go.Histogram(
        x=sim_array,
        nbinsx=40,
        marker=dict(color=CYAN, opacity=0.7, line=dict(color=BG_DARK, width=1)),
        name="Simulated Distributions",
    ))

    # Add percentile vertical lines
    fig.add_vline(x=baseline_value, line_width=2, line_dash="dash", line_color=GOLD, annotation_text="Baseline")
    fig.add_vline(x=p5, line_width=2, line_dash="dot", line_color=ROSE, annotation_text=f"5th %ile (VaR)")
    fig.add_vline(x=p50, line_width=2, line_dash="solid", line_color=EMERALD, annotation_text="Median")
    fig.add_vline(x=p95, line_width=2, line_dash="dot", line_color=EMERALD_LIGHT, annotation_text="95th %ile")

    fig.update_layout(
        **COMMON_LAYOUT,
        title=f"<b>Monte Carlo Risk Distribution ({metric_name})</b>",
        xaxis=dict(title=f"Simulated {metric_name} (₹)", showgrid=False, color=TEXT_MUTED),
        yaxis=dict(title="Frequency", showgrid=True, gridcolor="#273549", color=TEXT_MUTED),
    )
    return fig


def plot_risk_radar(scores: Dict[str, float]) -> go.Figure:
    """Radar chart mapping multi-dimensional financial risk vectors (0 to 100 scale)."""
    categories = list(scores.keys())
    values = list(scores.values())

    # Close the radar loop
    categories_closed = categories + [categories[0]]
    values_closed = values + [values[0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=categories_closed,
        fill="toself",
        fillcolor="rgba(244, 63, 94, 0.35)",
        line=dict(color=ROSE, width=2.5),
        name="Risk Exposure",
    ))

    fig.update_layout(
        **COMMON_LAYOUT,
        title="<b>Multi-Dimensional Financial Risk Radar</b>",
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#273549", color=TEXT_MUTED),
            angularaxis=dict(gridcolor="#273549", color=TEXT_COLOR),
            bgcolor=CARD_BG,
        ),
        showlegend=False,
    )
    return fig
