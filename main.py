import sys
from utils.state import GameState

def agent(obs):
    """
    Minimal Working Agent for Kaggriculture.
    Returns: {"farmer": ["ACTION"], "hands": [], "market": [["ORDER", "ITEM", QTY]]}
    """
    state = GameState(obs)
    
    day = state.current_day
    hour = state.current_hour
    money = state.my_money
    farmer_pos = state.farmer_pos
    
    action = "PASS"
    market_orders = []
    
    # 1. Turn 0: market order BUY_SEED WHEAT 5
    if day == 0 and hour == 0:
        market_orders.append(["BUY_SEED", "WHEAT", 5])
        
    # 4. If shed has wheat > 0: market order SELL WHEAT <qty>
    wheat_in_shed = state.shed_contents.get("WHEAT", 0)
    if wheat_in_shed > 0:
        market_orders.append(["SELL", "WHEAT", wheat_in_shed])
        
    # Get current tile
    x, y = farmer_pos
    tile = state.get_tile(x, y)
    
    if tile:
        kind = tile.get("kind", "empty")
        
        # 3. If standing on a PLANT tile
        if kind in ("crop", "plant"):
            watered = tile.get("watered_today", False)
            yield_units = tile.get("yield_units", 0)
            age = tile.get("growth", 0)
            
            if not watered and tile.get("water", 1) == 0:
                action = "WATER"
            elif yield_units > 0 and age >= 2:
                action = "HARVEST"
                
        # 2. If standing on empty tile and have wheat seeds: PLANT WHEAT
        elif kind == "empty":
            if state.seed_counts.get("WHEAT", 0) > 0:
                action = "PLANT_WHEAT"
                
    # 5. Otherwise: move SOUTH then EAST to explore tiles
    if action == "PASS":
        if hour % 2 == 0:
            action = "SOUTH"
        else:
            action = "EAST"
            
    # Format return dictionary exactly as specified
    action_dict = {
        "farmer": [action],
        "hands": [],
        "market": market_orders
    }
    
    print(f"Day {day:02d} Hr {hour:02d} | Pos: {farmer_pos} | Act: {action} | Money: {money}")
    
    return action_dict

if __name__ == "__main__":
    try:
        from kaggle_environments import make
        env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=True)
        env.run([agent, "random"])
        print("Final Rewards:", env.steps[-1][0].reward, env.steps[-1][1].reward)
    except ImportError:
        print("kaggle_environments not installed, skipping test.")
