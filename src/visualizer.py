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


def create_enhanced_portfolio_chart(
    ef_returns: np.ndarray,
    ef_volatilities: np.ndarray,
    max_sharpe_data: Dict,
    min_vol_data: Dict,
    max_utility_data: Dict,
    random_portfolios: tuple[np.ndarray, np.ndarray, np.ndarray],
    risk_aversion: float
) -> str:
    """
    Create an enhanced visualization with efficient frontier, three optimal portfolios,
    random portfolios, and allocation pie charts.

    Args:
        ef_returns: Array of efficient frontier returns
        ef_volatilities: Array of efficient frontier volatilities
        max_sharpe_data: Dict with 'weights', 'return', 'volatility', 'sharpe'
        min_vol_data: Dict with 'weights', 'return', 'volatility', 'sharpe'
        max_utility_data: Dict with 'weights', 'return', 'volatility', 'sharpe'
        random_portfolios: Tuple of (returns, volatilities, sharpe_ratios) arrays
        risk_aversion: Risk aversion parameter used

    Returns:
        HTML string containing the enhanced visualization
    """
    # Create subplots: 2 rows, 2 columns
    # Row 1: Efficient frontier (spans 2 columns)
    # Row 2: Three pie charts for allocations
    fig = make_subplots(
        rows=2, cols=3,
        subplot_titles=(
            'Efficient Frontier with Random Portfolios', None, None,
            'Max Sharpe Portfolio', 'Min Volatility Portfolio', 'Max Utility Portfolio'
        ),
        specs=[
            [{'type': 'scatter', 'colspan': 3}, None, None],
            [{'type': 'pie'}, {'type': 'pie'}, {'type': 'pie'}]
        ],
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )

    # Unpack random portfolios
    rand_returns, rand_vols, rand_sharpes = random_portfolios

    # Add random portfolios as background scatter (colored by Sharpe ratio)
    fig.add_trace(
        go.Scatter(
            x=rand_vols,
            y=rand_returns,
            mode='markers',
            name='Random Portfolios',
            marker=dict(
                size=3,
                color=rand_sharpes,
                colorscale='Viridis_r',
                showscale=True,
                colorbar=dict(title='Sharpe<br>Ratio', x=1.02),
                opacity=0.5
            ),
            hovertemplate='Volatility: %{x:.2%}<br>Return: %{y:.2%}<extra></extra>',
            showlegend=True
        ),
        row=1, col=1
    )

    # Add efficient frontier line
    fig.add_trace(
        go.Scatter(
            x=ef_volatilities,
            y=ef_returns,
            mode='lines',
            name='Efficient Frontier',
            line=dict(color='#0068ff', width=3),
            hovertemplate='Volatility: %{x:.2%}<br>Return: %{y:.2%}<extra></extra>'
        ),
        row=1, col=1
    )

    # Add Max Sharpe portfolio
    fig.add_trace(
        go.Scatter(
            x=[max_sharpe_data['volatility']],
            y=[max_sharpe_data['return']],
            mode='markers',
            name='Max Sharpe',
            marker=dict(color='#ff433d', size=15, symbol='star', line=dict(color='white', width=2)),
            hovertemplate=f"Max Sharpe<br>Return: {max_sharpe_data['return']:.2%}<br>Volatility: {max_sharpe_data['volatility']:.2%}<br>Sharpe: {max_sharpe_data['sharpe']:.2f}<extra></extra>"
        ),
        row=1, col=1
    )

    # Add Min Volatility portfolio
    fig.add_trace(
        go.Scatter(
            x=[min_vol_data['volatility']],
            y=[min_vol_data['return']],
            mode='markers',
            name='Min Volatility',
            marker=dict(color='#4af6c3', size=15, symbol='star', line=dict(color='white', width=2)),
            hovertemplate=f"Min Volatility<br>Return: {min_vol_data['return']:.2%}<br>Volatility: {min_vol_data['volatility']:.2%}<br>Sharpe: {min_vol_data['sharpe']:.2f}<extra></extra>"
        ),
        row=1, col=1
    )

    # Add Max Utility portfolio
    fig.add_trace(
        go.Scatter(
            x=[max_utility_data['volatility']],
            y=[max_utility_data['return']],
            mode='markers',
            name='Max Utility',
            marker=dict(color='#fb8b1e', size=15, symbol='star', line=dict(color='white', width=2)),
            hovertemplate=f"Max Utility<br>Return: {max_utility_data['return']:.2%}<br>Volatility: {max_utility_data['volatility']:.2%}<br>Sharpe: {max_utility_data['sharpe']:.2f}<extra></extra>"
        ),
        row=1, col=1
    )

    # Add pie charts for each portfolio
    # Max Sharpe
    sorted_max_sharpe = dict(sorted(max_sharpe_data['weights'].items(), key=lambda x: x[1], reverse=True))
    fig.add_trace(
        go.Pie(
            labels=list(sorted_max_sharpe.keys()),
            values=list(sorted_max_sharpe.values()),
            texttemplate='%{label}<br>%{percent:.1%}',
            hovertemplate='%{label}<br>Weight: %{percent:.2%}<extra></extra>',
            marker=dict(line=dict(color='white', width=2)),
            showlegend=False
        ),
        row=2, col=1
    )

    # Min Volatility
    sorted_min_vol = dict(sorted(min_vol_data['weights'].items(), key=lambda x: x[1], reverse=True))
    fig.add_trace(
        go.Pie(
            labels=list(sorted_min_vol.keys()),
            values=list(sorted_min_vol.values()),
            texttemplate='%{label}<br>%{percent:.1%}',
            hovertemplate='%{label}<br>Weight: %{percent:.2%}<extra></extra>',
            marker=dict(line=dict(color='white', width=2)),
            showlegend=False
        ),
        row=2, col=2
    )

    # Max Utility
    sorted_max_utility = dict(sorted(max_utility_data['weights'].items(), key=lambda x: x[1], reverse=True))
    fig.add_trace(
        go.Pie(
            labels=list(sorted_max_utility.keys()),
            values=list(sorted_max_utility.values()),
            texttemplate='%{label}<br>%{percent:.1%}',
            hovertemplate='%{label}<br>Weight: %{percent:.2%}<extra></extra>',
            marker=dict(line=dict(color='white', width=2)),
            showlegend=False
        ),
        row=2, col=3
    )

    # Update layout
    fig.update_xaxes(title_text='Volatility (Risk)', tickformat='.1%', row=1, col=1)
    fig.update_yaxes(title_text='Expected Return', tickformat='.1%', row=1, col=1)

    # Create title with performance metrics
    title_html = f"""
    <b>Portfolio Optimization Results</b><br>
    <sub>
    Max Sharpe: Return={max_sharpe_data['return']:.2%}, Vol={max_sharpe_data['volatility']:.2%}, Sharpe={max_sharpe_data['sharpe']:.2f} |
    Min Vol: Return={min_vol_data['return']:.2%}, Vol={min_vol_data['volatility']:.2%}, Sharpe={min_vol_data['sharpe']:.2f} |
    Max Utility: Return={max_utility_data['return']:.2%}, Vol={max_utility_data['volatility']:.2%}, Sharpe={max_utility_data['sharpe']:.2f} (λ={risk_aversion})
    </sub>
    """

    fig.update_layout(
        title_text=title_html,
        showlegend=True,
        template='plotly_white',
        height=1000,
        width=1600
    )

    # Convert to HTML
    html = fig.to_html(include_plotlyjs='cdn')
    return html


def create_combined_chart(
    returns: np.ndarray,
    volatilities: np.ndarray,
    max_sharpe_point: tuple[float, float],
    weights: Dict[str, float],
    portfolio_metrics: tuple[float, float, float]
) -> str:
    """
    Create a combined visualization with efficient frontier and pie chart.

    DEPRECATED: Use create_enhanced_portfolio_chart for new implementations.

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
