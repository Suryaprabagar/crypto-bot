import json
import os
from datetime import datetime

STATE_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'state.json')
HISTORY_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'trade_history.json')

def load_state():
    """Loads the bot state from state.json."""
    if not os.path.exists(STATE_FILE):
        return {"balance": 1000.0, "btc": 0.0}
    with open(STATE_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {"balance": 1000.0, "btc": 0.0}

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

def execute_trade(signal, current_price):
    """
    Executes a simulated trade based on the given signal and price.
    Returns the updated state.
    """
    state = load_state()
    history = load_history()
    
    balance = state.get("balance", 0.0)
    btc = state.get("btc", 0.0)
    
    timestamp = datetime.now().isoformat()
    action_taken = "hold"
    profit = 0.0
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Signal: {signal.upper()} | Price: ${current_price:.2f}")

    if signal == "buy" and balance > 0:
        # Buy uses 10% of available balance
        trade_amount_usdt = balance * 0.10
        btc_bought = trade_amount_usdt / current_price
        
        balance -= trade_amount_usdt
        btc += btc_bought
        action_taken = "buy"
        
        # Determine average buy price logic for profit calc on sell (simplified)
        state['last_buy_price'] = current_price
        
        print(f"Action: BOUGHT {btc_bought:.6f} BTC for ${trade_amount_usdt:.2f}")
    
    elif signal == "sell" and btc > 0:
        # Sell converts all BTC back to USDT
        usdt_gained = btc * current_price
        print(f"Action: SOLD {btc:.6f} BTC for ${usdt_gained:.2f}")
        
        # Calculate profit roughly from the exact trade that occurred
        # assuming basic FIFO from last buy price for simplicity in paper trading
        last_buy = state.get('last_buy_price', current_price)
        profit = (current_price - last_buy) * btc
        
        balance += usdt_gained
        btc = 0.0
        action_taken = "sell"
        state['last_buy_price'] = 0.0
        
    else:
        print("Action: HOLD / NO TRADE EXECUTED")

    state["balance"] = balance
    state["btc"] = btc
    
    portfolio_value = balance + (btc * current_price)
    print(f"Portfolio Update: {balance:.2f} USDT | {btc:.6f} BTC")
    print(f"Total Portfolio Value: ${portfolio_value:.2f}")
    print("-" * 50)

    save_state(state)
    
    # Store history log if action was matched
    if action_taken != "hold":
        history.append({
            "timestamp": timestamp,
            "action": action_taken,
            "price": current_price,
            "balance_usdt": balance,
            "btc_held": btc,
            "profit_usdt_realized": profit
        })
        save_history(history)
        
    return state
