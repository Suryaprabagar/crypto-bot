import json
import os
from datetime import datetime

STATE_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'state.json')
HISTORY_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'trade_history.json')

TRADING_FEE = 0.005 # 0.5%
SLIPPAGE = 0.0005 # 0.05%

def load_state():
    """Loads the bot state from state.json."""
    if not os.path.exists(STATE_FILE):
        return {"balance": 1000.0, "btc": 0.0, "eth": 0.0, "sol": 0.0, "bnb": 0.0}
    with open(STATE_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {"balance": 1000.0, "btc": 0.0, "eth": 0.0, "sol": 0.0, "bnb": 0.0}

def save_state(state):
    """Saves the bot state to state.json."""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=4)

def load_history():
    """Loads trade history from trade_history.json"""
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_history(history):
    """Saves trade history."""
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=4)

def execute_trade(signal, current_price, symbol="BTC/USDT"):
    """
    Executes a simulated trade based on the given signal, price, and symbol.
    Returns the updated state.
    """
    state = load_state()
    history = load_history()
    
    balance = state.get("balance", 0.0)
    asset = symbol.split('/')[0].lower() # e.g., 'btc'
    
    asset_balance = state.get(asset, 0.0)
    
    timestamp = datetime.now().isoformat()
    action_taken = "hold"
    profit = 0.0
    fee_paid = 0.0
    trade_amount = 0.0
    executed_price = current_price
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {symbol} Signal: {signal.upper()} | Price: ${current_price:.2f}")

    if signal == "buy" and balance > 0:
        # Apply slippage
        executed_price = current_price * (1 + SLIPPAGE)
        
        # Buy uses 10% of available balance
        trade_amount_usdt = balance * 0.10
        fee_paid = trade_amount_usdt * TRADING_FEE
        asset_bought = (trade_amount_usdt - fee_paid) / executed_price
        
        balance -= trade_amount_usdt
        asset_balance += asset_bought
        action_taken = "buy"
        trade_amount = asset_bought
        
        state[f'last_buy_price_{asset}'] = executed_price
        
        print(f"Action: BOUGHT {asset_bought:.6f} {asset.upper()} for ${trade_amount_usdt:.2f} (Fee: ${fee_paid:.2f})")
    
    elif signal == "sell" and asset_balance > 0:
        # Apply slippage
        executed_price = current_price * (1 - SLIPPAGE)
        
        usdt_value = asset_balance * executed_price
        fee_paid = usdt_value * TRADING_FEE
        net_usdt = usdt_value - fee_paid
        
        print(f"Action: SOLD {asset_balance:.6f} {asset.upper()} for ${net_usdt:.2f} (Fee: ${fee_paid:.2f})")
        
        last_buy = state.get(f'last_buy_price_{asset}', executed_price)
        # Calculate profit based on the net received compared to the estimated total cost
        # A simple method: Profit = Net received - (Amount of asset * last buy price)
        profit = net_usdt - (asset_balance * last_buy)
        
        balance += net_usdt
        trade_amount = asset_balance
        asset_balance = 0.0
        action_taken = "sell"
        state[f'last_buy_price_{asset}'] = 0.0
        
    else:
        print(f"Action: HOLD / NO TRADE EXECUTED FOR {symbol}")

    state["balance"] = balance
    state[asset] = asset_balance
    
    portfolio_value = balance
    for coin in ['btc', 'eth', 'sol', 'bnb']:
        # This is a bit of an approximation since we don't fetch all prices here, 
        # but for the execute log it'll just use the current price for the traded coin
        if coin == asset:
            portfolio_value += (state.get(coin, 0.0) * current_price)
            
    print(f"Portfolio Update: {balance:.2f} USDT | {asset_balance:.6f} {asset.upper()}")
    print("-" * 50)

    save_state(state)
    
    # Store history log if action was matched
    if action_taken != "hold":
        history.append({
            "timestamp": timestamp,
            "pair": symbol,
            "action": action_taken,
            "price": executed_price,
            "trade_amount": trade_amount,
            "fee": fee_paid,
            "profit": profit,
            "balance": balance,
            f"{asset}_held": asset_balance
        })
        save_history(history)
        
    return state
