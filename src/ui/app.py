import streamlit as st
import pandas as pd
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.data.store import DataStore
from src.engine import universe
from src.risk.signals import RiskManager

st.set_page_config(page_title="Portfolio Manager", layout="wide")

st.title("Vanguard Portfolio Manager")

store = DataStore()
risk_mgr = RiskManager(store)

# Sidebar
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Backtest", "Data Status"])

if page == "Dashboard":
    st.header("Market Overview")
    
    # Risk Regime
    st.subheader("Risk Regime Signals")
    signals = risk_mgr.get_market_regime()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Risk Status", "RISK ON" if signals['risk_on'] else "RISK OFF", 
                 delta=None, delta_color="normal")
    
    with col2:
        if signals['warnings']:
            for w in signals['warnings']:
                st.warning(w)
        else:
            st.success("No critical warnings detected.")

    st.divider()
    
    st.header("Asset Universe Performance (YTD)")
    tickers = universe.CORE_PORTFOLIO
    
    metrics = []
    
    for t in tickers:
        df = store.load_prices(t)
        if not df.empty:
            last_price = df.iloc[-1]['close']
            # YTD
            start_year = df[df.index.year == pd.Timestamp.now().year]
            if not start_year.empty:
                start_price = start_year.iloc[0]['close']
                ytd = (last_price / start_price) - 1
                metrics.append((t, last_price, ytd))
    
    # Display in columns
    # Fetch Asset Names
    asset_names = store.get_all_asset_names()
    
    cols = st.columns(len(metrics) if metrics else 1)
    for i, (t, p, y) in enumerate(metrics):
        with cols[i]:
            name = asset_names.get(t, "Unknown Asset")
            st.metric(t, f"${p:.2f}", f"{y:.2%}", help=name)

elif page == "Backtest":
    st.header("Strategy Simulator")
    
    from src.engine.backtest import Backtester
    bt = Backtester(store, risk_mgr)
    
    col1, col2 = st.columns(2)
    
    # Load Preferences
    import json
    default_start = pd.to_datetime("2020-01-01")
    default_end = pd.to_datetime("today")
    default_cap = 10000
    default_assets = universe.CORE_PORTFOLIO
    
    saved_start = store.get_preference("start_date")
    if saved_start: default_start = pd.to_datetime(saved_start)
    
    saved_end = store.get_preference("end_date")
    if saved_end: default_end = pd.to_datetime(saved_end)
    
    saved_cap = store.get_preference("initial_cap")
    if saved_cap: default_cap = int(float(saved_cap))
    
    saved_assets = store.get_preference("assets")
    if saved_assets:
        try:
            default_assets = json.loads(saved_assets)
            # Ensure loaded assets are still in universe
            all_assets = set(universe.get_all_tickers())
            default_assets = [a for a in default_assets if a in all_assets]
        except:
            pass

    with col1:
        start_date = st.date_input("Start Date", default_start)
        initial_cap = st.number_input("Initial Capital", value=default_cap)
    with col2:
        end_date = st.date_input("End Date", default_end)
        method = st.selectbox("Optimization Method", ["max_sharpe", "min_volatility", "risk_parity"])
        
    portfolio_selection = st.multiselect("Select Assets", universe.get_all_tickers(), default=default_assets)
    
    if st.button("Run Backtest"):
        # Save Preferences
        store.set_preference("start_date", str(start_date))
        store.set_preference("end_date", str(end_date))
        store.set_preference("initial_cap", str(initial_cap))
        store.set_preference("assets", json.dumps(portfolio_selection))
        
        with st.spinner("Simulating..."):
            curve, metrics, weights = bt.run_backtest(portfolio_selection, start_date, end_date, initial_cap, strategy=method)
            
            if curve is not None:
                # Allocation Over Time
                st.subheader("Portfolio Allocation Over Time")
                
                # Fetch Names
                asset_names = store.get_all_asset_names()
                
                # Stacked Bar Chart
                # Stacked Bar Chart
                import plotly.express as px
                # Transform for Plotly
                # Resample to monthly to show only rebalance points
                try:
                    w_monthly = weights.resample('ME').last()
                except ValueError: # Fallback for older pandas
                    w_monthly = weights.resample('M').last()
                
                w_monthly.index.name = 'Date'
                w_reset = w_monthly.reset_index().melt(id_vars='Date', var_name='Asset', value_name='Weight')
                
                # Add Name column
                w_reset['Name'] = w_reset['Asset'].map(lambda x: asset_names.get(x, x))
                
                fig_alloc = px.bar(w_reset, x='Date', y='Weight', color='Asset', 
                                   title="Portfolio Allocation Over Time",
                                   hover_data=['Name'])
                
                # Use new width parameter
                try:
                     st.plotly_chart(fig_alloc, width="stretch")
                except:
                     st.plotly_chart(fig_alloc, use_container_width=True)
                
                with st.expander("See Allocation Data"):
                    try:
                        st.dataframe(weights.resample('ME').last())
                    except ValueError:
                        st.dataframe(weights.resample('M').last())
                
                st.divider()

                st.subheader("Performance Metrics")
                m_cols = st.columns(5)
                m_cols[0].metric("Total Return", f"{metrics['Total Return']:.2%}")
                m_cols[1].metric("CAGR", f"{metrics['CAGR']:.2%}")
                m_cols[2].metric("Sharpe Ratio", f"{metrics['Sharpe']:.2f}")
                m_cols[3].metric("Volatility", f"{metrics['Vol']:.2%}")
                m_cols[4].metric("Max Drawdown", f"{metrics['Max Drawdown']:.2%}")
                
                import plotly.express as px
                fig = px.line(curve, title="Portfolio Value", labels={'value': 'Value ($)', 'index': 'Date'})
                # Auto scale Y axis
                fig.update_layout(yaxis=dict(autorange=True, fixedrange=False))
                
                try:
                     st.plotly_chart(fig, width="stretch")
                except:
                     st.plotly_chart(fig, use_container_width=True)
            else:
                st.error(metrics) # Error message

elif page == "Data Status":
    st.header("Database Status")
    
    tickers = universe.get_all_tickers()
    status_data = []
    
    for t in tickers:
        last = store.get_latest_date(t)
        status_data.append({"Ticker": t, "Last Update": last})
        
    st.dataframe(pd.DataFrame(status_data))
    
    if st.button("Force Update Now"):
        with st.spinner("Updating..."):
            from src.data.fetcher import DataFetcher
            f = DataFetcher(store)
            f.update_universe(tickers)
        st.success("Update Complete!")
        st.experimental_rerun()
