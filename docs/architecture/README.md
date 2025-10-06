# Architecture Documentation

Terminal Portfolio Optimizer (TPO) - Comprehensive Architecture Documentation

## Documentation Index

### Core Architecture
- [C4 Model Diagrams](./c4-model.md) - System context, containers, and components
- [Data Flow Architecture](./data-flow.md) - End-to-end data processing pipeline
- [Threading & Concurrency](./threading-concurrency.md) - Multi-threading and multi-processing architecture
- [Architecture Decision Records](./adr/) - Historical architectural decisions

### Technical Documentation
- [Deployment Architecture](./deployment.md) - Infrastructure and deployment patterns
- [Security Architecture](./security.md) - Authentication, data access, and threat model
- [Quality Attributes](./quality-attributes.md) - Performance, reliability, and scalability

### Maintenance
- [Documentation Maintenance](./maintenance.md) - Keeping architecture docs up-to-date

## Quick Reference

### System Overview
Terminal Portfolio Optimizer is a Python-based TUI application that combines:
- **Textual** for terminal user interface
- **vnstock3** for Vietnamese stock market data
- **PyPortfolioOpt** for modern portfolio theory optimization
- **Plotly** for interactive visualizations
- **PyWebView** for native chart display

### Key Architectural Patterns
- **Multiprocessing Architecture**: Separate processes for TUI and visualization
- **Worker Thread Pattern**: Non-blocking I/O operations
- **Thread-Safe UI Updates**: Event loop coordination
- **Domain-Driven Design**: Clear separation of concerns

### Critical Constraints
- PyWebView requires main thread (macOS Cocoa requirement)
- Textual requires main thread for event loop
- Solution: Run PyWebView in separate process via subprocess

### Technology Stack
```
Python 3.10+
├── UI Layer: Textual 0.47.0+
├── Data Layer: vnstock3 0.1.5+, pandas 2.1.0+
├── Optimization: PyPortfolioOpt 1.5.5+, numpy 1.24.0+
└── Visualization: Plotly 5.18.0+, PyWebView 4.4.1+
```

## Architecture Principles

1. **Separation of Concerns**: Each module has a single, well-defined responsibility
2. **Thread Safety**: All cross-thread communication is explicit and safe
3. **Process Isolation**: UI and visualization run in separate processes
4. **Fail Gracefully**: Errors are caught and displayed without crashing
5. **User-Centric**: Non-blocking operations keep UI responsive
