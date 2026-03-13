from market import get_market_data
from strategy import check_signal
from paper_trader import execute_trade, load_state
from ai_optimizer import load_current_params, optimize_strategy
from risk_manager import check_risk_limits
from analytics import generate_analytics
import random

TRADING_PAIRS = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT"]

def main():
    print("Starting Hybrid Crypto Paper-Trading Bot...")
    
    # We load params once
    params = load_current_params()
    if not params:
        # Fallback to defaults
        params = {
            "ma_crossover": {"short_window": 5, "long_window": 20},
            "rsi_strategy": {"buy_threshold": 30, "sell_threshold": 70},
            "momentum_strategy": {"threshold_pct": 0.05}
        }
        
    state = load_state()
    latest_prices = {}
    
    # Random chance to run optimizer (e.g. 5% chance per cron run)
    if random.random() < 0.05:
        print("Initiating periodic AI Strategy Optimization on BTC/USDT...")
        _, ohlcv_data, _ = get_market_data(symbol="BTC/USDT", timeframe="5m", limit=500)
        if ohlcv_data:
            optimize_strategy(ohlcv_data)
            params = load_current_params()  # Reload after update

    for pair in TRADING_PAIRS:
        print(f"\n--- Processing {pair} ---")
        current_price, _, closing_prices = get_market_data(symbol=pair, timeframe="5m", limit=500)
        
        if current_price is None or not closing_prices:
            print(f"Failed to fetch market data for {pair}. Skipping.")
            continue

        latest_prices[pair] = current_price
        asset = pair.split('/')[0].lower()
        entry_price = state.get(f'last_buy_price_{asset}', 0.0)
        
        # 1) Risk Management
        risk_signal = check_risk_limits(current_price, entry_price)
        
        signal = "hold"
        if risk_signal == "sell":
            signal = "sell"
            print("Risk limits matched! Emitting SELL signal priority.")
        else:
            # 2) Strategy logic
            signal = check_signal(closing_prices, params)
            print(f"Strategy returned signal: {signal.upper()}")
            
        # Execute the trade if signal tells us to (buy/sell)
        execute_trade(signal, current_price, symbol=pair)
        
        # Reload state as execute_trade modifies it
        state = load_state()
        
    print("\nUpdating performance metrics...")
    stats = generate_analytics()
    
    # Final Reporting
    print("\n" + "="*50)
    print("FINAL WORKFLOW REPORT")
    print("="*50)
    
    if stats:
        print(f"Total Fees Paid (All Time): ${stats.get('total_fees', 0):.4f}")
    
    # Calculate current portfolio value
    portfolio_value = state.get('balance', 0.0)
    for pair, price in latest_prices.items():
        asset = pair.split('/')[0].lower()
        amount = state.get(asset, 0.0)
        portfolio_value += amount * price
    
    print(f"Total Portfolio Value: ${portfolio_value:.2f}")
    print("="*50)
    
    print("\nBot run completed successfully.")

if __name__ == "__main__":
    main()
