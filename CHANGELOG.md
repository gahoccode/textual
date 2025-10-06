# Changelog

## [1.1.0] - 2025-10-06

### Added - Enhanced Portfolio Optimization

#### Modified Files

**src/optimizer.py**
- **New Functions Added:**
  - `get_min_volatility_allocation(prices: pd.DataFrame, risk_free_rate: float) -> Dict[str, float]`
    - Calculates minimum volatility portfolio allocation
    - Uses PyPortfolioOpt's min_volatility() method
    - Returns cleaned weights dictionary
  - `get_max_utility_allocation(prices: pd.DataFrame, risk_aversion: float, risk_free_rate: float) -> Dict[str, float]`
    - Calculates maximum utility portfolio using quadratic utility function
    - Takes risk aversion parameter (λ) as input
    - Uses PyPortfolioOpt's max_quadratic_utility() method
  - `generate_random_portfolios(mu: pd.Series, S: pd.DataFrame, n_samples: int) -> Tuple`
    - Generates random portfolio samples for visualization
    - Uses Dirichlet distribution for weight generation
    - Returns arrays of returns, volatilities, and Sharpe ratios for 10,000 portfolios

**src/visualizer.py**
- **New Functions Added:**
  - `create_enhanced_portfolio_chart(...) -> str`
    - Creates comprehensive 2-row visualization with 4 subplots
    - Row 1: Efficient frontier with 10,000 random portfolios (colored by Sharpe ratio using viridis colormap)
    - Plots 3 optimal portfolios as stars: Max Sharpe (red), Min Volatility (cyan), Max Utility (orange)
    - Row 2: Three pie charts showing allocation weights for each portfolio
    - Includes performance metrics in title for all three portfolios
    - Uses Bloomberg color palette: #0068ff (blue), #ff433d (red), #4af6c3 (cyan), #fb8b1e (orange)
- **Deprecated Functions:**
  - `create_combined_chart()` - Kept for backward compatibility, marked as DEPRECATED

**src/main.py**
- **New Imports:**
  - Added `get_min_volatility_allocation`, `get_max_utility_allocation`, `generate_random_portfolios`
  - Added `expected_returns`, `risk_models` from pypfopt
  - Changed to use `create_enhanced_portfolio_chart`
- **New Input Field:**
  - Risk Aversion (λ) input field with default value 1.0
  - Validation for risk aversion parameter
- **Enhanced Optimization Flow:**
  - Now calculates 3 portfolio types simultaneously:
    1. Maximum Sharpe Ratio portfolio
    2. Minimum Volatility portfolio
    3. Maximum Utility portfolio (using user-specified risk aversion)
  - Generates 10,000 random portfolios for comparison
  - Passes all data to enhanced visualization function

**src/theme.tcss**
- **CSS Variable Fixes:**
  - Changed `$panel` to `$app-panel` to avoid conflict with Textual's reserved variable names
  - Fixed `Button.error` to `Button.-error` for consistent variant naming

### Scope of Impact

**New Functionality:**
- Multi-portfolio comparison: Users can now compare 3 different optimization strategies side-by-side
- Random portfolio visualization: 10,000 randomly generated portfolios provide context for optimal portfolios
- Risk aversion parameter: Users can customize utility optimization based on their risk preferences

**Modified Functions:**
- src/optimizer.py: 3 new functions (lines 118-222)
- src/visualizer.py: 1 new function `create_enhanced_portfolio_chart` (lines 99-284)
- src/main.py: Enhanced optimization flow (lines 68-182)

**Performance:**
- Generation of 10,000 random portfolios adds ~1-2 seconds to computation time
- Larger visualization (1600x1000px vs 1400x600px) requires more memory

**User Experience:**
- More comprehensive analysis with minimal additional user input
- Bloomberg-themed colors provide professional, terminal-like aesthetics
- Interactive Plotly charts allow zooming and hovering for detailed metrics

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
