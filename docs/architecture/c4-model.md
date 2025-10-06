# C4 Model Architecture

This document follows the [C4 Model](https://c4model.com/) for visualizing software architecture at multiple levels of abstraction.

## Level 1: System Context Diagram

```mermaid
C4Context
    title System Context - Terminal Portfolio Optimizer

    Person(user, "Portfolio Manager", "Vietnamese stock investor seeking portfolio optimization")

    System(tpo, "Terminal Portfolio Optimizer", "TUI application for portfolio optimization using modern portfolio theory")

    System_Ext(vci, "VCI Stock Exchange", "Vietnamese stock market data provider via vnstock3 API")

    Rel(user, tpo, "Inputs tickers, dates, risk parameters", "Keyboard")
    Rel(tpo, vci, "Fetches historical price data", "HTTPS/API")
    Rel(tpo, user, "Displays optimized portfolios", "Terminal + WebView")
```

### External Dependencies
- **VCI Stock Exchange**: Provides real-time and historical Vietnamese stock data via vnstock3 API
- **Terminal Environment**: macOS/Linux terminal with Python 3.10+

### User Personas
- **Portfolio Manager**: Needs quick portfolio optimization for Vietnamese stocks
- **Retail Investor**: Seeks data-driven allocation recommendations
- **Risk Analyst**: Requires multiple optimization strategies (Max Sharpe, Min Vol, Max Utility)

## Level 2: Container Diagram

```mermaid
C4Container
    title Container Diagram - Terminal Portfolio Optimizer

    Person(user, "User", "Portfolio manager")

    Container_Boundary(tpo, "Terminal Portfolio Optimizer") {
        Container(tui, "Textual TUI", "Python/Textual", "Interactive terminal interface, main event loop")
        Container(worker, "Worker Threads", "Python/threading", "Handles blocking operations (data fetch, optimization)")
        Container(webview_proc, "WebView Process", "Python/PyWebView", "Separate process for chart visualization")

        ContainerDb(memory, "In-Memory Data", "pandas DataFrame", "Temporary storage for price data and optimization results")
    }

    System_Ext(vci_api, "vnstock3 API", "Vietnamese stock data provider")

    Rel(user, tui, "Inputs parameters", "Keyboard")
    Rel(tui, worker, "Spawns worker thread", "@work decorator")
    Rel(worker, vci_api, "Fetches price data", "HTTPS")
    Rel(worker, memory, "Stores/reads data", "pandas")
    Rel(worker, tui, "Updates UI", "call_from_thread()")
    Rel(worker, webview_proc, "Launches subprocess", "subprocess.Popen()")
    Rel(webview_proc, user, "Displays charts", "Native window")
```

### Container Responsibilities

#### Textual TUI (`src/main.py`)
- **Purpose**: Main application entry point and UI coordination
- **Technology**: Textual framework, runs on main thread
- **Key Classes**: `PortfolioApp`, `InputScreen`
- **Critical Constraint**: MUST run on main thread for event loop

#### Worker Threads
- **Purpose**: Execute blocking operations without freezing UI
- **Technology**: Python threading with `@work(thread=True)` decorator
- **Scope**: Data fetching, optimization calculations, subprocess management
- **Thread Safety**: All UI updates use `self.app.call_from_thread()`

#### WebView Process (`src/webview_process.py`)
- **Purpose**: Display Plotly charts in native window
- **Technology**: PyWebView with subprocess isolation
- **Critical Constraint**: MUST run on own main thread (macOS Cocoa requirement)
- **Communication**: Base64-encoded HTML via command-line arguments

#### In-Memory Data Store
- **Purpose**: Temporary storage during optimization session
- **Technology**: pandas DataFrame
- **Lifecycle**: Created per optimization run, discarded after visualization
- **No Persistence**: Application is stateless between runs

## Level 3: Component Diagram

```mermaid
C4Component
    title Component Diagram - Core Application Logic

    Container_Boundary(tui, "Textual TUI Container") {
        Component(app, "PortfolioApp", "Textual App", "Main application class, keyboard bindings, CSS theme")
        Component(input_screen, "InputScreen", "Textual Screen", "Input form for tickers, dates, risk parameters")
        Component(worker_coord, "Worker Coordinator", "Textual Worker", "Manages worker thread lifecycle and UI updates")
    }

    Container_Boundary(core, "Core Business Logic") {
        Component(data_fetcher, "DataFetcher", "vnstock3 wrapper", "Fetches and validates Vietnamese stock data")
        Component(optimizer, "PortfolioOptimizer", "PyPortfolioOpt wrapper", "Calculates efficient frontier and optimal allocations")
        Component(visualizer, "ChartVisualizer", "Plotly generator", "Creates interactive portfolio charts")
    }

    Container_Boundary(subprocess, "Visualization Process") {
        Component(webview_runner, "WebViewRunner", "PyWebView", "Standalone process for chart display")
    }

    Rel(input_screen, worker_coord, "Triggers optimization", "on_optimize()")
    Rel(worker_coord, data_fetcher, "Fetches data", "fetch_vn_stock_data()")
    Rel(worker_coord, optimizer, "Optimizes portfolio", "get_max_sharpe_allocation()")
    Rel(worker_coord, visualizer, "Generates chart HTML", "create_enhanced_portfolio_chart()")
    Rel(visualizer, webview_runner, "Launches subprocess", "subprocess.Popen()")
    Rel(webview_runner, worker_coord, "Process termination", "wait()")
    Rel(worker_coord, input_screen, "Updates UI", "call_from_thread()")
```

### Component Details

#### src/main.py
- **PortfolioApp**: Application root, manages global state and keyboard bindings
- **InputScreen**: Form validation, worker thread spawning, UI update coordination
- **run_optimization_worker()**: Worker method decorated with `@work(thread=True, exclusive=True)`

#### src/data_fetcher.py
- **fetch_vn_stock_data()**: Retrieves historical prices using vnstock3 Quote API
- **validate_tickers()**: Basic ticker symbol validation
- **DataFetchError**: Custom exception for data retrieval failures

#### src/optimizer.py
- **calculate_efficient_frontier()**: Generates 100-point risk-return curve
- **get_max_sharpe_allocation()**: Maximum Sharpe ratio portfolio
- **get_min_volatility_allocation()**: Minimum variance portfolio
- **get_max_utility_allocation()**: Quadratic utility optimization with risk aversion λ
- **generate_random_portfolios()**: 10,000 random portfolios via Dirichlet distribution
- **OptimizationError**: Custom exception for optimization failures

#### src/visualizer.py
- **create_enhanced_portfolio_chart()**: 2-row, 3-column Plotly chart (WebGL optimized)
- **display_charts()**: Subprocess launcher with base64 HTML encoding

#### src/webview_process.py
- **main()**: Standalone entry point, decodes HTML, calls `webview.start()`
- **Process lifecycle**: Owned by subprocess, terminates on window close

## Level 4: Code Organization

```
terminal-portfolio-optimizer/
├── src/
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # Textual TUI application (PortfolioApp, InputScreen)
│   ├── data_fetcher.py          # vnstock3 integration (fetch_vn_stock_data)
│   ├── optimizer.py             # PyPortfolioOpt integration (3 optimization strategies)
│   ├── visualizer.py            # Plotly chart generation + subprocess launcher
│   ├── webview_process.py       # Standalone PyWebView runner
│   └── theme.tcss               # Bloomberg-inspired Textual CSS
├── docs/
│   └── architecture/            # Architecture documentation
├── pyproject.toml               # Project metadata and dependencies
├── CLAUDE.md                    # Development guidelines and critical patterns
├── CHANGELOG.md                 # Version history
└── README.md                    # User-facing documentation
```

### Key Design Patterns

#### Worker Thread Pattern
```python
@work(thread=True, exclusive=True)
def run_optimization_worker(self):
    # Blocking operations run in separate thread
    data = fetch_vn_stock_data(...)
    allocation = get_max_sharpe_allocation(...)

    # UI updates are thread-safe
    self.app.call_from_thread(widget.update, result)
```

#### Subprocess Isolation Pattern
```python
# In visualizer.py
html_b64 = base64.b64encode(html.encode()).decode()
process = subprocess.Popen([
    sys.executable,
    webview_process_path,
    html_b64
])
process.wait()  # Non-blocking for worker thread
```

#### Thread-Safe UI Update Pattern
```python
# CORRECT: From Screen class
self.app.call_from_thread(widget.update, data)

# INCORRECT: AttributeError (Screen doesn't inherit this)
self.call_from_thread(widget.update, data)
```

## Cross-Cutting Concerns

### Error Handling
- Domain-specific exceptions: `DataFetchError`, `OptimizationError`
- All errors displayed in TUI's `#error-message` widget
- No crashes - application returns to input state

### Logging
- Currently uses print statements for warnings (e.g., failed ticker fetches)
- Future: Structured logging with log levels

### Configuration
- Hardcoded defaults in `InputScreen` (1-year lookback, 3% risk-free rate, λ=1.0)
- No external configuration files

### State Management
- Stateless design: Each optimization run is independent
- Input fields retain values between runs
- No database or file persistence
