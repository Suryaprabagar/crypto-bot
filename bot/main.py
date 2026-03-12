from market import get_market_data
from strategy import check_signal
from paper_trader import execute_trade

def main():
    print("Starting Crypto Paper-Trading Bot...")
    
    # Fetch price history from Binance
    print("Fetching market data...")
    current_price, closing_prices = get_market_data(symbol="BTC/USDT", timeframe="5m", limit=50)
    
    if current_price is None or not closing_prices:
        print("Failed to fetch market data. Exiting.")
        return

    print(f"Current BTC/USDT price: ${current_price:.2f}")

    # Run the strategy
    print("Calculating strategy signal...")
    signal = check_signal(closing_prices)
    
    # Execute the simulated trade
    print("Executing trade simulation...")
    execute_trade(signal, current_price)
    
    print("Bot run completed.")

if __name__ == "__main__":
    main()
