import pandas as pd
import numpy as np

class RiskManager:
    def __init__(self, data_store):
        self.store = data_store
        
    def get_market_regime(self):
        """
        Determines if we are in 'Risk On' or 'Risk Off'
        Returns a dict with signals.
        """
        # Fetch Indicators
        vix_df = self.store.load_prices('^VIX')
        # tnx_df = self.store.load_prices('^TNX') # 10 Year Yield
        
        signals = {
            'risk_on': True,
            'warnings': []
        }
        
        if not vix_df.empty:
            current_vix = vix_df.iloc[-1]['close']
            if current_vix > 30:
                signals['risk_on'] = False
                signals['warnings'].append(f"High Volatility (VIX={current_vix:.2f})")
            elif current_vix > 20:
                signals['warnings'].append(f"Elevated Volatility (VIX={current_vix:.2f})")
                
        # Simple MA Cross on SPY (using VOO as proxy if SPY not in universe, but we have VOO)
        voo_df = self.store.load_prices('VOO')
        if not voo_df.empty:
            current_price = voo_df.iloc[-1]['close']
            sma200 = voo_df['close'].rolling(200).mean().iloc[-1]
            if current_price < sma200:
                signals['risk_on'] = False
                signals['warnings'].append("Market in Downtrend (Price < SMA200)")
                
        return signals

    def adjust_weights(self, weights, signals):
        """
        Adjusts portfolio weights based on risk signals.
        If Risk Off, shift equity to bonds/cash.
        This is a heuristic rule-based approach.
        """
        if signals['risk_on']:
            return weights
        
        # Risk Off Logic: Reduce Equity, Increase Bonds/Cash
        print("Risk Off Signal Detected! Adjusting weights...")
        
        # Identify Equity and Bond tickers from Universe (hardcoded for now or fetch from DB asset class)
        # Using a simple heuristic: VTI, VOO, VUG, VTV, VXUS, VWO, VEA are Equity
        # BND, BIV, BLV, BSV, BNDX, VGIT are Bonds
        
        equity_tickers = [t for t in weights.index if t in ['VTI', 'VOO', 'VUG', 'VTV', 'VXUS', 'VWO', 'VEA', 'VNQ', 'GLD', 'GSG']]
        bond_tickers = [t for t in weights.index if t in ['BND', 'BIV', 'BLV', 'BSV', 'BNDX', 'VGIT']]
        
        if not bond_tickers:
            # If no bonds in portfolio, maybe cash? 
            # For now, just return weights but maybe we should warn.
            return weights
        
        # Reduce Equity by 50%, Reallocate to Bonds
        total_equity = weights[equity_tickers].sum()
        if total_equity > 0:
            reduction = total_equity * 0.5
            # Reduce each equity proportionally
            weights[equity_tickers] *= 0.5
            
            # Add to bonds proportionally
            total_bonds = weights[bond_tickers].sum()
            if total_bonds > 0:
                weights[bond_tickers] += (reduction * (weights[bond_tickers] / total_bonds))
            else:
                # Distribute equally if starting from 0 (unlikely in opt but possible)
                weights[bond_tickers] += (reduction / len(bond_tickers))
                
        return weights
