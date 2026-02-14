import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

def get_fx_rate(from_currency, to_currency="USD"):
    if from_currency == to_currency:
        return 1.0
    
    try:
        ticker = f"{from_currency}{to_currency}=X"
        data = yf.Ticker(ticker)
        rate = data.history(period="1d")['Close'].iloc[-1]
        return round(rate, 4)
    except:
        fallback_rates = {
            'ZARUSD': 0.053,
            'EURUSD': 1.08,
            'GBPUSD': 1.27,
            'USDZAR': 18.9,
            'USDEUR': 0.93,
            'USDGBP': 0.79
        }
        key = f"{from_currency}{to_currency}"
        return fallback_rates.get(key, 1.0)

def get_fx_history(from_currency, to_currency="USD", days=30):
    try:
        ticker = f"{from_currency}{to_currency}=X"
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        return data['Close']
    except:
        return pd.Series()

def calculate_fx_exposure(cash_positions, base_currency="USD"):
    exposures = {}
    for currency, amount in cash_positions.items():
        if currency != base_currency:
            rate = get_fx_rate(currency, base_currency)
            exposure_usd = amount * rate
            impact_5pct = exposure_usd * 0.05
            exposures[currency] = {
                'amount': amount,
                'rate': rate,
                'exposure_usd': exposure_usd,
                'impact_5pct_move': impact_5pct
            }
    return exposures