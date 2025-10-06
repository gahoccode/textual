# Changelog

## [1.0.0] - 2025-10-06

### Added - Initial Implementation

#### New Files Created

**pyproject.toml**
- Project configuration with uv package manager
- Dependencies: textual, vnstock3, PyPortfolioOpt, plotly, pywebview, pandas, numpy
- Entry point script: `tpo`

**src/__init__.py**
- Package initialization
- Version: 1.0.0

**src/data_fetcher.py**
- **Functions Added:**
  - `validate_tickers(tickers: List[str]) -> Tuple[List[str], List[str]]`
    - Validates Vietnamese stock ticker symbols
    - Returns tuple of valid and invalid tickers
  - `fetch_vn_stock_data(tickers: List[str], start_date: str, end_date: str) -> pd.DataFrame`
    - Fetches historical price data from vnstock3
    - Validates date formats
    - Handles missing data gracefully
    - Returns DataFrame with adjusted closing prices
- **Custom Exceptions:**
  - `DataFetchError` - Raised for data fetching failures

**src/optimizer.py**
- **Functions Added:**
  - `calculate_efficient_frontier(prices: pd.DataFrame, risk_free_rate: float, num_points: int) -> Tuple`
    - Calculates efficient frontier using PyPortfolioOpt
    - Computes expected returns and covariance matrix
    - Returns arrays of returns, volatilities, and max Sharpe point
  - `get_max_sharpe_allocation(prices: pd.DataFrame, risk_free_rate: float) -> Dict[str, float]`
    - Optimizes portfolio for maximum Sharpe ratio
    - Returns cleaned weights dictionary (zero weights filtered)
  - `get_portfolio_performance(prices: pd.DataFrame, weights: Dict[str, float], risk_free_rate: float) -> Tuple`
    - Calculates portfolio metrics: return, volatility, Sharpe ratio
- **Custom Exceptions:**
  - `OptimizationError` - Raised for optimization failures

**src/visualizer.py**
- **Functions Added:**
  - `create_efficient_frontier_chart(returns: np.ndarray, volatilities: np.ndarray, max_sharpe_point: tuple) -> go.Figure`
    - Creates Plotly scatter plot of efficient frontier
    - Highlights max Sharpe ratio point with red star marker
  - `create_pie_chart(weights: Dict[str, float]) -> go.Figure`
    - Creates pie chart of portfolio allocation
    - Sorts weights descending
  - `create_combined_chart(...) -> str`
    - Combines frontier and pie chart in subplot layout
    - Includes portfolio metrics in title
    - Returns HTML string for webview display
  - `display_charts(html_content: str, title: str) -> None`
    - Launches PyWebView window with visualization
    - Window size: 1500x700, resizable

**src/main.py**
- **Classes Added:**
  - `InputScreen(Screen)`
    - Textual screen for user input collection
    - Input fields: tickers, start date, end date, risk-free rate
    - Default values: 1-year lookback, 3% risk-free rate
    - Event handlers:
      - `on_optimize()` - Orchestrates data fetch, optimization, visualization
      - `on_exit()` - Exits application
    - Error/success message display areas
  - `PortfolioApp(App)`
    - Main Textual application class
    - Key bindings: 'q' and 'Ctrl+C' to quit
    - Methods:
      - `on_mount()` - Pushes InputScreen on startup
      - `action_quit()` - Exit handler
- **Functions Added:**
  - `main() -> None`
    - Entry point for CLI execution
    - Instantiates and runs PortfolioApp

### Scope of Impact

**New Components:**
- Complete greenfield implementation
- 4 core modules: data_fetcher, optimizer, visualizer, main
- 15 total functions across all modules
- 3 custom exception classes
- Full TUI integration with Textual
- Interactive visualization with Plotly + PyWebView

**Dependencies:**
- vnstock3: Vietnamese stock market data source
- PyPortfolioOpt: Mean-variance optimization
- Plotly: Interactive charting
- PyWebView: Native window display
- Textual: Terminal UI framework

**Data Flow:**
1. User input (TUI) → Data fetcher (vnstock3)
2. Price data → Optimizer (PyPortfolioOpt)
3. Optimization results → Visualizer (Plotly)
4. HTML visualization → Display (PyWebView)
5. Return to TUI for next iteration

**Error Handling:**
- Input validation in main.py:134-145
- Data fetch errors in data_fetcher.py:44-122
- Optimization errors in optimizer.py:91-94
- User-friendly error messages in TUI

**Testing Considerations:**
- Ticker validation with Vietnamese market symbols
- Date range validation and edge cases
- Network failure handling for vnstock3
- Optimization convergence for various portfolio sizes
- UI responsiveness during long-running operations

### Modified Files
None (greenfield project)
