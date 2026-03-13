import numpy as np
import pandas as pd

def calculate_sma(prices, period):
    """Calculates the Simple Moving Average (SMA)."""
    if len(prices) < period:
        return None
    return np.mean(prices[-period:])

def calculate_rsi(prices, period=14):
    """Calculates the Relative Strength Index (RSI)."""
    if len(prices) < period + 1:
        return None
    
    deltas = np.diff(prices)
    seed = deltas[:period]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    if down == 0:
        return 100
    rs = up / down
    rsi = np.zeros_like(prices)
    rsi[:period] = 100. - 100. / (1. + rs)

    for i in range(period, len(prices)):
        delta = deltas[i - 1]
        
        upval = delta if delta > 0 else 0.
        downval = -delta if delta < 0 else 0.

        up = (up * (period - 1) + upval) / period
        down = (down * (period - 1) + downval) / period
        
        if down == 0:
            rsi[i] = 100.
        else:
            rs = up / down
            rsi[i] = 100. - 100. / (1. + rs)
    return rsi[-1]

def strategy_ma_crossover(closing_prices, short_window, long_window):
    """Moving Average Crossover logic."""
    if len(closing_prices) < long_window:
        return "hold"
    
    short_ma = calculate_sma(closing_prices, short_window)
    long_ma = calculate_sma(closing_prices, long_window)
    
    if short_ma is None or long_ma is None:
        return "hold"
        
    if short_ma > long_ma:
        return "buy"
    elif short_ma < long_ma:
        return "sell"
    return "hold"

def strategy_rsi(closing_prices, buy_threshold, sell_threshold):
    """Relative Strength Index logic."""
    rsi = calculate_rsi(closing_prices)
    if rsi is None:
        return "hold"
        
    if rsi < buy_threshold:
        return "buy"
    elif rsi > sell_threshold:
        return "sell"
    return "hold"

def strategy_momentum(closing_prices, threshold_pct):
    """Momentum logic based on recent price change percentage."""
    if len(closing_prices) < 2:
        return "hold"
        
    current_price = closing_prices[-1]
    prev_price = closing_prices[-2]
    
    pct_change = (current_price - prev_price) / prev_price
    
    if pct_change > threshold_pct:
        return "buy"
    elif pct_change < -threshold_pct:
        return "sell"
    return "hold"

def check_signal(closing_prices, params):
    """
    Master function to check signals based on a strategy voting mechanism.
    Evaluates MA Crossover, RSI, and Momentum.
    """
    votes = []
    
    # MA Crossover
    ma_params = params.get("ma_crossover", {"short_window": 5, "long_window": 20})
    votes.append(strategy_ma_crossover(
        closing_prices, 
        ma_params.get("short_window", 5), 
        ma_params.get("long_window", 20)
    ))
    
    # RSI
    rsi_params = params.get("rsi_strategy", {"buy_threshold": 35, "sell_threshold": 65})
    votes.append(strategy_rsi(
        closing_prices,
        rsi_params.get("buy_threshold", 35),
        rsi_params.get("sell_threshold", 65)
    ))
    
    # Momentum
    mom_params = params.get("momentum_strategy", {"threshold_pct": 0.005})
    votes.append(strategy_momentum(
        closing_prices,
        mom_params.get("threshold_pct", 0.005)
    ))
    
    # Tally votes (using 2 out of 3 logic basically since there are 3 strategies)
    buy_count = votes.count("buy")
    sell_count = votes.count("sell")
    
    if buy_count >= 2:
        return "buy"
    elif sell_count >= 2:
        return "sell"
        
    return "hold"
