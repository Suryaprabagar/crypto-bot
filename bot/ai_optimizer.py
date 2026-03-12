import json
import os
import itertools
from sklearn.ensemble import RandomForestRegressor
import numpy as np
from backtester import run_backtest

PARAMS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'strategy_params.json')

def load_current_params():
    if not os.path.exists(PARAMS_FILE):
        return {}
    with open(PARAMS_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_params(params):
    os.makedirs(os.path.dirname(PARAMS_FILE), exist_ok=True)
    with open(PARAMS_FILE, 'w') as f:
        json.dump(params, f, indent=4)

def generate_parameter_grid():
    """Generate combinations of parameters for backtesting."""
    grids = []
    
    # MA Crossover grid
    short_windows = [3, 5, 7, 9]
    long_windows = [15, 20, 25, 30]
    for sw, lw in itertools.product(short_windows, long_windows):
        if sw < lw:
            grids.append({
                "active_strategy": "ma_crossover",
                "ma_crossover": {"short_window": sw, "long_window": lw}
            })
            
    # RSI grid
    buy_thresholds = [25, 30, 35]
    sell_thresholds = [65, 70, 75]
    for bt, st in itertools.product(buy_thresholds, sell_thresholds):
        grids.append({
            "active_strategy": "rsi_strategy",
            "rsi_strategy": {"buy_threshold": bt, "sell_threshold": st}
        })
        
    # Momentum grid
    thresholds = [0.03, 0.05, 0.07]
    for th in thresholds:
        grids.append({
            "active_strategy": "momentum_strategy",
            "momentum_strategy": {"threshold_pct": th}
        })
        
    return grids

def optimize_strategy(ohlcv_data):
    """
    Uses a Random Forest to predict the best strategy score based on a grid search evaluation.
    Updates strategy_params.json with the best parameter set.
    """
    print("Starting AI Optimization...")
    grids = generate_parameter_grid()
    
    results = []
    # Collect real score targets via backtest for all grid configs
    for params in grids:
        profit, win_rate, dd, score = run_backtest(ohlcv_data, params)
        
        # Flatten parameters for ML features
        features = []
        if params['active_strategy'] == 'ma_crossover':
            features = [1, 0, 0, params['ma_crossover']['short_window'], params['ma_crossover']['long_window'], 0, 0, 0]
        elif params['active_strategy'] == 'rsi_strategy':
            features = [0, 1, 0, 0, 0, params['rsi_strategy']['buy_threshold'], params['rsi_strategy']['sell_threshold'], 0]
        else: # momentum
            features = [0, 0, 1, 0, 0, 0, 0, params['momentum_strategy']['threshold_pct']]
            
        results.append((features, score, params))

    # Prepare ML dataset
    X = np.array([r[0] for r in results])
    y = np.array([r[1] for r in results])
    
    if len(X) == 0:
        print("No valid grid combinations found.")
        return
        
    # Train the AI Model
    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(X, y)
    
    # In a fully genetic/evolutionary setup, we'd predict on *unseen* parameter continuous spaces.
    # For this implementation, we evaluate our grid using the trained model 
    # and pick the one with the highest predicted score.
    predictions = model.predict(X)
    
    best_index = np.argmax(predictions)
    best_params = results[best_index][2]
    best_expected_score = predictions[best_index]
    
    print(f"Optimization complete. Best strategy: {best_params['active_strategy']}")
    print(f"Expected Score: {best_expected_score:.2f}")
    
    # Save the best parameters
    current_state = load_current_params()
    # Merge best params in (this ensures we keep unused strategy keys around for structure)
    current_state["active_strategy"] = best_params["active_strategy"]
    
    key = best_params["active_strategy"]
    current_state[key] = best_params[key]
    
    save_params(current_state)
    print("Updated strategy parameters.")
    return best_params

