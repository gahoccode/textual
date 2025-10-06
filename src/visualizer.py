"""Visualization module using Plotly and PyWebView."""

from typing import Dict
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import webview


def create_efficient_frontier_chart(
    returns: np.ndarray,
    volatilities: np.ndarray,
    max_sharpe_point: tuple[float, float]
) -> go.Figure:
    """
    Create an efficient frontier chart using Plotly.

    Args:
        returns: Array of portfolio returns
        volatilities: Array of portfolio volatilities
        max_sharpe_point: Tuple of (return, volatility) for max Sharpe portfolio

    Returns:
        Plotly Figure object
    """
    fig = go.Figure()

    # Add efficient frontier line
    fig.add_trace(go.Scatter(
        x=volatilities,
        y=returns,
        mode='lines',
        name='Efficient Frontier',
        line=dict(color='blue', width=2),
        hovertemplate='Volatility: %{x:.2%}<br>Return: %{y:.2%}<extra></extra>'
    ))

    # Add max Sharpe ratio point
    fig.add_trace(go.Scatter(
        x=[max_sharpe_point[1]],
        y=[max_sharpe_point[0]],
        mode='markers',
        name='Max Sharpe Ratio',
        marker=dict(color='red', size=12, symbol='star'),
        hovertemplate='Max Sharpe<br>Volatility: %{x:.2%}<br>Return: %{y:.2%}<extra></extra>'
    ))

    fig.update_layout(
        title='Efficient Frontier',
        xaxis_title='Volatility (Risk)',
        yaxis_title='Expected Return',
        hovermode='closest',
        showlegend=True,
        template='plotly_white',
        height=500
    )

    # Format axes as percentages
    fig.update_xaxes(tickformat='.1%')
    fig.update_yaxes(tickformat='.1%')

    return fig


def create_pie_chart(weights: Dict[str, float]) -> go.Figure:
    """
    Create a pie chart of portfolio weights.

    Args:
        weights: Dictionary of {ticker: weight}

    Returns:
        Plotly Figure object
    """
    # Sort by weight descending
    sorted_weights = dict(sorted(weights.items(), key=lambda x: x[1], reverse=True))

    labels = list(sorted_weights.keys())
    values = list(sorted_weights.values())

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        texttemplate='%{label}<br>%{percent:.1%}',
        hovertemplate='%{label}<br>Weight: %{percent:.2%}<extra></extra>',
        marker=dict(line=dict(color='white', width=2))
    )])

    fig.update_layout(
        title='Max Sharpe Portfolio Allocation',
        showlegend=True,
        template='plotly_white',
        height=500
    )

    return fig


def create_combined_chart(
    returns: np.ndarray,
    volatilities: np.ndarray,
    max_sharpe_point: tuple[float, float],
    weights: Dict[str, float],
    portfolio_metrics: tuple[float, float, float]
) -> str:
    """
    Create a combined visualization with efficient frontier and pie chart.

    Args:
        returns: Array of portfolio returns
        volatilities: Array of portfolio volatilities
        max_sharpe_point: Tuple of (return, volatility) for max Sharpe portfolio
        weights: Dictionary of {ticker: weight}
        portfolio_metrics: Tuple of (return, volatility, sharpe_ratio)

    Returns:
        HTML string containing the combined visualization
    """
    # Create subplots: 1 row, 2 columns
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Efficient Frontier', 'Max Sharpe Portfolio Allocation'),
        specs=[[{'type': 'scatter'}, {'type': 'pie'}]],
        horizontal_spacing=0.15
    )

    # Add efficient frontier to subplot 1
    fig.add_trace(
        go.Scatter(
            x=volatilities,
            y=returns,
            mode='lines',
            name='Efficient Frontier',
            line=dict(color='blue', width=2),
            hovertemplate='Volatility: %{x:.2%}<br>Return: %{y:.2%}<extra></extra>'
        ),
        row=1, col=1
    )

    # Add max Sharpe point to subplot 1
    fig.add_trace(
        go.Scatter(
            x=[max_sharpe_point[1]],
            y=[max_sharpe_point[0]],
            mode='markers',
            name='Max Sharpe Ratio',
            marker=dict(color='red', size=12, symbol='star'),
            hovertemplate='Max Sharpe<br>Volatility: %{x:.2%}<br>Return: %{y:.2%}<extra></extra>'
        ),
        row=1, col=1
    )

    # Add pie chart to subplot 2
    sorted_weights = dict(sorted(weights.items(), key=lambda x: x[1], reverse=True))
    labels = list(sorted_weights.keys())
    values = list(sorted_weights.values())

    fig.add_trace(
        go.Pie(
            labels=labels,
            values=values,
            texttemplate='%{label}<br>%{percent:.1%}',
            hovertemplate='%{label}<br>Weight: %{percent:.2%}<extra></extra>',
            marker=dict(line=dict(color='white', width=2))
        ),
        row=1, col=2
    )

    # Update layout
    fig.update_xaxes(title_text='Volatility (Risk)', tickformat='.1%', row=1, col=1)
    fig.update_yaxes(title_text='Expected Return', tickformat='.1%', row=1, col=1)

    ret, vol, sharpe = portfolio_metrics

    fig.update_layout(
        title_text=f'Portfolio Optimization Results<br><sub>Expected Return: {ret:.2%} | Volatility: {vol:.2%} | Sharpe Ratio: {sharpe:.2f}</sub>',
        showlegend=True,
        template='plotly_white',
        height=600,
        width=1400
    )

    # Convert to HTML
    html = fig.to_html(include_plotlyjs='cdn')
    return html


def display_charts(html_content: str, title: str = "Portfolio Optimization Results") -> None:
    """
    Display charts in a PyWebView window.

    Args:
        html_content: HTML string containing the visualization
        title: Window title
    """
    webview.create_window(
        title=title,
        html=html_content,
        width=1500,
        height=700,
        resizable=True
    )
    webview.start()
