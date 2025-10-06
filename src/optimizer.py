"""Portfolio optimization module using PyPortfolioOpt."""

from typing import Dict, Tuple
import pandas as pd
import numpy as np
from pypfopt import EfficientFrontier, risk_models, expected_returns
from pypfopt.exceptions import OptimizationError


class OptimizationError(Exception):
    """Custom exception for optimization errors."""
    pass


def calculate_efficient_frontier(
    prices: pd.DataFrame,
    risk_free_rate: float = 0.03,
    num_points: int = 100
) -> Tuple[np.ndarray, np.ndarray, Tuple[float, float]]:
    """
    Calculate the efficient frontier.

    Args:
        prices: DataFrame of historical prices (tickers as columns)
        risk_free_rate: Annual risk-free rate (default 3%)
        num_points: Number of points to calculate on the frontier

    Returns:
        Tuple of (returns_array, volatilities_array, (max_sharpe_return, max_sharpe_vol))
    """
    # Calculate expected returns and covariance matrix
    mu = expected_returns.mean_historical_return(prices)
    S = risk_models.sample_cov(prices)

    returns_range = []
    volatilities_range = []

    # Get the min and max possible returns
    ef_temp = EfficientFrontier(mu, S)
    try:
        ef_temp.min_volatility()
        min_ret = ef_temp.portfolio_performance()[0]
    except:
        min_ret = mu.min()

    ef_temp = EfficientFrontier(mu, S)
    try:
        ef_temp.max_sharpe(risk_free_rate=risk_free_rate)
        max_ret = ef_temp.portfolio_performance()[0]
    except:
        max_ret = mu.max()

    # Calculate frontier points
    target_returns = np.linspace(min_ret, max_ret * 1.2, num_points)

    for target_return in target_returns:
        try:
            ef_temp = EfficientFrontier(mu, S)
            ef_temp.efficient_return(target_return)
            ret, vol, _ = ef_temp.portfolio_performance()
            returns_range.append(ret)
            volatilities_range.append(vol)
        except (OptimizationError, ValueError):
            # Skip if optimization fails for this point
            continue

    # Calculate max Sharpe portfolio
    ef_max = EfficientFrontier(mu, S)
    ef_max.max_sharpe(risk_free_rate=risk_free_rate)
    max_sharpe_return, max_sharpe_vol, _ = ef_max.portfolio_performance()

    return (
        np.array(returns_range),
        np.array(volatilities_range),
        (max_sharpe_return, max_sharpe_vol)
    )


def get_max_sharpe_allocation(
    prices: pd.DataFrame,
    risk_free_rate: float = 0.03
) -> Dict[str, float]:
    """
    Calculate the maximum Sharpe ratio portfolio allocation.

    Args:
        prices: DataFrame of historical prices (tickers as columns)
        risk_free_rate: Annual risk-free rate (default 3%)

    Returns:
        Dictionary of {ticker: weight} for the optimal portfolio

    Raises:
        OptimizationError: If optimization fails
    """
    try:
        # Calculate expected returns and covariance matrix
        mu = expected_returns.mean_historical_return(prices)
        S = risk_models.sample_cov(prices)

        # Optimize for maximum Sharpe ratio
        ef = EfficientFrontier(mu, S)
        weights = ef.max_sharpe(risk_free_rate=risk_free_rate)
        cleaned_weights = ef.clean_weights()

        # Get performance metrics
        ret, vol, sharpe = ef.portfolio_performance(verbose=False)

        # Filter out zero weights
        cleaned_weights = {k: v for k, v in cleaned_weights.items() if v > 0.0001}

        return cleaned_weights

    except Exception as e:
        raise OptimizationError(f"Failed to optimize portfolio: {str(e)}")


def get_portfolio_performance(
    prices: pd.DataFrame,
    weights: Dict[str, float],
    risk_free_rate: float = 0.03
) -> Tuple[float, float, float]:
    """
    Calculate portfolio performance metrics.

    Args:
        prices: DataFrame of historical prices
        weights: Dictionary of portfolio weights
        risk_free_rate: Annual risk-free rate

    Returns:
        Tuple of (expected_return, volatility, sharpe_ratio)
    """
    mu = expected_returns.mean_historical_return(prices)
    S = risk_models.sample_cov(prices)

    # Convert weights dict to the order of columns in prices
    weights_array = np.array([weights.get(col, 0) for col in prices.columns])

    # Calculate metrics
    portfolio_return = np.dot(weights_array, mu)
    portfolio_vol = np.sqrt(np.dot(weights_array, np.dot(S, weights_array)))
    sharpe = (portfolio_return - risk_free_rate) / portfolio_vol

    return portfolio_return, portfolio_vol, sharpe
