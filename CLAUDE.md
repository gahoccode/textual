# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Terminal Portfolio Optimizer (TPO) is a terminal-based application for Vietnamese stock portfolio optimization using modern portfolio theory. It combines:
- **Textual TUI** for keyboard-driven input
- **vnstock3** for Vietnamese stock market data
- **PyPortfolioOpt** for mean-variance optimization
- **Plotly** for interactive visualizations
- **PyWebView** for native chart display

## Commands

### Run the application
```bash
uv run tpo
```

**In activated virtual env**
```bash
tpo
```

### Install dependencies
```bash
uv sync
```

### Run directly via Python
```bash
python3 -m src.main
```

## Architecture

### Module Structure

**src/main.py** - Textual TUI application
- `PortfolioApp`: Main Textual App class with keyboard bindings ('q', 'Ctrl+C' to quit)
- `InputScreen`: Collects user inputs (tickers, dates, risk-free rate, risk aversion)
- Orchestrates the full workflow: input → fetch → optimize → visualize → loop
- References CSS from `src/theme.tcss` via `CSS_PATH` (line 214)

**src/data_fetcher.py** - vnstock3 data integration
- `fetch_vn_stock_data()`: Retrieves historical price data using vnstock's Quote API
- `validate_tickers()`: Basic validation for Vietnamese stock symbols (≥3 chars)
- Custom exception: `DataFetchError`
- Requires minimum 30 days of data for optimization

**src/optimizer.py** - PyPortfolioOpt integration
- `calculate_efficient_frontier()`: Generates 100-point efficient frontier
- `get_max_sharpe_allocation()`: Maximum Sharpe ratio portfolio
- `get_min_volatility_allocation()`: Minimum volatility portfolio
- `get_max_utility_allocation()`: Maximum utility using quadratic utility function (risk aversion parameter)
- `generate_random_portfolios()`: Creates 10,000 random portfolios using Dirichlet distribution
- `get_portfolio_performance()`: Calculates return, volatility, Sharpe ratio for any portfolio
- All functions use PyPortfolioOpt's mean_historical_return and sample_cov
- Custom exception: `OptimizationError`

**src/visualizer.py** - Plotly + PyWebView visualization
- `create_enhanced_portfolio_chart()`: **CURRENT** - Creates 2-row, 3-column subplot:
  - Row 1: Efficient frontier with 10,000 random portfolios (colored by Sharpe using viridis colormap), plus 3 optimal portfolios as stars
  - Row 2: Three pie charts showing allocations for Max Sharpe, Min Volatility, Max Utility
  - Size: 1600x1000px
  - Bloomberg-inspired colors: blue (#0068ff), red (#ff433d), cyan (#4af6c3), orange (#fb8b1e)
- `create_combined_chart()`: **DEPRECATED** - Old 2-subplot layout (kept for backward compatibility)
- `display_charts()`: Launches PyWebView window (1500x700, resizable)

**src/theme.tcss** - Bloomberg-inspired Textual CSS
- Dark theme with terminal aesthetics
- CSS variables use `$app-panel` (not `$panel` - reserved by Textual)
- Button variants use `.-primary` and `.-error` syntax (not `.primary`, `.error`)

### Data Flow

```
User Input (TUI)
  ↓
fetch_vn_stock_data() → Returns DataFrame with adjusted closing prices
  ↓
calculate_efficient_frontier() + generate_random_portfolios()
  ↓
get_max_sharpe_allocation() + get_min_volatility_allocation() + get_max_utility_allocation()
  ↓
create_enhanced_portfolio_chart() → HTML string
  ↓
display_charts() → PyWebView window (blocks until closed)
  ↓
Return to TUI (loop for next run)
```

## Important Implementation Details

### vnstock3 Integration
- Uses `Quote(symbol=ticker, source='VCI')` for data fetching
- Data returned with 'time' column as index, 'close' column for prices
- Failed ticker fetches print warnings but don't crash - continues with remaining valid tickers
- Requires at least 30 data points across all tickers after cleaning (src/data_fetcher.py:114)

### Portfolio Optimization
- Three simultaneous optimization strategies computed for comparison:
  1. **Max Sharpe**: Traditional risk-adjusted return optimization
  2. **Min Volatility**: Conservative approach, lowest risk
  3. **Max Utility**: User-customizable via risk aversion parameter (λ)
- Random portfolios generated using `np.random.dirichlet()` for proper weight distribution
- Weights below 0.0001 are filtered out in cleaned_weights dictionaries

### Textual TUI Specifics
- CSS file referenced via `CSS_PATH = Path(__file__).parent / "theme.tcss"` in PortfolioApp (main.py:214)
- Error/success messages displayed in dedicated Static widgets (`#error-message`, `#success-message`)
- Input validation happens synchronously before optimization starts
- PyWebView window blocks execution - TUI becomes responsive again after window closes

### Session Handling
- App runs in loop: user can perform multiple optimizations without restarting
- After closing PyWebView, success message updates to prompt for next action
- Exit via dedicated button or keybindings ('q', 'Ctrl+C')

## Testing Considerations

- **Ticker validation**: Test with valid Vietnamese symbols (FPT, VNM, VIC, etc.) and invalid ones
- **Date range edge cases**: Very short periods (<30 days), future dates, malformed dates
- **Network failures**: vnstock3 API unavailability should be handled gracefully
- **Optimization convergence**: Test with 2-5 stocks (typical) and 20-30 stocks (performance limits)
- **Risk aversion parameter**: Test with λ values from 0.1 (aggressive) to 10.0 (conservative)

## Known Architecture Patterns

### Error Handling Strategy
- Custom exceptions (`DataFetchError`, `OptimizationError`) for domain-specific errors
- Generic `Exception` caught at top level in main.py:201 for unexpected errors
- All errors displayed in TUI's error message widget - no crashes
- Warnings (like failed individual ticker fetches) print to stdout but don't halt execution

### State Management
- No persistent state - each optimization run is independent
- Input fields retain values between runs (user can modify incrementally)
- Default values: 1-year lookback, 3% risk-free rate, 1.0 risk aversion

### Performance Notes
- Random portfolio generation (10,000 samples) adds ~1-2 seconds
- Efficient frontier calculation (100 points) typically <1 second
- vnstock3 data fetching is the slowest component (network-dependent)
- PyWebView rendering is instantaneous with Plotly CDN
