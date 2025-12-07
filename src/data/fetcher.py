import yfinance as yf
import pandas as pd
import datetime
from .store import DataStore

class DataFetcher:
    def __init__(self, store: DataStore):
        self.store = store

    def update_ticker(self, ticker):
        """
        Updates data for a single ticker. 
        Fetches only missing data since the last record in DB.
        """
        print(f"Updating {ticker}...")
        try:
            latest_date = self.store.get_latest_date(ticker)
        except Exception as e:
            print(f"Error accessing DB for {ticker}: {e}")
            latest_date = None

        start_date = None
        if latest_date:
            # Fetch from next day
            start_date = latest_date + datetime.timedelta(days=1)
            # If start_date is in future (today is the latest), skip
            if start_date > datetime.date.today():
                print(f"  {ticker} is up to date.")
                return
        
        # If no data exists, fetch max history
        # If data exists, fetch from start_date
        
        data = pd.DataFrame()
        try:
            if start_date:
                print(f"  Fetching from {start_date}...")
                data = yf.download(ticker, start=start_date, progress=False, auto_adjust=True)
            else:
                print(f"  Fetching max history...")
                data = yf.download(ticker, period="max", progress=False, auto_adjust=True)
            
            if not data.empty:
                # Standardize columns
                if 'Adj Close' not in data.columns and 'Close' in data.columns:
                    # yfinance auto_adjust=True makes Close = Adj Close
                    data['Adj Close'] = data['Close']
                
                # Filter out rows that might duplicate the start_date if yfinance behaves oddly
                if start_date:
                    data = data[data.index.date >= start_date]
                
                if not data.empty:
                    print(f"  Saving {len(data)} records...")
                    self.store.store_prices(ticker, data)
                    
                    # Also try to update asset details if possible
                    try:
                        info = yf.Ticker(ticker).info
                        self.store.store_asset_details(
                            ticker, 
                            name=info.get('longName', info.get('shortName')), 
                            sector=info.get('sector'),
                            asset_class=info.get('quoteType')
                        )
                    except:
                        pass # Info fetch is often flaky
                else:
                    print("  No new data found.")
        except Exception as e:
            print(f"  Failed to update {ticker}: {e}")

    def update_universe(self, tickers):
        """
        Updates a list of tickers.
        """
        for t in tickers:
            self.update_ticker(t)
