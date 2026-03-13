import json
import os

HISTORY_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'trade_history.json')
PERFORMANCE_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'performance.json')

def generate_analytics():
    """Reads trade_history.json, calculates stats, and saves to performance.json"""
    if not os.path.exists(HISTORY_FILE):
        return
        
    with open(HISTORY_FILE, 'r') as f:
        try:
            history = json.load(f)
        except json.JSONDecodeError:
            history = []
            
    if not history:
        with open(PERFORMANCE_FILE, 'w') as f:
            json.dump({"total_profit": 0, "total_fees": 0}, f, indent=4)
        return
        
    total_trades = len(history)
    sells = [t for t in history if t.get('action') == 'sell']
    
    winning_trades = len([t for t in sells if t.get('profit', 0) > 0])
    win_rate = (winning_trades / len(sells)) if sells else 0.0
    
    total_profit = sum(t.get('profit', 0) for t in sells)
    total_fees = sum(t.get('fee', 0) for t in history)
    
    average_trade_profit = (total_profit / len(sells)) if sells else 0.0
    
    highest_balance = 0
    max_drawdown = 0.0
    
    for t in history:
        bal = t.get('balance', 0)
        if bal > highest_balance:
            highest_balance = bal
        
        if highest_balance > 0:
            drawdown = (highest_balance - bal) / highest_balance
            if drawdown > max_drawdown:
                max_drawdown = drawdown
                
    performance = {
        "total_trades": total_trades,
        "completed_trades": len(sells),
        "win_rate": win_rate,
        "total_profit": total_profit,
        "total_fees": total_fees,
        "average_trade_profit": average_trade_profit,
        "maximum_drawdown": max_drawdown
    }
    
    with open(PERFORMANCE_FILE, 'w') as f:
        json.dump(performance, f, indent=4)
        
    print("Performance analytics updated.")
    return performance

if __name__ == "__main__":
    generate_analytics()
