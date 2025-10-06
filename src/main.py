"""Main Textual TUI application for Terminal Portfolio Optimizer."""

import sys
from datetime import datetime, timedelta
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Input, Button, Static, Label
from textual.screen import Screen
from textual import on

from src.data_fetcher import fetch_vn_stock_data, DataFetchError
from src.optimizer import (
    calculate_efficient_frontier,
    get_max_sharpe_allocation,
    get_portfolio_performance,
    OptimizationError
)
from src.visualizer import create_combined_chart, display_charts


class InputScreen(Screen):
    """Screen for collecting user inputs."""

    CSS = """
    InputScreen {
        align: center middle;
    }

    #input-container {
        width: 60;
        height: auto;
        background: $panel;
        border: solid $primary;
        padding: 2;
    }

    Label {
        margin: 1 0;
        color: $text;
    }

    Input {
        margin: 0 0 1 0;
    }

    #button-container {
        height: auto;
        align: center middle;
        margin: 1 0;
    }

    Button {
        margin: 0 1;
    }

    #error-message {
        color: $error;
        margin: 1 0;
        height: auto;
    }

    #success-message {
        color: $success;
        margin: 1 0;
        height: auto;
    }
    """

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

            # Calculate efficient frontier
            returns, volatilities, max_sharpe_point = calculate_efficient_frontier(
                prices, risk_free_rate
            )

            # Get max Sharpe allocation
            weights = get_max_sharpe_allocation(prices, risk_free_rate)

            # Get portfolio performance
            portfolio_metrics = get_portfolio_performance(prices, weights, risk_free_rate)

            # Create visualization
            html_content = create_combined_chart(
                returns, volatilities, max_sharpe_point, weights, portfolio_metrics
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
