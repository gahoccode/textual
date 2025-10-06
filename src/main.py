"""Main Textual TUI application for Terminal Portfolio Optimizer."""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Input, Button, Static, Label
from textual.screen import Screen
from textual import on

from src.data_fetcher import fetch_vn_stock_data, DataFetchError
from src.optimizer import (
    calculate_efficient_frontier,
    get_max_sharpe_allocation,
    get_min_volatility_allocation,
    get_max_utility_allocation,
    generate_random_portfolios,
    get_portfolio_performance,
    OptimizationError,
    expected_returns,
    risk_models
)
from src.visualizer import create_enhanced_portfolio_chart, display_charts


class InputScreen(Screen):
    """Screen for collecting user inputs."""

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()

        with Container(id="input-container"):
            yield Static("Terminal Portfolio Optimizer", id="title")
            yield Static("Vietnamese Stock Market Analysis", id="subtitle")
            yield Static("")

            yield Label("Tickers (comma-separated, e.g., FPT,VNM,VIC):")
            yield Input(
                placeholder="FPT,VNM,VIC",
                id="tickers-input"
            )

            yield Label("Start Date (YYYY-MM-DD):")
            default_start = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
            yield Input(
                placeholder=default_start,
                value=default_start,
                id="start-date-input"
            )

            yield Label("End Date (YYYY-MM-DD):")
            default_end = datetime.now().strftime("%Y-%m-%d")
            yield Input(
                placeholder=default_end,
                value=default_end,
                id="end-date-input"
            )

            yield Label("Risk-Free Rate (annual, e.g., 0.03 for 3%):")
            yield Input(
                placeholder="0.03",
                value="0.03",
                id="risk-free-rate-input"
            )

            yield Label("Risk Aversion (λ, e.g., 1.0 for moderate risk):")
            yield Input(
                placeholder="1.0",
                value="1.0",
                id="risk-aversion-input"
            )

            yield Static("", id="error-message")
            yield Static("", id="success-message")

            with Horizontal(id="button-container"):
                yield Button("Optimize", variant="primary", id="optimize-btn")
                yield Button("Exit", variant="error", id="exit-btn")

        yield Footer()

    @on(Button.Pressed, "#optimize-btn")
    def on_optimize(self) -> None:
        """Handle optimize button press."""
        # Clear previous messages
        self.query_one("#error-message", Static).update("")
        self.query_one("#success-message", Static).update("")

        # Get inputs
        tickers_input = self.query_one("#tickers-input", Input).value.strip()
        start_date = self.query_one("#start-date-input", Input).value.strip()
        end_date = self.query_one("#end-date-input", Input).value.strip()
        risk_free_input = self.query_one("#risk-free-rate-input", Input).value.strip()
        risk_aversion_input = self.query_one("#risk-aversion-input", Input).value.strip()

        # Validate inputs
        if not tickers_input:
            self.query_one("#error-message", Static).update("Error: Please enter at least one ticker")
            return

        if not start_date or not end_date:
            self.query_one("#error-message", Static).update("Error: Please enter both start and end dates")
            return

        try:
            risk_free_rate = float(risk_free_input) if risk_free_input else 0.03
        except ValueError:
            self.query_one("#error-message", Static).update("Error: Invalid risk-free rate. Use decimal format (e.g., 0.03)")
            return

        try:
            risk_aversion = float(risk_aversion_input) if risk_aversion_input else 1.0
        except ValueError:
            self.query_one("#error-message", Static).update("Error: Invalid risk aversion. Use decimal format (e.g., 1.0)")
            return

        # Parse tickers
        tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

        if not tickers:
            self.query_one("#error-message", Static).update("Error: No valid tickers found")
            return

        # Show processing message
        self.query_one("#success-message", Static).update("Processing... Please wait.")

        # Run optimization
        try:
            # Fetch data
            prices = fetch_vn_stock_data(tickers, start_date, end_date)

            # Calculate expected returns and covariance (needed for random portfolios)
            mu = expected_returns.mean_historical_return(prices)
            S = risk_models.sample_cov(prices)

            # Calculate efficient frontier
            ef_returns, ef_volatilities, _ = calculate_efficient_frontier(
                prices, risk_free_rate
            )

            # Get max Sharpe portfolio
            max_sharpe_weights = get_max_sharpe_allocation(prices, risk_free_rate)
            max_sharpe_metrics = get_portfolio_performance(prices, max_sharpe_weights, risk_free_rate)
            max_sharpe_data = {
                'weights': max_sharpe_weights,
                'return': max_sharpe_metrics[0],
                'volatility': max_sharpe_metrics[1],
                'sharpe': max_sharpe_metrics[2]
            }

            # Get min volatility portfolio
            min_vol_weights = get_min_volatility_allocation(prices, risk_free_rate)
            min_vol_metrics = get_portfolio_performance(prices, min_vol_weights, risk_free_rate)
            min_vol_data = {
                'weights': min_vol_weights,
                'return': min_vol_metrics[0],
                'volatility': min_vol_metrics[1],
                'sharpe': min_vol_metrics[2]
            }

            # Get max utility portfolio
            max_utility_weights = get_max_utility_allocation(prices, risk_aversion, risk_free_rate)
            max_utility_metrics = get_portfolio_performance(prices, max_utility_weights, risk_free_rate)
            max_utility_data = {
                'weights': max_utility_weights,
                'return': max_utility_metrics[0],
                'volatility': max_utility_metrics[1],
                'sharpe': max_utility_metrics[2]
            }

            # Generate random portfolios
            random_portfolios = generate_random_portfolios(mu, S, n_samples=10000)

            # Create enhanced visualization
            html_content = create_enhanced_portfolio_chart(
                ef_returns, ef_volatilities,
                max_sharpe_data, min_vol_data, max_utility_data,
                random_portfolios,
                risk_aversion
            )

            # Update success message
            self.query_one("#success-message", Static).update(
                "Optimization complete! Opening visualization..."
            )

            # Display charts (this will block until window is closed)
            display_charts(html_content)

            # Clear success message after window closes
            self.query_one("#success-message", Static).update(
                "Visualization closed. You can run another optimization or exit."
            )

        except DataFetchError as e:
            self.query_one("#error-message", Static).update(f"Data Error: {str(e)}")
        except OptimizationError as e:
            self.query_one("#error-message", Static).update(f"Optimization Error: {str(e)}")
        except Exception as e:
            self.query_one("#error-message", Static).update(f"Unexpected Error: {str(e)}")

    @on(Button.Pressed, "#exit-btn")
    def on_exit(self) -> None:
        """Handle exit button press."""
        self.app.exit()


class PortfolioApp(App):
    """Main Textual application."""

    TITLE = "Terminal Portfolio Optimizer"
    CSS_PATH = Path(__file__).parent / "theme.tcss"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+c", "quit", "Quit"),
    ]

    def on_mount(self) -> None:
        """Mount the input screen."""
        self.push_screen(InputScreen())

    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()


def main() -> None:
    """Main entry point."""
    app = PortfolioApp()
    app.run()


if __name__ == "__main__":
    main()
