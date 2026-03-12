import ccxt
import time

def get_market_data(symbol="BTC/USDT", timeframe="5m", limit=50):
    """
    Connects to KuCoin (more permissive for cloud runners),
    fetches the latest ticker price and the last `limit` candles.
    Returns the latest price and a list of closing prices.
    """
    # Initialize the exchange
    exchange = ccxt.kucoin({
        "enableRateLimit": True,
    })

    try:
        # Fetch the latest ticker
        ticker = exchange.fetch_ticker(symbol)
        current_price = ticker['last']

        # Fetch the historical klines (candles)
        # Structure of each ohlcv: [timestamp, open, high, low, close, volume]
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        
        # Extract the closing prices
        closing_prices = [candle[4] for candle in ohlcv]

        return current_price, ohlcv, closing_prices

    except ccxt.NetworkError as e:
        print(f"Network error fetching from Binance: {e}")
    except ccxt.ExchangeError as e:
        print(f"Exchange error fetching from Binance: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        
    return None, None
