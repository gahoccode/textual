# ADR-0007: Stateless Application Design

**Status**: Accepted

**Date**: 2024-01-16

**Deciders**: Development Team

## Context

Portfolio optimization applications often need to persist data:
- Historical price data for offline analysis
- Previous optimization results for comparison
- User preferences and default parameters
- Session history for auditing

Typical approaches include:
1. SQLite database for structured data
2. JSON/pickle files for serialized results
3. Configuration files for user preferences
4. Log files for session history

However, Terminal Portfolio Optimizer is designed for:
- Quick, ad-hoc portfolio analysis
- Real-time data from vnstock3 API
- Interactive exploration, not long-term storage
- Single-user desktop use

Considerations:
- Data freshness: Stock prices change daily, caching introduces staleness
- Security: No sensitive data (portfolio allocations) should be persisted
- Simplicity: Database adds complexity (migrations, backups, corruption)
- Privacy: Users may not want optimization history stored

## Decision

We will design the application as **completely stateless**:

1. **No persistent storage**: No database, no result files, no session history
2. **All data in memory**: Use pandas DataFrames and Python dicts during runtime
3. **Fetch data fresh**: Always pull latest data from vnstock3 API
4. **Input field retention**: Textual widgets naturally retain values between runs in same session
5. **Session loop only**: User can run multiple optimizations in one session, but state clears on app restart

### What is NOT persisted

- Historical price data (fetched fresh each run)
- Optimization results (displayed once, then discarded)
- Chart HTML (generated on-demand)
- Error logs (printed to stdout only)
- User preferences (defaults hardcoded in src/main.py)

### What IS persisted (implicitly by Textual)

- Input field values within a single app session (Textual widget state)
- Terminal scroll buffer (OS terminal feature, not app-managed)

## Consequences

### Positive

- **Simplicity**: No database schema, migrations, or backups
- **Security**: No sensitive portfolio data written to disk
- **Privacy**: No user activity tracking or history
- **Data freshness**: Always uses latest market data
- **No corruption**: No database files to corrupt
- **Zero cleanup**: No temp files, logs, or caches to manage
- **Portable**: App state is just the running process

### Negative

- **No offline mode**: Requires internet connection for every run
- **Repeated fetches**: Network overhead if user runs same portfolio multiple times
- **No result comparison**: Can't compare today's optimization to yesterday's
- **No audit trail**: No history of what portfolios were analyzed
- **No saved preferences**: User must re-enter parameters after app restart

### Risks

- **API rate limiting**: Frequent fetches might hit vnstock3 rate limits
  - *Mitigation*: Typical usage is 5-10 runs per session, well below limits
- **Network dependency**: No internet = app unusable
  - *Mitigation*: Accept as trade-off for data freshness
- **User frustration**: Losing parameters on app restart
  - *Mitigation*: Input fields retain values within session, users typically analyze similar portfolios

## Alternatives Considered

### Option 1: SQLite database for caching

**Approach**: Cache historical price data in SQLite with timestamps

```python
# Cache structure
CREATE TABLE price_data (
    ticker TEXT,
    date DATE,
    close REAL,
    fetched_at TIMESTAMP
);
```

**Pros**:
- Faster subsequent runs (no network fetch)
- Offline analysis possible
- Standard SQL tooling

**Cons**:
- Stale data: User doesn't know if prices are from today or last week
- Cache invalidation complexity: When to refresh?
- Database overhead: Schema migrations, corruption handling
- Storage management: Old data accumulation

**Reason for rejection**: Data freshness more important than speed for financial decisions

### Option 2: JSON results export

**Approach**: Optionally save optimization results to JSON file

```python
{
    "timestamp": "2024-01-16T10:30:00",
    "tickers": ["FPT", "VNM", "VIC"],
    "max_sharpe": {
        "allocation": {"FPT": 0.35, ...},
        "performance": {"return": 0.156, ...}
    }
}
```

**Pros**:
- User can track historical optimizations
- Results can be imported to Excel/other tools
- Simple file format

**Cons**:
- Adds file management UI (save dialog, file paths)
- Users may store outdated allocations
- More code complexity (serialization, file I/O)
- Storage location ambiguity (where to save?)

**Reason for rejection**: Out of scope for MVP, can add later if users request

### Option 3: Configuration file for defaults

**Approach**: TOML config for user preferences

```toml
# ~/.config/tpo/config.toml
[defaults]
lookback_days = 365
risk_free_rate = 0.03
risk_aversion = 1.0
```

**Pros**:
- User doesn't re-enter preferences each session
- Standard config pattern

**Cons**:
- Config file location varies by OS
- Most users only change defaults occasionally
- Adds ~100 lines of config parsing code

**Reason for rejection**: Input field retention within session is sufficient

### Option 4: In-memory caching with TTL

**Approach**: Cache fetched data in Python dict with expiration

```python
_cache = {}  # {(tickers, start, end): (data, timestamp)}

def fetch_with_cache(tickers, start, end, ttl=3600):
    key = (tuple(tickers), start, end)
    if key in _cache:
        data, ts = _cache[key]
        if time.time() - ts < ttl:
            return data
    # Fetch and cache
```

**Pros**:
- Speeds up same-session repeated runs
- No disk I/O
- Automatic expiration

**Cons**:
- Memory overhead (multiple portfolios cached)
- Still can serve stale data within TTL window
- Cache invalidation complexity (what if market hours end?)
- Optimization is already fast enough (~5s)

**Reason for rejection**: Premature optimization, current performance acceptable

## Design Principles

### 1. Data Freshness Over Speed
Financial decisions should use latest data. Caching introduces uncertainty.

### 2. Simplicity Over Features
Every persistence layer adds complexity. Justify storage before adding.

### 3. Privacy by Default
No data written to disk = no data leaks.

### 4. Ephemeral by Nature
Portfolio optimization is exploratory. Results inform decisions but aren't the artifact.

## When to Revisit This Decision

Consider adding persistence if:
1. **User request**: Multiple users ask for result export or history
2. **Performance**: vnstock3 API becomes too slow/unreliable
3. **Offline use**: Use case requires offline analysis (e.g., on-site client meetings)
4. **Collaboration**: Need to share optimization results with others
5. **Auditing**: Regulatory requirement to track portfolio analyses

## Implementation Notes

### Memory Lifecycle

```python
# Data lifecycle within single optimization run
def run_optimization_worker(self):
    # 1. Fetch data (creates DataFrame in memory)
    prices_df = fetch_vn_stock_data(tickers, start, end)

    # 2. Optimize (creates result dicts in memory)
    max_sharpe = get_max_sharpe_allocation(prices_df, rf_rate)

    # 3. Visualize (creates HTML string in memory)
    html = create_enhanced_portfolio_chart(...)

    # 4. Display (passes HTML to subprocess)
    display_charts(html)

    # 5. Cleanup (Python GC frees memory when function returns)
    # prices_df, max_sharpe, html all freed
```

### Input Persistence (Textual Widget State)

```python
# src/main.py:43-87
class InputScreen(Screen):
    def compose(self):
        # Widget values persist in Textual widget state during app lifetime
        yield Input(value="FPT, VNM, VIC", id="tickers")
        yield Input(value=default_start, id="start-date")
        # ...

    # After first optimization, widget.value retains user input
    # User can modify incrementally for next run
```

## References

- Related: [ADR-0001: Multiprocessing for PyWebView](./0001-multiprocessing-for-webview.md)
- Related: [ADR-0002: Worker Thread Pattern](./0002-worker-thread-pattern.md)
- vnstock3 API documentation: https://docs.vnstock.site/
- Implementation: `src/main.py`, `src/data_fetcher.py`
