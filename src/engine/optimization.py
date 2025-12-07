import pandas as pd
import numpy as np
from scipy.optimize import minimize

def get_returns(prices_df):
    """
    Calculate daily returns from prices.
    Assumes prices_df has columns as tickers.
    """
    return prices_df.pct_change().dropna()

def portfolio_performance(weights, mean_returns, cov_matrix):
    returns = np.sum(mean_returns * weights) * 252
    std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
    return returns, std

def neg_sharpe_ratio(weights, mean_returns, cov_matrix, risk_free_rate):
    p_ret, p_var = portfolio_performance(weights, mean_returns, cov_matrix)
    return -(p_ret - risk_free_rate) / p_var

def optimize_portfolio(prices, risk_free_rate=0.04, method='max_sharpe'):
    """
    Optimize portfolio weights.
    prices: DataFrame of asset prices (cols=tickers, index=date)
    """
    returns = get_returns(prices)
    mean_returns = returns.mean()
    cov_matrix = returns.cov()
    num_assets = len(mean_returns)
    args = (mean_returns, cov_matrix, risk_free_rate)
    
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0.0, 1.0) for asset in range(num_assets))
    
    initial_guess = num_assets * [1./num_assets,]
    
    if method == 'max_sharpe':
        result = minimize(neg_sharpe_ratio, initial_guess, args=args,
                          method='SLSQP', bounds=bounds, constraints=constraints)
    elif method == 'min_volatility':
        # Minimize Variance
        fun = lambda w: portfolio_performance(w, mean_returns, cov_matrix)[1]
        result = minimize(fun, initial_guess,
                          method='SLSQP', bounds=bounds, constraints=constraints)
    elif method == 'risk_parity':
        # Simple Risk Parity (Equal Risk Contribution)
        # This is a more complex implementation often solving for w s.t. w_i * (Sigma*w)_i is constant.
        # For simplicity in this demo, we use Inverse Volatility weighting.
        vols = returns.std()
        weights = 1. / vols
        weights /= weights.sum()
        
        # Clean small weights
        weights[weights < 0.001] = 0.0
        weights /= weights.sum()
        
        return pd.Series(weights, index=prices.columns)
    
    else:
        raise ValueError(f"Unknown method: {method}")
        
    weights = pd.Series(result.x, index=prices.columns)
    
    # Clean small weights
    weights[weights < 0.001] = 0.0
    weights /= weights.sum()
    
    return weights

def hierarchical_risk_parity(prices):
    """
    Placeholder for HRP. 
    Ideally implements the clustering and quasi-diagonalization steps.
    For this scope, we can rely on basic 'risk_parity' (inverse vol) or add full HRP if requested.
    Let's stick to Inverse Vol as a proxy for "risk balanced" for now to keep it robust.
    """
    # Simple Inverse Volatility for now
    returns = get_returns(prices)
    vols = returns.std()
    weights = 1. / vols
    weights /= weights.sum()
    return pd.Series(weights, index=prices.columns)
