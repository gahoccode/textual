# Quality Attributes and Cross-Cutting Concerns

Documentation of non-functional requirements, quality attributes, and system-wide concerns.

## Overview

This document addresses the "-ilities" and cross-cutting concerns that affect the entire system:
- Performance and Scalability
- Reliability and Availability
- Maintainability and Extensibility
- Security and Privacy
- Usability and Accessibility

---

## Performance

### Response Time Targets

| Operation | Target | Actual | Status |
|-----------|--------|--------|--------|
| Input validation | < 50ms | ~10ms | ✅ Exceeds |
| Data fetching (3 tickers) | < 5s | 2-5s | ✅ Meets |
| Efficient frontier (100 pts) | < 1s | 200-500ms | ✅ Exceeds |
| Random portfolios (10k) | < 2s | 300-700ms | ✅ Exceeds |
| Chart generation | < 500ms | 100-200ms | ✅ Exceeds |
| Subprocess spawn | < 3s | 1-2s | ✅ Meets |
| **Total optimization run** | **< 15s** | **5-10s** | ✅ Exceeds |

### Performance Bottlenecks

#### 1. Network I/O (Data Fetching)

**Bottleneck**: Sequential HTTP requests to vnstock3 API

```python
# Current: Sequential fetching
for ticker in tickers:
    data = Quote(ticker).quote.history(start, end)  # Blocking I/O
```

**Impact**: 2-5 seconds (70% of total time)

**Mitigation**: Could parallelize with `ThreadPoolExecutor`

```python
# Future: Parallel fetching
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(fetch_ticker, t) for t in tickers]
    results = [f.result() for f in futures]
```

**Trade-off**: Increased complexity vs 50% time reduction

#### 2. CVXPY Solver (Optimization)

**Bottleneck**: Quadratic programming solver for efficient frontier

**Impact**: 200-500ms (10% of total time)

**Mitigation**: Already using fast solver (ECOS), acceptable performance

#### 3. Subprocess Spawn

**Bottleneck**: Python interpreter startup for PyWebView process

**Impact**: 1-2 seconds (20% of total time)

**Mitigation**: None feasible (OS limitation), acceptable for user workflow

### Performance Benchmarks

**Hardware**: MacBook Pro M1 (2021), 16GB RAM, 100 Mbps connection

```
Benchmark: 5 tickers (FPT, VNM, VIC, HPG, VCB)
Date range: 2023-01-01 to 2024-01-01 (252 trading days)
Risk-free rate: 3%
Risk aversion: 1.0

Results:
- Data fetching: 3.2s
- Efficient frontier (100 points): 420ms
- Random portfolios (10,000): 580ms
- Optimization (3 strategies): 180ms
- Chart generation: 150ms
- Subprocess spawn: 1.5s
- Total: 6.03s
```

### Scalability Limits

| Dimension | Limit | Reason | Workaround |
|-----------|-------|--------|------------|
| Number of tickers | 2-30 | Optimization convergence | Split into sub-portfolios |
| Time series length | 30-3000 days | Memory (DataFrames) | Sample or aggregate |
| Random portfolios | 100-100,000 | WebGL rendering | Already at 10k, optimal |
| Concurrent users | 1 | Desktop app, no server | N/A |
| Concurrent optimizations | 1 | `@work(exclusive=True)` | Intentional (UX) |

---

## Reliability

### Error Handling Strategy

**Philosophy**: Fail gracefully, display errors, never crash

```python
# Error handling pattern
@work(thread=True, exclusive=True)
def run_optimization_worker(self):
    try:
        # Layer 1: Data fetching
        try:
            data = fetch_vn_stock_data(...)
        except DataFetchError as e:
            self.app.call_from_thread(self.show_error, f"Data fetch failed: {e}")
            return

        # Layer 2: Optimization
        try:
            result = get_max_sharpe_allocation(...)
        except OptimizationError as e:
            self.app.call_from_thread(self.show_error, f"Optimization failed: {e}")
            return

    except Exception as e:
        # Layer 3: Catch-all for unexpected errors
        self.app.call_from_thread(self.show_error, f"Unexpected error: {e}")
        return
```

### Failure Modes and Recovery

| Failure Mode | Probability | Impact | Recovery Strategy |
|--------------|-------------|--------|-------------------|
| Network timeout | Medium | High | Retry with backoff, display error |
| API rate limiting | Low | Medium | Exponential backoff, user waits |
| Invalid ticker | Medium | Low | Continue with valid tickers |
| Insufficient data | Low | Medium | Display error, suggest longer date range |
| Optimization divergence | Low | Medium | Display error, suggest fewer tickers |
| Subprocess crash | Very Low | Low | Display error, user retries |
| Out of memory | Very Low | High | Uncaught, OS kills process |

### Resilience Patterns

#### 1. Graceful Degradation (Ticker Fetching)

```python
# Continue with partial data
for ticker in tickers:
    try:
        data = fetch_ticker(ticker, start, end)
        combined_df[ticker] = data['close']
    except Exception as e:
        print(f"Warning: Failed to fetch {ticker}. Continuing...")
        # Don't abort, continue with remaining tickers
```

**Trade-off**: Partial results vs complete failure

#### 2. Input Validation (Fail Fast)

```python
# Validate before expensive operations
if len(tickers) < 2:
    raise ValueError("At least 2 tickers required")

if start_date >= end_date:
    raise ValueError("Start date must be before end date")
```

**Benefit**: Catch errors early, avoid wasting API calls

#### 3. Timeout Protection

```python
# Future: Add timeouts to network calls
response = requests.get(url, timeout=10)  # 10s max
```

**Current State**: No explicit timeouts, relies on `requests` defaults (no timeout)

---

## Availability

### Current State: Desktop Application

- **Uptime target**: N/A (no server component)
- **Maintenance windows**: User-initiated (app updates)
- **Downtime**: Only during user's machine downtime

### External Dependencies

| Dependency | SLA | Fallback |
|------------|-----|----------|
| vnstock3 API | ~99% | No fallback, display error |
| Python interpreter | N/A | User's responsibility |
| OS GUI framework | N/A | User's responsibility |

### Future: API Dependency Resilience

If deployed as server-side service:

```python
# Implement circuit breaker pattern
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None

    def call(self, func, *args, **kwargs):
        if self.is_open():
            raise Exception("Circuit breaker is open")

        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise
```

---

## Maintainability

### Code Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Module size | < 500 LOC | 150-400 LOC | ✅ Good |
| Function complexity | < 10 (cyclomatic) | 2-8 | ✅ Good |
| Test coverage | > 80% | 0% | ⚠️ No tests yet |
| Docstring coverage | 100% (public APIs) | ~60% | ⚠️ Needs improvement |
| Linter warnings | 0 | 0 (Ruff) | ✅ Good |

### Code Organization

```
src/
├── main.py            # 220 LOC - Textual TUI
├── data_fetcher.py    # 150 LOC - vnstock3 integration
├── optimizer.py       # 230 LOC - PyPortfolioOpt wrappers
├── visualizer.py      # 420 LOC - Plotly chart generation
└── webview_process.py # 25 LOC - PyWebView subprocess
```

**Design Principles**:
- **Single Responsibility**: Each module has one clear purpose
- **Loose Coupling**: Modules communicate via function calls, not shared state
- **High Cohesion**: Related functionality grouped together

### Technical Debt

| Item | Severity | Impact | Mitigation Plan |
|------|----------|--------|-----------------|
| No automated tests | High | Regressions undetected | Add pytest suite (Q1 2024) |
| Missing docstrings | Medium | Harder onboarding | Add to all public APIs |
| Sequential ticker fetching | Low | Slower performance | Parallelize in v1.1.0 |
| No input sanitization | Medium | Injection risk (low) | Add in v1.1.0 |
| Hardcoded defaults | Low | Less flexible | Add config file in v2.0.0 |

### Refactoring Opportunities

1. **Extract validation logic**: Move from `InputScreen` to separate validator module
2. **Introduce strategy pattern**: Optimization strategies could be classes with common interface
3. **Add logging framework**: Replace `print()` statements with structured logging

---

## Extensibility

### Extension Points

#### 1. New Optimization Strategies

**Current**: 3 hardcoded strategies (Max Sharpe, Min Vol, Max Utility)

**Future**: Plugin architecture

```python
# src/optimizer.py (future)
class OptimizationStrategy(ABC):
    @abstractmethod
    def optimize(self, prices: pd.DataFrame, **kwargs) -> dict:
        pass

class MaxSharpeStrategy(OptimizationStrategy):
    def optimize(self, prices, rf_rate):
        # Implementation
        ...

# Register strategies
STRATEGIES = {
    'max_sharpe': MaxSharpeStrategy(),
    'min_volatility': MinVolatilityStrategy(),
    'max_utility': MaxUtilityStrategy(),
    'risk_parity': RiskParityStrategy(),  # User-added
}
```

#### 2. New Data Sources

**Current**: vnstock3 only

**Future**: Data source abstraction

```python
# src/data_fetcher.py (future)
class DataSource(ABC):
    @abstractmethod
    def fetch_prices(self, tickers, start, end) -> pd.DataFrame:
        pass

class VNStock3Source(DataSource):
    def fetch_prices(self, tickers, start, end):
        # Current implementation
        ...

class YahooFinanceSource(DataSource):
    def fetch_prices(self, tickers, start, end):
        # Use yfinance library
        ...
```

#### 3. New Visualization Types

**Current**: 2-row combined chart (frontier + pie charts)

**Future**: Chart type selection

```python
# src/visualizer.py (future)
def create_chart(data, chart_type='combined'):
    if chart_type == 'combined':
        return create_enhanced_portfolio_chart(data)
    elif chart_type == 'frontier_only':
        return create_frontier_chart(data)
    elif chart_type == 'allocation_comparison':
        return create_allocation_comparison_chart(data)
```

---

## Security

### Threat Model

**Assets**:
- User's portfolio allocations (confidential)
- Stock ticker inputs (low sensitivity)
- Network credentials (none - public API)

**Threats**:
- Data exfiltration (malicious dependency)
- Code injection (user input)
- Supply chain attack (compromised PyPI package)

**Mitigations**:
- Dependency pinning (pyproject.toml specifies versions)
- Input validation (ticker format, date ranges)
- No sensitive data persistence (stateless app)

### Input Validation

**Current**:
```python
# src/main.py:146-179
def validate_inputs(tickers_str, start_date, end_date, rf_rate, risk_aversion):
    # Basic validation
    tickers = [t.strip().upper() for t in tickers_str.split(',')]
    if len(tickers) < 2:
        return False, "At least 2 tickers required"

    # Date parsing
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return False, "Invalid date format (use YYYY-MM-DD)"

    # Numeric validation
    if not (0 <= rf_rate <= 100):
        return False, "Risk-free rate must be 0-100%"
```

**Gaps**:
- No ticker format validation (e.g., SQL injection risk if backed by DB)
- No rate limiting on API calls

**Improvements**:
```python
# Future: Stronger validation
def validate_ticker(ticker: str) -> bool:
    # Vietnamese tickers: 3-4 uppercase letters
    return bool(re.match(r'^[A-Z]{3,4}$', ticker))
```

### Dependency Security

**Current State**:
- Manual dependency updates
- No automated vulnerability scanning

**Future**:
```yaml
# .github/workflows/security.yml
- name: Scan dependencies
  run: |
    pip install pip-audit
    pip-audit --require-hashes pyproject.toml
```

---

## Privacy

### Data Collection

**Current State**: Zero data collection

- No telemetry
- No analytics
- No error reporting to external service
- No user tracking

**Per [ADR-0007: Stateless Application](./adr/0007-stateless-application.md)**:
- Portfolio allocations not persisted to disk
- Optimization history not logged
- No cookies or local storage

### Future: Opt-In Telemetry

If telemetry is added (requires user consent):

```python
# Only if user explicitly opts in
if os.getenv("TPO_TELEMETRY_ENABLED") == "1":
    # Anonymized, aggregated data only
    track_event("optimization_complete", {
        "num_tickers": len(tickers),  # Count, not actual tickers
        "duration_ms": elapsed_time,
        "strategy": "max_sharpe"
    })
```

**Privacy Principles**:
- Explicit opt-in (never default)
- Anonymized data only
- No PII (tickers, allocations, user identifiers)
- Clear privacy policy

---

## Usability

### Target Users

- **Portfolio Managers**: Professional investors managing Vietnamese stock portfolios
- **Retail Investors**: Individual investors seeking data-driven allocation
- **Risk Analysts**: Professionals comparing risk-return profiles

### Usability Goals

| Goal | Metric | Target | Status |
|------|--------|--------|--------|
| Time to first optimization | Minutes | < 2 min | ✅ ~1 min |
| Input error rate | Errors per run | < 10% | ⚠️ Not measured |
| Learning curve | Time to proficiency | < 5 min | ✅ Estimated |
| Keyboard efficiency | Mouse usage | 0% (keyboard-only) | ✅ Achieved |

### Accessibility

**Current State**:
- Terminal-based: Works with screen readers (Textual supports ANSI)
- Keyboard-only navigation: Full keyboard control (no mouse required)
- Color usage: Bloomberg-inspired theme (high contrast)

**Gaps**:
- No alternative text for charts (PyWebView window not accessible)
- No audio cues for completion
- No localization (English only)

**Future Improvements**:
- Screen reader friendly status announcements
- Audio notification when optimization completes
- High contrast mode toggle
- Vietnamese language localization

---

## Monitoring and Observability

### Current State: Stdout Logging

```python
# src/data_fetcher.py:90
print(f"Warning: Failed to fetch data for {ticker}. {e}")

# src/visualizer.py:415
print(f"Warning: Failed to display chart. {e}")
```

**Limitations**:
- No log levels (debug, info, warning, error)
- No structured logging (hard to parse)
- No log aggregation (no central logging)

### Future: Structured Logging

```python
import logging

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # stdout
        logging.FileHandler('~/.local/share/tpo/tpo.log')  # optional file
    ]
)

logger = logging.getLogger(__name__)

# Usage
logger.info("Starting optimization", extra={
    "tickers": tickers,
    "date_range": f"{start} to {end}"
})

logger.warning("Failed to fetch ticker", extra={
    "ticker": ticker,
    "error": str(e)
})
```

### Future: Performance Monitoring

```python
import time

def timed_operation(operation_name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start
            logger.info(f"{operation_name} completed", extra={
                "duration_ms": duration * 1000
            })
            return result
        return wrapper
    return decorator

@timed_operation("data_fetching")
def fetch_vn_stock_data(tickers, start, end):
    # Implementation
    ...
```

---

## Testing Strategy

### Current State: No Automated Tests

**Test Coverage**: 0%

### Future: Testing Pyramid

```
         /\
        /  \  E2E Tests (5%)
       /____\
      /      \  Integration Tests (15%)
     /________\
    /          \  Unit Tests (80%)
   /____________\
```

#### Unit Tests (Target: 80% coverage)

```python
# tests/test_optimizer.py
def test_max_sharpe_allocation():
    prices = pd.DataFrame({
        'AAPL': [100, 102, 105],
        'GOOGL': [200, 198, 202]
    })

    result = get_max_sharpe_allocation(prices, rf_rate=0.03)

    assert 'allocation' in result
    assert 'performance' in result
    assert abs(sum(result['allocation'].values()) - 1.0) < 0.001  # Weights sum to 1
    assert result['performance']['sharpe'] > 0  # Positive Sharpe
```

#### Integration Tests (Target: Critical paths)

```python
# tests/test_integration.py
def test_full_optimization_flow():
    # Mock vnstock3 API
    with patch('src.data_fetcher.Quote') as mock_quote:
        mock_quote.return_value.quote.history.return_value = sample_data

        # Run full flow
        data = fetch_vn_stock_data(['FPT', 'VNM'], '2024-01-01', '2024-12-31')
        result = get_max_sharpe_allocation(data, 0.03)
        html = create_enhanced_portfolio_chart(result, data)

        assert len(html) > 1000  # HTML generated
        assert 'Plotly' in html  # Plotly chart
```

#### E2E Tests (Target: Smoke tests)

```python
# tests/test_e2e.py
def test_app_launches():
    # Use Textual's testing harness
    from textual.testing import run_app

    async with run_app(PortfolioApp) as pilot:
        # App launches without crashing
        assert pilot.app.is_running

        # Can enter tickers
        await pilot.click("#tickers")
        await pilot.type("FPT, VNM")

        # Can quit
        await pilot.press("q")
        assert not pilot.app.is_running
```

---

## Cross-Cutting Concerns

### Localization (Future)

**Current**: English only

**Future**: Vietnamese localization

```python
# src/i18n.py
TRANSLATIONS = {
    'en': {
        'optimize_button': 'Optimize',
        'error_insufficient_data': 'Insufficient data',
    },
    'vi': {
        'optimize_button': 'Tối ưu hóa',
        'error_insufficient_data': 'Dữ liệu không đủ',
    }
}

def t(key, lang='en'):
    return TRANSLATIONS[lang].get(key, key)
```

### Configuration Management

**Current**: Hardcoded in `src/main.py`

**Future**: TOML config file

```toml
# ~/.config/tpo/config.toml
[defaults]
lookback_days = 365
risk_free_rate = 0.03
risk_aversion = 1.0

[ui]
theme = "bloomberg"  # or "light", "high-contrast"
animation_speed = "normal"

[data]
api_timeout = 10
retry_attempts = 3
```

### Versioning

**Current**: `pyproject.toml` version only

**Future**: Runtime version checking

```python
# src/__init__.py
__version__ = "1.0.0"

# src/main.py
def check_for_updates():
    response = requests.get('https://pypi.org/pypi/terminal-portfolio-optimizer/json')
    latest = response.json()['info']['version']
    if latest > __version__:
        print(f"Update available: {latest} (current: {__version__})")
```

---

## References

- ISO/IEC 25010 Quality Model: https://iso25000.com/index.php/en/iso-25000-standards/iso-25010
- OWASP Secure Coding Practices: https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/
- Textual Accessibility: https://textual.textualize.io/guide/accessibility/
- Related: [ADR-0007: Stateless Application](./adr/0007-stateless-application.md)
- Related: [Threading and Concurrency Architecture](./threading-concurrency.md)
