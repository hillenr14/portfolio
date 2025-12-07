from .store import DataStore
from .fetcher import DataFetcher
from ..engine import universe

def main():
    print("Starting Daily Update...")
    store = DataStore()
    fetcher = DataFetcher(store)
    
    tickers = universe.get_all_tickers()
    fetcher.update_universe(tickers)
    print("Update Complete.")

if __name__ == "__main__":
    main()
