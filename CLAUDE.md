# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Terminal Portfolio Optimizer (TPO) is a terminal-based application for Vietnamese stock portfolio optimization using modern portfolio theory. It combines:
- **Textual TUI** for keyboard-driven input
- **vnstock3** for Vietnamese stock market data
- **PyPortfolioOpt** for mean-variance optimization
- **Plotly** for interactive visualizations
- **PyWebView** for native chart display (runs in separate process)

## Critical Architecture Rules

### ⚠️ Textual + PyWebView Threading Requirements

**NEVER call `webview.start()` from Textual's event loop or Screen methods.**

**Problem:**
- Both Textual and PyWebView require the **main thread**
- Textual runs async event loop on main thread
- PyWebView's `webview.start()` MUST run on main thread (macOS Cocoa requirement)
- Calling `webview.start()` from Textual event handler creates deadlock

**Solution - Multiprocessing Architecture:**
1. **PyWebView runs in separate process** (`src/webview_process.py`)
   - Gets its own main thread (satisfies Cocoa requirements)
   - Launched via `subprocess.Popen()` from Textual worker thread
   - Accepts HTML via base64-encoded command-line argument

2. **Textual uses worker threads** for blocking operations
   - Use `@work(thread=True)` decorator for data fetching and optimization
   - Never block the main event loop with long-running tasks

3. **Thread-safe UI updates** from worker threads
   - **ALWAYS use:** `self.app.call_from_thread()` when in Screen class
   - **NEVER use:** `self.call_from_thread()` - AttributeError (Screen doesn't inherit this)
   - Pattern:
     ```python
     @work(thread=True, exclusive=True)
     def my_worker(self):
         result = blocking_operation()
         # CORRECT: Access App's call_from_thread from Screen
         self.app.call_from_thread(widget.update, result)
     ```

**Current Implementation:**
- `src/webview_process.py`: Standalone PyWebView runner
- `src/visualizer.py`: Uses `subprocess.Popen()` to launch webview process
- `src/main.py`: Uses `@work(thread=True)` with `self.app.call_from_thread()` for UI updates

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
- `run_optimization_worker()`: Worker thread method decorated with `@work(thread=True, exclusive=True)`
  - Runs blocking operations (data fetch, optimization, visualization) in separate thread
  - **CRITICAL:** All UI updates use `self.app.call_from_thread()` (NOT `self.call_from_thread()`)
  - Thread-safe pattern required because Screen class doesn't inherit `call_from_thread`
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
  - Row 1: Efficient frontier with 1,000 random portfolios (colored by Sharpe using viridis colormap), plus 3 optimal portfolios as stars
  - Uses `go.Scattergl` (WebGL) for random portfolios - significantly faster than SVG `go.Scatter`
  - Row 2: Three pie charts showing allocations for Max Sharpe, Min Volatility, Max Utility
  - Size: 1400x900px
  - Bloomberg-inspired colors: blue (#0068ff), red (#ff433d), cyan (#4af6c3), orange (#fb8b1e)
- `create_combined_chart()`: **DEPRECATED** - Old 2-subplot layout (kept for backward compatibility)
- `display_charts()`: Launches PyWebView in **separate process** (lines 381-416)
  - Encodes HTML as base64 for safe command-line passing
  - Runs `subprocess.Popen()` to execute `src/webview_process.py`
  - **Does NOT call `webview.start()` directly** - avoids main thread conflict with Textual

**src/webview_process.py** - Standalone PyWebView runner
- Runs in separate process, gets its own main thread
- Accepts base64-encoded HTML via command-line argument
- Calls `webview.start()` on process's main thread (satisfies macOS Cocoa)
- Window size: 1400x900, `vibrancy=False` for macOS performance

**src/theme.tcss** - Bloomberg-inspired Textual CSS
- Dark theme with terminal aesthetics
- CSS variables use `$app-panel` (not `$panel` - reserved by Textual)
- Button variants use `.-primary` and `.-error` syntax (not `.primary`, `.error`)

### Data Flow

```
User Input (TUI) - Main Thread
  ↓
on_optimize() validates inputs
  ↓
run_optimization_worker() - Worker Thread (@work decorator)
  ↓
fetch_vn_stock_data() → Returns DataFrame with adjusted closing prices
  ↓
calculate_efficient_frontier() + generate_random_portfolios(n_samples=1000)
  ↓
get_max_sharpe_allocation() + get_min_volatility_allocation() + get_max_utility_allocation()
  ↓
create_enhanced_portfolio_chart() → HTML string (with go.Scattergl for WebGL)
  ↓
display_charts() → subprocess.Popen() launches webview_process.py
  ↓
webview_process.py - Separate Process (own main thread)
  ↓
webview.start() → PyWebView window opens
  ↓
[User closes window] → Process terminates
  ↓
Worker thread updates UI via self.app.call_from_thread()
  ↓
Return to TUI (loop for next run) - Main Thread
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
- **Worker threads** used for all blocking operations via `@work(thread=True, exclusive=True)` decorator
- **Thread-safe UI updates:** All widget updates from worker thread use `self.app.call_from_thread()`
  - **CRITICAL:** Must use `self.app.call_from_thread()` from Screen class, not `self.call_from_thread()`
  - Screen class doesn't inherit `call_from_thread` - raises AttributeError if used directly
- TUI remains responsive during optimization and visualization (no blocking of main event loop)

### Session Handling & Multiprocessing
- App runs in loop: user can perform multiple optimizations without restarting
- PyWebView runs in **separate process** (not thread) to avoid main thread conflict with Textual
- Each optimization spawns new webview process via `subprocess.Popen()`
- Process cleanup automatic when window closes (no manual cleanup needed)
- Worker thread waits for webview process termination, then updates UI
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
- Random portfolio generation (1,000 samples with WebGL) adds ~0.5-1 seconds
- Efficient frontier calculation (100 points) typically <1 second
- vnstock3 data fetching is the slowest component (network-dependent)
- PyWebView rendering in separate process: 1-2 seconds initial load
- Window close: <1 second (no window switching required on macOS)
- **WebGL optimization:** Using `go.Scattergl` instead of `go.Scatter` for 1,000+ points significantly reduces rendering time and DOM complexity

## Development Guidelines for Future Changes

### When Adding New Blocking Operations
1. **Always use worker threads** via `@work(thread=True)` decorator
2. **Never call blocking code** from Textual event handlers or main event loop
3. **Update UI safely** using `self.app.call_from_thread()` from worker threads
4. **Check for cancellation** using `get_current_worker().is_cancelled` in long loops

### When Modifying PyWebView Integration
1. **Never import `webview` directly** in main.py or any Textual Screen/Widget
2. **Always use subprocess** to launch webview_process.py in separate process
3. **Pass data via base64 encoding** in command-line arguments (not stdin for macOS compatibility)
4. **Never call `webview.start()`** from within Textual's execution context

### Thread Safety Checklist
- [ ] Using `@work(thread=True)` for blocking operations?
- [ ] Updating UI with `self.app.call_from_thread()` (not `self.call_from_thread()`)?
- [ ] Avoiding direct `webview.start()` calls from Textual context?
- [ ] Using separate process for PyWebView via subprocess?
- [ ] Handling worker cancellation appropriately?
