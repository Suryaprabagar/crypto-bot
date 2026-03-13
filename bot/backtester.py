import pandas as pd
from strategy import check_signal

TRADING_FEE = 0.005
SLIPPAGE = 0.0005

def run_backtest(ohlcv_data, params):
    """
    Simulate the strategy on historical data.
    Returns: profit, win_rate, drawdown, and a composite strategy score.
    """
    if not ohlcv_data:
        return 0, 0, 0, 0
        
    df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    balance = 1000.0
    asset_balance = 0.0
    initial_balance = balance
    
    trades = 0
    winning_trades = 0
    
    peak_balance = balance
    max_drawdown = 0.0
    
    buy_price = 0
    
    # We need to simulate stepping through time
    # To check signal at step i, we pass prices up to i
    closing_prices = df['close'].tolist()
    
    for i in range(20, len(closing_prices)): 
        # using a minimum buffer of 20 to allow MAs to calculate
        current_closes = closing_prices[:i+1]
        current_price = current_closes[-1]
        
        signal = check_signal(current_closes, params)
        
        if signal == "buy" and balance > 0:
            executed_price = current_price * (1 + SLIPPAGE)
            trade_amount_usdt = balance * 0.10
            fee = trade_amount_usdt * TRADING_FEE
            
            asset_bought = (trade_amount_usdt - fee) / executed_price
            balance -= trade_amount_usdt
            asset_balance += asset_bought
            buy_price = executed_price
            
        elif signal == "sell" and asset_balance > 0:
            executed_price = current_price * (1 - SLIPPAGE)
            usdt_value = asset_balance * executed_price
            fee = usdt_value * TRADING_FEE
            net_usdt = usdt_value - fee
            
            # Record win/loss
            if executed_price > buy_price:
                winning_trades += 1
            trades += 1
            
            balance += net_usdt
            asset_balance = 0.0
            
        # Update peak and DD
        current_portfolio_value = balance + (asset_balance * current_price)
        if current_portfolio_value > peak_balance:
            peak_balance = current_portfolio_value
            
        drawdown = (peak_balance - current_portfolio_value) / peak_balance
        if drawdown > max_drawdown:
            max_drawdown = drawdown
            
    # Final liquidation to calculate true total value at the end of backtest
    final_value = balance + (asset_balance * closing_prices[-1])
    total_profit = final_value - initial_balance
    
    win_rate = (winning_trades / trades) if trades > 0 else 0
    
    # Simple composite score prioritizing profit and penalizing drawdown
    strategy_score = total_profit * (1 + win_rate) - (max_drawdown * 100)
    
    return total_profit, win_rate, max_drawdown, strategy_score
