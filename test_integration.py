from src.data.store import DataStore
from src.engine.backtest import Backtester
from src.engine import universe
import pandas as pd

def test_backtest():
    print("Testing Backtest Engine...")
    store = DataStore()
    bt = Backtester(store)
    
    tickers = universe.CORE_PORTFOLIO
    start = "2023-01-01"
    end = "2023-06-01"
    
    try:
        curve, metrics, weights = bt.run_backtest(tickers, start, end)
        if curve is not None:
            print("Backtest Successful!")
            print(metrics)
        else:
            print("Backtest failed w/o error but no curve.")
    except Exception as e:
        print(f"Backtest Crashed: {e}")
        raise e

if __name__ == "__main__":
    test_backtest()
