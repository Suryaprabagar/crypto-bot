def check_risk_limits(current_price, entry_price):
    """
    Checks if the current price hits the stop loss (2%) or take profit (3%).
    Returns 'sell' if limits are hit, otherwise 'hold'.
    """
    if entry_price <= 0:
        return "hold"
        
    stop_loss = entry_price * 0.98
    take_profit = entry_price * 1.03
    
    if current_price <= stop_loss:
        print(f"Risk Manager: Stop loss hit at ${current_price:.2f} (Entry: ${entry_price:.2f})")
        return "sell"
        
    if current_price >= take_profit:
        print(f"Risk Manager: Take profit hit at ${current_price:.2f} (Entry: ${entry_price:.2f})")
        return "sell"
        
    return "hold"
