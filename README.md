# Vanguard Portfolio Manager

A Python-based investment portfolio management tool designed for moderate-risk investors, focusing on Vanguard ETFs. This application provides robust backtesting, portfolio optimization, and market regime detection to help users make informed decisions.

![Dashboard Preview](https://via.placeholder.com/800x400.png?text=Dashboard+Preview+Coming+Soon)

## Features

*   **Portfolio Optimization**: Implements Modern Portfolio Theory (Mean-Variance Optimization) to find Max Sharpe or Minimum Volatility portfolios. Also supports Risk Parity (Inverse Volatility).
*   **Backtesting Engine**: Fast, vectorized simulation of trading strategies with customizable timeframes and rebalancing frequencies.
    *   Tracks **CAGR**, Total Return, Volatility, and Max Drawdown.
    *   Visualizes allocation changes over time.
    *   Accounts for transaction costs (optional config) and rebalancing drift.
*   **Risk Regime Detection**: Automated signal generation ("Risk On" / "Risk Off") based on:
    *   **VIX Levels**: Volatility index thresholds.
    *   **Technical Trends**: SMA comparisons (e.g., Price vs SMA200).
*   **Interactive Dashboard**: Built with **Streamlit** and **Plotly** for responsive, high-quality visualizations.
    *   **Analysis**: Deep dive into individual asset performance.
    *   **Persistence**: Automatically saves your backtest settings (Dates, Capital, Assets) to a local SQLite database.
*   **Data Caching**: Efficiently manages historical data using SQLite and `yfinance`, respecting API rate limits.

## Installation

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/hillenr14/portfolio.git
    cd portfolio
    ```

2.  **Create Environment**:
    We recommend using Conda to manage dependencies (especially for scientific libraries like `scipy` on Apple Silicon).
    ```bash
    conda create -n finance python=3.10
    conda activate finance
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: If you are on a Mac with M1/M2 chips and encounter errors with `scipy`, consider installing it via conda:*
    ```bash
    conda install -c conda-forge scipy numpy pandas
    ```

## Usage

### 1. Initialize/Update Data
Before running the dashboard, populate the local database with historical price data. This script fetches the latest data for the defined asset universe.
```bash
python -m src.data.update
```

### 2. Run the Dashboard
Launch the Streamlit application:
```bash
streamlit run src/ui/app.py
```
The app will open in your default browser (usually at `http://localhost:8501`).

## Project Structure

```text
portfolio/
├── main.py                  # Entry point (alternative to app.py)
├── requirements.txt         # Python dependencies
├── src/
│   ├── data/
│   │   ├── store.py         # SQLAlchemy Database Models & Interface
│   │   ├── fetcher.py       # YFinance Data Fetcher
│   │   └── update.py        # Data Update Script
│   ├── engine/
│   │   ├── backtest.py      # Vectorized Backtesting Engine
│   │   ├── optimization.py  # MVO & Risk Parity Logic
│   │   └── universe.py      # Asset Definitions (Vanguard ETFs)
│   ├── risk/
│   │   └── signals.py       # Risk Regime Detection Logic
│   └── ui/
│       └── app.py           # Streamlit Web Application
└── test_integration.py      # Backend Verification Tests
```

## Technologies

*   **Python 3.10+**
*   **Streamlit**: Frontend UI
*   **Plotly**: Interactive Charts
*   **Pandas & NumPy**: Data Manipulation
*   **SciPy**: Optimization Algorithms
*   **SQLAlchemy & SQLite**: Data Persistence
*   **yfinance**: Market Data API

## License

[MIT](LICENSE)
