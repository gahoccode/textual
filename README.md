# Terminal Portfolio Optimizer (TPO)

> **A proof-of-concept terminal-based portfolio optimizer for Vietnamese stocks, inspired by [OpenBB Terminal](https://openbb.co/) — the free, open-source Bloomberg Terminal alternative.**

TPO brings modern portfolio theory to the Vietnamese stock market through a clean, keyboard-driven terminal interface. Like OpenBB democratizes financial analysis for global markets, TPO focuses specifically on Vietnamese equities (HOSE, HNX, UPCoM) with a minimalist, terminal-first approach.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)

---

## 🎯 Why TPO?

While [OpenBB Terminal](https://github.com/OpenBB-finance/OpenBB) is an incredible open-source alternative to Bloomberg Terminal ($25,000/year), it primarily focuses on US and global markets. **TPO fills the gap for Vietnamese market participants** by providing:

- ✅ **Native Vietnamese stock market integration** via [vnstock3](https://github.com/thinh-vu/vnstock)
- ✅ **Terminal-first experience** inspired by OpenBB's philosophy
- ✅ **Professional portfolio optimization** using modern portfolio theory (PyPortfolioOpt)
- ✅ **Bloomberg-inspired UI** with dark theme and interactive visualizations
- ✅ **Zero cost, fully open source** — accessible to retail investors and students

This is a **proof-of-concept** exploring how terminal-based financial tools can serve emerging markets with specialized data sources.

---

## ✨ Features

### 🖥️ Terminal-Based Interface
- **Textual TUI**: Keyboard-driven input collection (no mouse required)
- **Bloomberg-inspired theme**: Dark terminal aesthetics with cyan/blue/orange accent colors
- **Session-based workflow**: Run multiple optimizations without restarting

### 📊 Portfolio Optimization
Compare **3 optimization strategies** side-by-side:
1. **Maximum Sharpe Ratio** — Traditional risk-adjusted return optimization
2. **Minimum Volatility** — Conservative, lowest-risk portfolio
3. **Maximum Utility** — Customizable via risk aversion parameter (λ)

### 📈 Advanced Visualizations
- **Efficient Frontier**: 100-point frontier with highlighted optimal portfolios
- **10,000 Random Portfolios**: Context visualization colored by Sharpe ratio (viridis colormap)
- **Allocation Pie Charts**: Clear weight breakdowns for each strategy
- **Interactive Plotly Charts**: Zoom, pan, hover for detailed metrics
- **PyWebView Display**: Native window rendering (no browser required)

### 🇻🇳 Vietnamese Market Focus
- **vnstock3 Integration**: Real-time data from HOSE, HNX, UPCoM exchanges
- **Ticker Validation**: Vietnamese symbol format support (FPT, VNM, VIC, etc.)
- **Graceful Error Handling**: Continues with valid tickers even if some fail

---

## 🚀 Quick Start

### Installation

**Prerequisites**: Python 3.10+ and [uv](https://docs.astral.sh/uv/) package manager

```bash
# Clone the repository
git clone https://github.com/yourusername/terminal-portfolio-optimizer.git
cd terminal-portfolio-optimizer

# Install dependencies
uv sync

# Run the application
uv run tpo
```

**Alternative (with activated virtual environment)**:
```bash
# Activate the virtual environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Run directly
tpo
```

### Example Usage

1. **Launch TPO**:
   ```bash
   uv run tpo
   ```

2. **Input Vietnamese tickers** (comma-separated):
   ```
   FPT,VNM,VIC,HPG,MSN
   ```

3. **Set date range**:
   - Start: `2024-01-01`
   - End: `2025-10-06`

4. **Configure parameters**:
   - Risk-Free Rate: `0.03` (3% annual)
   - Risk Aversion (λ): `1.0` (moderate risk)

5. **Hit "Optimize"** — The TUI will:
   - Fetch historical data from vnstock3
   - Calculate efficient frontier
   - Generate 10,000 random portfolios
   - Optimize for Max Sharpe, Min Volatility, Max Utility
   - Display interactive charts in a new window

6. **Close the chart window** to return to the TUI and run another analysis.

---

## 🧰 Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **TUI** | [Textual](https://textual.textualize.io/) | Terminal-based UI framework |
| **Data Source** | [vnstock3](https://github.com/thinh-vu/vnstock) | Vietnamese stock market data (HOSE/HNX/UPCoM) |
| **Optimization** | [PyPortfolioOpt](https://github.com/robertmartin8/PyPortfolioOpt) | Modern portfolio theory algorithms |
| **Visualization** | [Plotly](https://plotly.com/python/) | Interactive chart generation |
| **Display** | [PyWebView](https://pywebview.flowrl.com/) | Native window rendering |
| **Package Manager** | [uv](https://docs.astral.sh/uv/) | Fast, reliable dependency management |

---

## 📸 Example Output

When you run an optimization, you'll see:

**Terminal UI**:
- Clean, Bloomberg-inspired dark theme
- Input fields for tickers, dates, risk parameters
- Real-time status messages (processing, success, errors)

**Visualization Window** (1600x1000px):
- **Top Panel**: Efficient frontier plot with:
  - 10,000 random portfolios (scatter, colored by Sharpe ratio)
  - Efficient frontier curve (blue line)
  - 3 optimal portfolios (red/cyan/orange stars)
- **Bottom Panel**: Three pie charts showing allocation weights:
  - Max Sharpe (red): Typically concentrated in high-performers
  - Min Volatility (cyan): More diversified, conservative
  - Max Utility (orange): Balanced based on your risk aversion

**Performance Metrics** (in title):
```
Max Sharpe: Return=18.2%, Vol=15.3%, Sharpe=0.99
Min Vol: Return=12.1%, Vol=9.8%, Sharpe=0.93
Max Utility: Return=15.7%, Vol=12.4%, Sharpe=1.02 (λ=1.0)
```

---

## 🎨 Design Philosophy

TPO follows the **OpenBB Terminal philosophy** of democratizing financial analysis:

| Principle | TPO Implementation |
|-----------|-------------------|
| **Open Source** | MIT licensed, full source code transparency |
| **Accessibility** | Zero cost, runs on any platform with Python |
| **Terminal-First** | Keyboard-driven, fast, minimal resource usage |
| **Customizable** | Modular codebase, easy to extend/modify |
| **Professional** | Bloomberg-inspired UI, institutional-grade algorithms |
| **Community-Driven** | Open to contributions, transparent development |

---

## 🛣️ Roadmap (Potential Extensions)

This is a **proof-of-concept**. Future directions could include:

- [ ] **More Optimization Strategies**: Black-Litterman, risk parity, hierarchical clustering
- [ ] **Backtesting Module**: Historical performance simulation
- [ ] **Correlation Analysis**: Heatmaps, factor analysis
- [ ] **Export Functionality**: CSV, JSON, Excel output for allocations
- [ ] **Macro Indicators**: Integrate VN economic data (inflation, GDP, rates)
- [ ] **Sector Analysis**: Industry-level diversification metrics
- [ ] **Real-Time Data**: Live price updates during market hours
- [ ] **CLI Arguments**: Non-interactive mode for scripting
- [ ] **Plugin System**: Extensible architecture like OpenBB's

---

## 🤝 Contributing

Contributions are welcome! This is a proof-of-concept, so feel free to:

1. **Report Issues**: Found a bug? [Open an issue](https://github.com/yourusername/terminal-portfolio-optimizer/issues)
2. **Suggest Features**: Have ideas? Start a discussion
3. **Submit PRs**: Improvements to code, docs, or tests

**Development Setup**:
```bash
# Clone and install
git clone https://github.com/yourusername/terminal-portfolio-optimizer.git
cd terminal-portfolio-optimizer
uv sync

# Run from source
python3 -m src.main
```

---

## 📚 Resources

- **OpenBB Terminal**: [https://openbb.co/](https://openbb.co/) — The inspiration for this project
- **vnstock3 Docs**: [https://docs.vnstock.site/](https://docs.vnstock.site/)
- **PyPortfolioOpt Docs**: [https://pyportfolioopt.readthedocs.io/](https://pyportfolioopt.readthedocs.io/)
- **Textual Docs**: [https://textual.textualize.io/](https://textual.textualize.io/)
- **Modern Portfolio Theory**: [Investopedia Guide](https://www.investopedia.com/terms/m/modernportfoliotheory.asp)

---

## ⚠️ Disclaimer

**This is a proof-of-concept educational tool.**

- Not financial advice
- No warranty of data accuracy
- Historical performance ≠ future results
- Always conduct your own research before making investment decisions

TPO is designed for learning and experimentation with portfolio optimization concepts.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- **[OpenBB](https://openbb.co/)** — For pioneering the open-source Bloomberg alternative movement
- **[vnstock3](https://github.com/thinh-vu/vnstock)** — For Vietnamese market data access
- **[PyPortfolioOpt](https://github.com/robertmartin8/PyPortfolioOpt)** — For robust portfolio optimization algorithms
- **[Textual](https://textual.textualize.io/)** — For making beautiful terminal UIs possible

---

**Built with ❤️ for the Vietnamese investment community**

*Inspired by OpenBB Terminal's mission to democratize financial analysis*
