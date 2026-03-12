from market import get_market_data
from strategy import check_signal
from paper_trader import execute_trade
from ai_optimizer import load_current_params, optimize_strategy
import random

def main():
    print("Starting Hybrid Crypto Paper-Trading Bot...")
    
    # Fetch price history from Binance
    print("Fetching market data...")
    # Getting much more history (e.g. 500 candles) for sufficient backtesting and RSI stability
    current_price, ohlcv_data, closing_prices = get_market_data(symbol="BTC/USDT", timeframe="5m", limit=500)
    
    if current_price is None or not closing_prices:
        print("Failed to fetch market data. Exiting.")
        return

    print(f"Current BTC/USDT price: ${current_price:.2f}")

    # Random chance to run optimizer so it doesn't happen on every single 5m cron run unnecessarily
    # E.g., ~10% chance to retrain and find new params during a run, 
    # or you can force it manually depending on logic.
    if random.random() < 0.1:
        print("Initiating periodic AI Strategy Optimization...")
        optimize_strategy(ohlcv_data)

    # Load Active Strategy
    params = load_current_params()
    if not params:
        # Use fallback standard properties if empty
        params = {"active_strategy": "ma_crossover", "ma_crossover": {"short_window": 5, "long_window": 20}}
        
    print(f"Using Strategy: {params.get('active_strategy').upper()}")

    # Run the strategy
    print("Calculating strategy signal...")
    signal = check_signal(closing_prices, params)
    
    # Execute the simulated trade
    print("Executing trade simulation...")
    execute_trade(signal, current_price)
    
    print("Bot run completed.")

if __name__ == "__main__":
    main()
