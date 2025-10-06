"""Data fetching module using vnstock3 for Vietnamese stock market data."""

from datetime import datetime
from typing import List, Tuple
import pandas as pd
from vnstock import Quote


class DataFetchError(Exception):
    """Custom exception for data fetching errors."""
    pass


def validate_tickers(tickers: List[str]) -> Tuple[List[str], List[str]]:
    """
    Validate Vietnamese stock tickers.

    Args:
        tickers: List of ticker symbols

    Returns:
        Tuple of (valid_tickers, invalid_tickers)
    """
    valid = []
    invalid = []

    for ticker in tickers:
        ticker = ticker.strip().upper()
        if ticker and len(ticker) >= 3:  # Basic validation for VN tickers
            valid.append(ticker)
        else:
            invalid.append(ticker)

    return valid, invalid


def fetch_vn_stock_data(
    tickers: List[str],
    start_date: str,
    end_date: str
) -> pd.DataFrame:
    """
    Fetch historical stock price data from vnstock3.

    Args:
        tickers: List of Vietnamese stock ticker symbols
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        DataFrame with adjusted closing prices, tickers as columns, dates as index

    Raises:
        DataFetchError: If data fetching fails or no valid data is retrieved
    """
    # Validate date format
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError as e:
        raise DataFetchError(f"Invalid date format. Use YYYY-MM-DD: {e}")

    # Validate tickers
    valid_tickers, invalid_tickers = validate_tickers(tickers)

    if invalid_tickers:
        raise DataFetchError(f"Invalid tickers found: {', '.join(invalid_tickers)}")

    if not valid_tickers:
        raise DataFetchError("No valid tickers provided")

    # Fetch data for each ticker
    price_data = {}
    failed_tickers = []

    for ticker in valid_tickers:
        try:
            # Fetch historical data using Quote directly
            quote = Quote(symbol=ticker, source='VCI')
            df = quote.history(
                start=start_date,
                end=end_date,
                interval='1D'
            )

            if df is not None and not df.empty and 'close' in df.columns:
                # Set time as index and use close price
                df = df.set_index('time')
                price_data[ticker] = df['close']
            else:
                failed_tickers.append(ticker)

        except Exception as e:
            failed_tickers.append(ticker)
            print(f"Warning: Failed to fetch data for {ticker}: {str(e)}")

    if not price_data:
        raise DataFetchError(
            f"Failed to fetch data for all tickers. Failed: {', '.join(failed_tickers)}"
        )

    if failed_tickers:
        print(f"Warning: Could not fetch data for: {', '.join(failed_tickers)}")

    # Combine into single DataFrame
    prices_df = pd.DataFrame(price_data)

    # Drop rows with any NaN values
    prices_df = prices_df.dropna()

    if prices_df.empty:
        raise DataFetchError("No valid price data available after cleaning")

    if len(prices_df) < 30:
        raise DataFetchError(
            f"Insufficient data points ({len(prices_df)}). Need at least 30 days of data."
        )

    return prices_df
