# Standard Vanguard ETF Universe for Moderate Risk

# Equity
US_EQUITY = ['VTI', 'VOO', 'VTV', 'VUG'] # Total, S&P500, Value, Growth
INTL_EQUITY = ['VXUS', 'VEA', 'VWO'] # Total Intl, Developed, Emerging

# Fixed Income
US_BONDS = ['BND', 'BIV', 'BLV', 'BSV', 'VGIT'] # Total, Interm, Long, Short, Treasury
INTL_BONDS = ['BNDX'] # Total Intl Bond

# Alternatives / Sector (Optional additions for diversification)
REAL_ESTATE = ['VNQ']
GOLD = ['GLD'] # Not Vanguard, but common
COMMODITIES = ['GSG'] # iShares, but good context

# Moderate Risk Core (Simple Boglehead style)
CORE_PORTFOLIO = ['VTI', 'VXUS', 'BND']

# Warnings Indicators
MACRO_INDICATORS = ['^VIX', '^TNX'] # VIX, 10Y Yield (Yahoo symbols)

def get_all_tickers():
    return list(set(
        US_EQUITY + INTL_EQUITY + 
        US_BONDS + INTL_BONDS + 
        REAL_ESTATE + GOLD + COMMODITIES +
        MACRO_INDICATORS
    ))
