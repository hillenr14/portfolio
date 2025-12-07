import pandas as pd
import numpy as np
from .optimization import optimize_portfolio
from ..risk.signals import RiskManager

class Backtester:
    def __init__(self, store, risk_manager: RiskManager = None):
        self.store = store
        self.risk_manager = risk_manager
        
    def run_backtest(self, tickers, start_date, end_date, initial_capital=10000, rebalance_freq='M', strategy='max_sharpe'):
        """
        Simulate portfolio performance.
        rebalance_freq: 'M' (Month End), 'Q' (Quarter End), 'A' (Year End), or None (Buy & Hold)
        """
        # Load Data
        price_map = {}
        for t in tickers:
            df = self.store.load_prices(t)
            if not df.empty:
                # Truncate to dates
                df = df[(df.index >= pd.Timestamp(start_date)) & (df.index <= pd.Timestamp(end_date))]
                price_map[t] = df['adj_close']
        
        # Combine into one DF
        # Drop tickers with no data
        valid_tickers = [t for t in tickers if t in price_map]
        prices = pd.DataFrame({t: price_map[t] for t in valid_tickers}).dropna()
        
        if prices.empty:
            return None, "No sufficient data for backtest", None
        
        # Rebalance Dates
        if rebalance_freq:
            # Handle deprecation if needed but Pandas 2.2+ suggests 'ME' for Month End
            freq = 'ME' if rebalance_freq == 'M' else rebalance_freq
            rebalance_dates = prices.resample(freq).last().index
        else:
            rebalance_dates = [prices.index[0]]
            
        # Simulation
        portfolio_value = []
        current_holdings = {t: 0 for t in valid_tickers} # Units held
        cash = initial_capital
        
        current_weights = None
        
        # We need to iterate day by day to capture daily value, but valid weights change only on rebalance dates.
        # Efficient approach: Calculate daily returns of the *current allocation*.
        
        # Actually, simpler loop: iterate rebalance periods.
        # But we want daily equity curve.
        
        # Let's iterate days for accurate tracking
        # To speed up, we can compute weights at rebalance dates and then forward fill?
        # No, because price changes shift weights.
        
        # Let's use a "Vectorized with Rebalance" approach:
        # Create a defined Series of target weights per day (ffilled)
        
        target_weights = pd.DataFrame(index=prices.index, columns=valid_tickers, dtype=float)
        
        print("Calculating target weights...")
        for date in rebalance_dates:
            # Avoid lookahead: ensure date is in prices index or take closest previous
            if date not in prices.index:
                # Find closest prev date
                loc = prices.index.get_indexer([date], method='pad')[0]
                if loc == -1: continue
                calc_date = prices.index[loc]
            else:
                calc_date = date
            
            # Use data UP TO calc_date (exclusive of today if we want strict, but inclusive is standard for "close")
            # For optimization we should use a lookback window, e.g. 1 year.
            lookback_start = calc_date - pd.DateOffset(years=1)
            history = prices[(prices.index >= lookback_start) & (prices.index <= calc_date)]
            
            if len(history) < 60: # Need some data
                # Default Equal Weight
                w = pd.Series(1.0/len(valid_tickers), index=valid_tickers)
            else:
                # Run Optimization
                # Check for Risk Signals at this rebalance point
                # (In a real system, we might check daily, but for this backtest we check at rebalance)
                
                try:
                    w = optimize_portfolio(history, method=strategy)
                    
                    if self.risk_manager:
                        # Fake a "historical" signal check?
                        # This is hard because signals need data at that time. 
                        # We can try to reuse risk manager logic if we implemented "historical lookup" support.
                        # For now, let's skip dynamic risk adjustment in backtest unless easy.
                        pass
                        
                except Exception as e:
                    print(f"Optimization failed on {calc_date}: {e}, using EW")
                    w = pd.Series(1.0/len(valid_tickers), index=valid_tickers)
            
            # Assign weights to the rebalance date row in target_weights
            # We assign to the *next* day? Or this day? 
            # Usually we calculate on Close, trade on Next Open. 
            # For simplicity: Trade on Close (Theoretical).
            target_weights.loc[calc_date] = w
            
        # Forward fill weights
        target_weights = target_weights.ffill()
        pd.set_option('future.no_silent_downcasting', True)
        target_weights = target_weights.infer_objects(copy=False)
        target_weights = target_weights.fillna(0) # For beginning if any
        
        # Now calculate strategy returns
        # Strategy Return = Sum(Weight_i * Asset_Return_i)
        asset_returns = prices.pct_change().dropna()
        
        # Shift weights by 1 day because weights determined at T Close apply to T+1 Return
        aligned_weights = target_weights.shift(1).dropna()
        aligned_returns = asset_returns.loc[aligned_weights.index] # Align dates
        
        portfolio_returns = (aligned_weights * aligned_returns).sum(axis=1)
        
        cumulative_return = (1 + portfolio_returns).cumprod()
        portfolio_value = cumulative_return * initial_capital
        
        # Calculate CAGR
        days = (portfolio_value.index[-1] - portfolio_value.index[0]).days
        years = days / 365.25
        total_ret = (portfolio_value.iloc[-1] / initial_capital) - 1
        cagr = ((portfolio_value.iloc[-1] / initial_capital) ** (1/years)) - 1 if years > 0 else total_ret

        metrics = {
            'Total Return': total_ret,
            'CAGR': cagr,
            'Sharpe': (portfolio_returns.mean() / portfolio_returns.std()) * (252**0.5),
            'Vol': portfolio_returns.std() * (252**0.5),
            'Max Drawdown': (portfolio_value / portfolio_value.cummax() - 1).min()
        }
        
        return portfolio_value, metrics, target_weights

