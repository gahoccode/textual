# Deployment Architecture

Deployment strategies, infrastructure requirements, and distribution methods for Terminal Portfolio Optimizer.

## Deployment Overview

Terminal Portfolio Optimizer is a **desktop terminal application** designed for:
- **Local execution**: Runs on user's machine, not a server
- **Interactive use**: Requires terminal and GUI for PyWebView
- **Single-user**: No multi-tenancy or concurrent users
- **Ad-hoc analysis**: Not a long-running service

## Deployment Models

### 1. Local Development Install (Current Primary)

**Target Audience**: Developers, power users

**Installation Method**: `uv` package manager

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/terminal-portfolio-optimizer.git
cd terminal-portfolio-optimizer

# Install with uv (handles virtual environment automatically)
uv sync

# Run application
uv run tpo
```

**Advantages**:
- Full source code access
- Easy customization
- Fast iteration for development
- No distribution overhead

**Disadvantages**:
- Requires Python 3.10+ installed
- User must manage dependencies
- Not suitable for non-technical users

---

### 2. PyPI Package Distribution (Future)

**Target Audience**: Python developers, data analysts

**Installation Method**: `pip` or `uv`

```bash
# Install from PyPI (hypothetical)
pip install terminal-portfolio-optimizer

# Run
tpo
```

**Configuration**: `pyproject.toml` already configured for packaging

```toml
[project]
name = "terminal-portfolio-optimizer"
version = "1.0.0"
dependencies = [
    "textual>=0.47.0",
    "vnstock3>=0.1.5",
    # ...
]

[project.scripts]
tpo = "src.main:main"
```

**Publishing Steps**:
```bash
# Build distribution
python -m build

# Publish to PyPI
python -m twine upload dist/*
```

**Advantages**:
- Standard Python distribution
- Easy version management
- Automatic dependency resolution
- Works with `pipx` for isolated installs

**Disadvantages**:
- Still requires Python runtime
- PyWebView native dependencies (GTK/Qt on Linux, WebView2 on Windows)

---

### 3. Standalone Executable (Future - PyInstaller/Nuitka)

**Target Audience**: Non-technical end users

**Build Tool**: PyInstaller or Nuitka

```bash
# PyInstaller build
pyinstaller --onefile \
    --name tpo \
    --hidden-import vnstock3 \
    --hidden-import pyportfolioopt \
    --collect-all textual \
    --collect-all plotly \
    src/main.py

# Nuitka build (better performance)
nuitka --standalone \
    --onefile \
    --include-package=textual \
    --include-package=vnstock3 \
    src/main.py
```

**Advantages**:
- No Python installation required
- Single executable file
- Platform-native distribution

**Disadvantages**:
- Large file size (~100-200MB with dependencies)
- Platform-specific builds (macOS, Linux, Windows)
- Longer build times
- Potential compatibility issues with native libs (PyWebView)

**Challenges**:
- **PyWebView native dependencies**: GTK3 on Linux, WebView2 on Windows
- **SciPy/NumPy binaries**: PyPortfolioOpt requires binary wheels
- **Textual terminal detection**: May need environment variable tuning

---

### 4. Docker Container (Future - Linux Only)

**Target Audience**: Server deployments, CI/CD, reproducible environments

**Dockerfile**:
```dockerfile
FROM python:3.11-slim

# Install system dependencies for PyWebView
RUN apt-get update && apt-get install -y \
    libgtk-3-0 \
    libwebkit2gtk-4.0-37 \
    gir1.2-webkit2-4.0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY src/ ./src/

# Install Python dependencies with binary wheels
RUN pip install --prefer-binary \
    textual>=0.47.0 \
    vnstock3>=0.1.5 \
    pyportfolioopt>=1.5.5 \
    plotly>=5.18.0 \
    pywebview>=4.4.1 \
    pandas>=2.1.0 \
    numpy>=1.24.0

# Install package
RUN pip install -e .

# Set environment variables for terminal
ENV TERM=xterm-256color
ENV PYTHONUNBUFFERED=1

# Entry point
CMD ["tpo"]
```

**Usage**:
```bash
# Build image
docker build -t terminal-portfolio-optimizer:1.0.0 .

# Run with terminal support
docker run -it \
    --env DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    terminal-portfolio-optimizer:1.0.0
```

**Advantages**:
- Reproducible environment
- Isolated dependencies
- CI/CD integration
- Multi-platform builds (linux/amd64, linux/arm64)

**Disadvantages**:
- **GUI limitation**: PyWebView requires X11 forwarding (complex)
- Larger image size (~500MB)
- Terminal I/O may be degraded
- Not suitable for end-user distribution

**Note**: Per CLAUDE.md instructions, use `--prefer-binary` flag for PyPortfolioOpt to ensure ARM64 and x86 compatibility.

---

## Infrastructure Requirements

### Compute Resources

| Component | CPU | Memory | Disk |
|-----------|-----|--------|------|
| Textual TUI | Minimal (~5% single core) | ~50MB | 0MB (no writes) |
| Data Fetching | Minimal (network-bound) | ~100MB (pandas DataFrames) | 0MB |
| Optimization | Moderate (CVXPY solver) | ~200MB (matrix operations) | 0MB |
| PyWebView | Low (rendering) | ~150MB (browser engine) | ~10MB (temp files) |
| **Total** | ~20% single core | ~500MB | ~10MB |

**Scaling**: Application is single-user, no horizontal scaling needed

### Network Requirements

- **Outbound HTTPS**: vnstock3 API calls to VCI data provider
- **No inbound ports**: Desktop application, no server component
- **Bandwidth**: Minimal (~1MB per optimization run for data fetch)
- **Latency**: 2-5 seconds acceptable for API responses

### Operating System Support

| OS | Status | Notes |
|----|--------|-------|
| macOS 11+ (Intel/ARM) | ✅ Fully Supported | Primary development platform |
| Ubuntu 20.04+ | ✅ Supported | Requires GTK3 for PyWebView |
| Debian 11+ | ✅ Supported | Requires GTK3 for PyWebView |
| Windows 10+ | ⚠️ Untested | Requires WebView2 runtime |
| Arch/Fedora | ⚠️ Should Work | User-managed dependencies |

---

## Dependency Management

### Runtime Dependencies

```toml
[project]
dependencies = [
    "textual>=0.47.0",          # TUI framework
    "vnstock3>=0.1.5",          # Vietnamese stock data
    "pyportfolioopt>=1.5.5",    # Portfolio optimization
    "plotly>=5.18.0",           # Interactive charts
    "pywebview>=4.4.1",         # Native webview
    "pandas>=2.1.0",            # Data manipulation
    "numpy>=1.24.0",            # Numerical computing
]
```

### System Dependencies (Linux)

```bash
# Ubuntu/Debian
sudo apt-get install \
    python3.10 \
    python3-pip \
    libgtk-3-0 \
    libwebkit2gtk-4.0-37 \
    gir1.2-webkit2-4.0

# Fedora
sudo dnf install \
    python3.10 \
    python3-pip \
    gtk3 \
    webkit2gtk3
```

### Transitive Dependencies (Critical)

| Package | Reason | Binary Required? |
|---------|--------|------------------|
| scipy | PyPortfolioOpt optimization | ✅ Yes (BLAS/LAPACK) |
| cvxpy | Convex optimization solver | ✅ Yes (ECOS/SCS) |
| numpy | Linear algebra | ✅ Yes (OpenBLAS) |
| pandas | Data structures | ✅ Yes (C extensions) |

**Docker Consideration**: Always use `--prefer-binary` flag to avoid compiling from source (CLAUDE.md requirement)

---

## Environment Configuration

### Required Environment Variables

```bash
# Optional: Override default terminal type
export TERM=xterm-256color

# Optional: Python buffering for debugging
export PYTHONUNBUFFERED=1

# Optional: Textual development mode
export TEXTUAL=devtools
```

### No Configuration Files

Per [ADR-0007: Stateless Application](./adr/0007-stateless-application.md), application has:
- **No config files**: All settings hardcoded or user-input
- **No persistent state**: No database, no session storage
- **No logging files**: Errors printed to stdout only

---

## Distribution Strategies

### Strategy 1: GitHub Releases (Current)

**Target**: Developers, early adopters

**Release Artifact**: Source code tarball

```bash
# User downloads and installs
curl -L https://github.com/USER/REPO/archive/refs/tags/v1.0.0.tar.gz | tar xz
cd terminal-portfolio-optimizer-1.0.0
uv sync
uv run tpo
```

**Automation**:
```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    tags:
      - 'v*'
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            README.md
            CHANGELOG.md
          generate_release_notes: true
```

---

### Strategy 2: PyPI Package (Future)

**Target**: Python developers

**Release Process**:
```bash
# 1. Update version in pyproject.toml
vim pyproject.toml  # version = "1.0.1"

# 2. Update CHANGELOG.md
vim CHANGELOG.md

# 3. Build distributions
python -m build

# 4. Upload to PyPI
python -m twine upload dist/*

# 5. Tag release
git tag v1.0.1
git push origin v1.0.1
```

**User Installation**:
```bash
pip install terminal-portfolio-optimizer
tpo
```

---

### Strategy 3: Homebrew (Future - macOS)

**Target**: macOS users

**Formula** (`homebrew-tap/Formula/terminal-portfolio-optimizer.rb`):
```ruby
class TerminalPortfolioOptimizer < Formula
  desc "Terminal-based portfolio optimizer for Vietnamese stocks"
  homepage "https://github.com/USER/REPO"
  url "https://github.com/USER/REPO/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "..."
  license "MIT"

  depends_on "python@3.11"

  def install
    virtualenv_create(libexec, "python3.11")
    system libexec/"bin/pip", "install", "-e", "."
    bin.install_symlink libexec/"bin/tpo"
  end

  test do
    assert_match "Portfolio Optimizer", shell_output("#{bin}/tpo --version")
  end
end
```

**User Installation**:
```bash
brew tap USER/REPO
brew install terminal-portfolio-optimizer
tpo
```

---

### Strategy 4: Snap Package (Future - Linux)

**Target**: Ubuntu/Debian users

**snapcraft.yaml**:
```yaml
name: terminal-portfolio-optimizer
version: '1.0.0'
summary: Portfolio optimizer for Vietnamese stocks
description: |
  Terminal-based portfolio optimizer using Modern Portfolio Theory.
  Supports Vietnamese stock market via vnstock3.

base: core22
grade: stable
confinement: strict

apps:
  tpo:
    command: bin/tpo
    plugs:
      - network
      - x11
      - home

parts:
  tpo:
    plugin: python
    source: .
    python-packages:
      - textual>=0.47.0
      - vnstock3>=0.1.5
      - pyportfolioopt>=1.5.5
      - plotly>=5.18.0
      - pywebview>=4.4.1
      - pandas>=2.1.0
      - numpy>=1.24.0
```

**User Installation**:
```bash
sudo snap install terminal-portfolio-optimizer
tpo
```

---

## Continuous Integration / Continuous Deployment

### CI Pipeline (GitHub Actions)

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
        python-version: ['3.10', '3.11', '3.12']

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Install dependencies
        run: uv sync

      - name: Run linters
        run: |
          uv run ruff check src/
          uv run mypy src/

      - name: Run tests
        run: uv run pytest tests/

      - name: Test CLI
        run: uv run tpo --help
```

### CD Pipeline (Automated Releases)

```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    tags:
      - 'v*'

jobs:
  pypi-publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Build package
        run: |
          pip install build
          python -m build

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}

  github-release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          generate_release_notes: true
          files: |
            CHANGELOG.md
            README.md
```

---

## Monitoring and Observability

### Current State: No Monitoring

Per [ADR-0007: Stateless Application](./adr/0007-stateless-application.md):
- No telemetry or analytics
- No error reporting (Sentry, etc.)
- No usage tracking
- Errors printed to stdout only

### Future Considerations

If monitoring is added (requires explicit user opt-in):

**Option 1: Crash Reporting (Sentry)**
```python
import sentry_sdk

# Only if user opts in
if os.getenv("TPO_ENABLE_TELEMETRY") == "1":
    sentry_sdk.init(dsn="...")
```

**Option 2: Usage Analytics (Mixpanel/Posthog)**
```python
# Track anonymized usage patterns
track_event("optimization_run", {
    "num_tickers": len(tickers),
    "optimization_strategy": "max_sharpe",
    "duration_seconds": elapsed_time
})
```

**Privacy Requirements**:
- Explicit opt-in (never default)
- No personal data (tickers, allocations)
- Anonymized IDs only
- Clear privacy policy

---

## Backup and Disaster Recovery

### Current State: Not Applicable

Per [ADR-0007: Stateless Application](./adr/0007-stateless-application.md):
- No persistent data to back up
- No database to restore
- Application is ephemeral
- User can re-run optimization anytime with fresh data

### Future: If Persistence Added

If configuration or results are persisted:
```bash
# Backup location (XDG Base Directory Specification)
~/.config/terminal-portfolio-optimizer/
~/.local/share/terminal-portfolio-optimizer/

# Backup strategy: Simple file copy
cp -r ~/.config/tpo ~/Dropbox/backups/
```

---

## Security Considerations

### Network Security

- **TLS/SSL**: vnstock3 uses HTTPS (verified by Python `requests`)
- **No authentication**: Public API, no credentials stored
- **No proxy support**: Currently uses system proxy settings

### Dependency Security

```bash
# Audit dependencies for vulnerabilities
uv run pip-audit

# Update vulnerable packages
uv sync --upgrade
```

### Code Signing (Future)

For standalone executables:
```bash
# macOS code signing
codesign --sign "Developer ID Application: NAME" \
    --timestamp \
    --options runtime \
    tpo.app

# macOS notarization
xcrun notarytool submit tpo.zip \
    --apple-id EMAIL \
    --password APP_SPECIFIC_PASSWORD \
    --team-id TEAM_ID
```

---

## Performance Optimization

### Deployment-Time Optimizations

1. **PyPortfolioOpt Binary Wheels**: Use `--prefer-binary` to avoid compilation (CLAUDE.md requirement)

```bash
pip install --prefer-binary pyportfolioopt
```

2. **Plotly Minification**: Plotly HTML includes large JS bundles (~3MB). Consider using CDN:

```python
# In src/visualizer.py
fig.write_html(
    include_plotlyjs='cdn',  # Use CDN instead of embedding (~3MB savings)
    config={'displayModeBar': False}  # Remove unnecessary UI
)
```

3. **Dependency Pruning**: Remove unused dependencies

```bash
# Analyze actual imports
pipdeptree -p terminal-portfolio-optimizer
```

### Runtime Optimizations

- Already using WebGL (Scattergl) for random portfolios
- Worker threads prevent UI blocking
- Subprocess isolation prevents memory leaks

---

## Rollback Strategy

### PyPI Package Rollback

```bash
# User pins to previous version
pip install terminal-portfolio-optimizer==1.0.0

# Or use version constraint
pip install "terminal-portfolio-optimizer<1.1.0"
```

### Git-Based Rollback

```bash
# Checkout previous tag
git checkout v1.0.0
uv sync
uv run tpo
```

### No Database Migrations

Per [ADR-0007: Stateless Application](./adr/0007-stateless-application.md):
- No schema migrations to roll back
- No data migration concerns
- Rollback is just code version change

---

## References

- PyPI Packaging Guide: https://packaging.python.org/
- PyInstaller Documentation: https://pyinstaller.org/
- Docker Best Practices: https://docs.docker.com/develop/dev-best-practices/
- Homebrew Formula Cookbook: https://docs.brew.sh/Formula-Cookbook
- Snap Documentation: https://snapcraft.io/docs
- Related: [ADR-0007: Stateless Application](./adr/0007-stateless-application.md)
