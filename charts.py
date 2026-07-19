import plotly.graph_objects as go


def gauge_chart(readiness_index, classification):
    """Gauge showing the overall readiness index (0-100)."""
    if readiness_index >= 75:
        bar_color = "#2e7d32"      # green
    elif readiness_index >= 50:
        bar_color = "#f9a825"      # amber
    else:
        bar_color = "#c62828"      # red

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=readiness_index,
            number={"suffix": "%", "font": {"size": 40}},
            title={"text": f"Readiness Index<br><b>{classification}</b>", "font": {"size": 18}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1},
                "bar": {"color": bar_color},
                "steps": [
                    {"range": [0, 50], "color": "#ffebee"},
                    {"range": [50, 75], "color": "#fff8e1"},
                    {"range": [75, 100], "color": "#e8f5e9"},
                ],
                "threshold": {
                    "line": {"color": "black", "width": 3},
                    "thickness": 0.75,
                    "value": readiness_index,
                },
            },
        )
    )
    fig.update_layout(height=320, margin=dict(l=20, r=20, t=60, b=20))
    return fig


def radar_chart(dimension_scores):
    """Radar chart of the six readiness dimensions."""
    categories = list(dimension_scores.keys())
    values = list(dimension_scores.values())

    # close the loop
    categories_closed = categories + [categories[0]]
    values_closed = values + [values[0]]

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=values_closed,
            theta=categories_closed,
            fill="toself",
            name="Your Profile",
            line=dict(color="#1565c0"),
            fillcolor="rgba(21, 101, 192, 0.25)",
        )
    )
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        height=320,
        margin=dict(l=40, r=40, t=40, b=40),
        title="Readiness by Dimension",
    )
    return fig
