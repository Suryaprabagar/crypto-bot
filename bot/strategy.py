import numpy as np

def calculate_sma(prices, period):
    """
    Calculates the Simple Moving Average (SMA) for a given list of prices and period.
    """
    if len(prices) < period:
        return None
    return np.mean(prices[-period:])

def check_signal(closing_prices, short_window=5, long_window=20):
    """
    Implements a moving average crossover strategy.
    If short MA > long MA -> "buy"
    If short MA < long MA -> "sell"
    Otherwise -> "hold"
    """
    if not closing_prices or len(closing_prices) < long_window:
        return "hold"

    short_ma = calculate_sma(closing_prices, short_window)
    long_ma = calculate_sma(closing_prices, long_window)

    if short_ma is None or long_ma is None:
        return "hold"

    # print(f"Short MA ({short_window}): {short_ma:.2f} | Long MA ({long_window}): {long_ma:.2f}")

    if short_ma > long_ma:
        return "buy"
    elif short_ma < long_ma:
        return "sell"
    else:
        return "hold"
