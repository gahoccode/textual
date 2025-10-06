
📝 Product Requirements Document (PRD)

Product Name: Terminal Portfolio Optimizer (TPO)
Version: 1.0
Author: [Your Name]
Date: October 6, 2025

⸻

1. 🧭 Overview

Terminal Portfolio Optimizer (TPO) is a text-based terminal application that enables users to run portfolio optimization for Vietnamese stocks using maximum Sharpe ratio allocation.
It features a Textual Python TUI for input, PyPortfolioOpt for optimization, Plotly for charting, and PyWebView for displaying the results—all while keeping the interface lightweight and terminal-focused.
Historical price data is fetched from vnstock3, tailored to the Vietnamese market.

⸻

2. 🎯 Goals & Objectives
	•	✅ Provide a keyboard-driven TUI to collect ticker symbols and date ranges.
	•	✅ Run portfolio optimization using vnstock3 price data and PyPortfolioOpt.
	•	✅ Display Efficient Frontier and Max Sharpe Allocation charts in an interactive PyWebView window.
	•	✅ Allow iterative analysis runs within a single session without restarting.

⸻

3. 🧰 Tech Stack

Component	Technology	Purpose
TUI	Textual	Terminal-based UI for inputs and navigation
Data Source	vnstock3	Fetch historical stock price data for Vietnamese tickers
Optimization Engine	PyPortfolioOpt	Compute expected returns, covariance, and max Sharpe allocation
Visualization	Plotly	Generate interactive charts (efficient frontier & pie chart)
Display Layer	PyWebView	Render Plotly charts in a separate lightweight webview window


⸻

4. 👤 User Stories

4.1 Retail Investor / Portfolio Analyst (Vietnam Market)
	•	As a user, I want to input Vietnamese stock tickers and a date range so I can analyze historical performance.
	•	As a user, I want to see the efficient frontier for my selected stocks.
	•	As a user, I want to view the max Sharpe allocation visually (pie chart) and in tabular format.
	•	As a user, I want the process to happen inside the terminal, with rich charts opening in a separate minimal window.
	•	As a user, I want clear error handling for invalid tickers or date ranges.

⸻

5. 🖥️ Core Features

Feature	Description
TUI Input Interface	Textual-based UI prompts user for:– Tickers (comma-separated, e.g. FPT, VNM, VIC)– Start date– End date– Optional risk-free rate
Data Fetching (vnstock3)	Retrieve daily historical prices from vnstock3 for all tickers between the specified dates. Validate data availability and handle missing tickers gracefully.
Portfolio Optimization	Use PyPortfolioOpt to:– Calculate expected returns and covariance matrix– Generate efficient frontier– Compute max Sharpe weights
Visualization	Generate two Plotly figures:– Efficient Frontier (highlighting the max Sharpe portfolio)– Pie Chart of max Sharpe portfolio weights
Display	Use PyWebView to render both Plotly charts in a single webview window. Layout can be stacked vertically or with tabs.
Session Handling	After closing the chart window, users return to the terminal menu to either run another optimization or exit.


⸻

6. 🧭 User Flow

+---------------------------+
| Launch Terminal App       |
+------------+--------------+
             |
             v
+---------------------------+
| Textual TUI Input         |
| - Tickers (VN)           |
| - Start Date             |
| - End Date               |
| - (Optional Risk-free)   |
+------------+--------------+
             |
             v
+---------------------------+
| vnstock3 Data Fetch       |
| - Validate tickers       |
| - Retrieve price history |
+------------+--------------+
             |
             v
+---------------------------+
| PyPortfolioOpt Engine     |
| - Expected returns       |
| - Covariance matrix      |
| - Efficient frontier     |
| - Max Sharpe weights     |
+------------+--------------+
             |
             v
+---------------------------+
| Plotly Visualization      |
| - Efficient Frontier     |
| - Pie Chart             |
+------------+--------------+
             |
             v
+---------------------------+
| PyWebView Window          |
| - Displays both charts   |
+------------+--------------+
             |
             v
+---------------------------+
| Return to TUI Menu        |
| - Run again / Exit       |
+---------------------------+


⸻

7. 🧠 Non-Functional Requirements
	•	Performance: Handle up to ~30 tickers with responsive performance (<5 seconds ideally).
	•	VN Market Focus: vnstock3 is the primary and only data source; ticker validation must match HOSE/HNX/UPCoM conventions.
	•	Portability: Cross-platform (macOS, Windows, Linux).
	•	Terminal Experience: All inputs and errors are handled textually.
	•	Resilience: Handle network failures or unavailable data gracefully.

⸻

8. 🧪 Acceptance Criteria
	•	✅ User can launch the app and input valid VN tickers + date range.
	•	✅ vnstock3 fetches data successfully and missing tickers trigger warnings, not crashes.
	•	✅ Optimization runs and charts are generated without manual steps.
	•	✅ PyWebView window pops up automatically with both charts.
	•	✅ After closing the webview, the user can run another scenario without restarting the app.
	•	✅ Invalid inputs produce clear textual error messages.

⸻

9. 🛠️ MVP Scope
	•	Textual-based input for tickers & dates
	•	Data fetching with vnstock3
	•	Portfolio optimization (max Sharpe) with PyPortfolioOpt
	•	Plotly visualization (efficient frontier & pie chart)
	•	PyWebView display of charts
	•	Session loop for multiple runs
  

⸻

