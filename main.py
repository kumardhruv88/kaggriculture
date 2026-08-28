import sys
from utils.state import GameState
from strategy.crop_manager import CropManager
from strategy.market_manager import MarketManager
from strategy.movement import next_move_toward, manhattan
from utils.constants import CROPS

AGENT_STATE = {
    "unit_task_queues": {"farmer": [], "hand_0": [], "hand_1": []},
    "day_plan": {},
    "planted_this_day": set(),
    "last_day": -1
}

def get_unit_action(unit_id, state, crop_manager, is_hand=False):
    """
    Decides the next action for a specific unit (farmer or hand).
    Falls back to PASS if an error occurs.
    """
    try:
        global AGENT_STATE
        
        # Determine position
        if unit_id == "farmer":
            pos = state.farmer_pos
        else:
            idx = int(unit_id.split("_")[1])
            hands_pos = state.obs.get("hands_pos", [])
            if idx < len(hands_pos):
                pos = hands_pos[idx]
            else:
                return "PASS"
                
        # Check task queue
        queue = AGENT_STATE["unit_task_queues"].setdefault(unit_id, [])
        if queue:
            return queue.pop(0)
            
        x, y = pos
        tile = state.get_tile(x, y)
        
        if not tile:
            return "PASS"
            
        kind = tile.get("kind", "empty")
        
        # --- REACTIVE ACTIONS ON CURRENT TILE ---
        if kind in ("crop", "plant"):
            yield_units = tile.get("yield_units", 0)
            watered = tile.get("watered_today", False)
            crop_name = tile.get("crop")
            
            is_one_time = False
            if crop_name in CROPS:
                is_one_time = (CROPS[crop_name]["yield_type"] == "one-time")
                
            growth = tile.get("growth", 0)
            max_yield_day = CROPS.get(crop_name, {}).get("max_yield_day", 0)
            
            # Harvest
            if yield_units > 0 and (not is_one_time or growth >= max_yield_day):
                return "HARVEST"
                
            # Water
            if not watered and tile.get("water", 1) == 0:
                return "WATER"
                
            # Fertilize
            fertilizer_count = state.shed_contents.get("fertilizer", 0)
            first_yield_day = CROPS.get(crop_name, {}).get("first_yield_day", 0)
            fertilized_until = tile.get("fertilized_until_day", -1)
            
            if is_one_time and fertilizer_count > 0 and (first_yield_day <= growth <= max_yield_day) and fertilized_until < state.current_day:
                return "FERTILIZE"
                
        elif kind == "weed":
            return "DIG"
            
        elif kind == "animal":
            # Animal handling logic
            if tile.get("needs_feed", False) and state.shed_contents.get("WHEAT", 0) > 0:
                return "FEED"
            if tile.get("needs_care", False):
                return "CARE"
            if tile.get("yield_units", 0) > 0:
                return "HARVEST"
            if tile.get("has_fertilizer", False):
                return "COLLECT_FERTILIZER"
                
        elif kind == "empty" and (x, y) not in AGENT_STATE["planted_this_day"]:
            # Planting
            plan = AGENT_STATE["day_plan"].get("should_plant", {})
            best_crop = None
            for crop, count in plan.items():
                if count > 0 and state.seed_counts.get(crop, 0) > 0:
                    best_crop = crop
                    break
            if best_crop:
                plan[best_crop] -= 1
                AGENT_STATE["planted_this_day"].add((x, y))
                return f"PLANT_{best_crop}"
                
        # --- TARGETING / MOVEMENT LOGIC ---
        
        # 1. Urgent Animal targets (applies to all units)
        animal_tiles = state.find_all_tiles_of_type("animal")
        urgent_animal_targets = []
        for ax, ay in animal_tiles:
            atile = state.get_tile(ax, ay)
            if atile and (atile.get("needs_feed", False) or atile.get("needs_care", False) or atile.get("yield_units", 0) > 0 or atile.get("has_fertilizer", False)):
                urgent_animal_targets.append((ax, ay))
                
        if urgent_animal_targets:
            best_target = min(urgent_animal_targets, key=lambda t: manhattan(pos, t))
            move = next_move_toward(state, pos, best_target)
            if move != "PASS": return move
            
        # 2. Specific Unit Priorities
        if unit_id == "farmer":
            targets = crop_manager.get_harvest_targets()
            if targets:
                return next_move_toward(state, pos, min(targets, key=lambda t: manhattan(pos, t)))
                
            targets = crop_manager.get_water_targets()
            if targets:
                return next_move_toward(state, pos, min(targets, key=lambda t: manhattan(pos, t)))
                
            plan = AGENT_STATE["day_plan"].get("should_plant", {})
            has_seeds = any(count > 0 and state.seed_counts.get(crop, 0) > 0 for crop, count in plan.items())
            if has_seeds:
                empty_tiles = [t for t in state.empty_tiles() if t not in AGENT_STATE["planted_this_day"]]
                if empty_tiles:
                    return next_move_toward(state, pos, min(empty_tiles, key=lambda t: manhattan(pos, t)))
                    
            targets = crop_manager.get_dig_targets()
            if targets:
                return next_move_toward(state, pos, min(targets, key=lambda t: manhattan(pos, t)))
                
        elif unit_id == "hand_0":
            targets = crop_manager.get_water_targets()
            if targets:
                return next_move_toward(state, pos, min(targets, key=lambda t: manhattan(pos, t)))
                
            targets = crop_manager.get_fertilize_targets()
            if targets:
                return next_move_toward(state, pos, min(targets, key=lambda t: manhattan(pos, t)))
                
        elif unit_id == "hand_1":
            targets = crop_manager.get_water_targets()
            if targets:
                return next_move_toward(state, pos, min(targets, key=lambda t: manhattan(pos, t)))
                
            targets = crop_manager.get_harvest_targets()
            if targets:
                return next_move_toward(state, pos, min(targets, key=lambda t: manhattan(pos, t)))
                
        return "PASS"
        
    except Exception as e:
        print(f"Error in {unit_id}: {e}")
        return "PASS"


def agent(obs):
    """
    Entry point for the Kaggriculture competition agent.
    """
    global AGENT_STATE
    state = GameState(obs)
    
    crop_manager = CropManager(state)
    market_manager = MarketManager(state)
    
    day = state.current_day
    hour = state.current_hour
    money = state.my_money
    
    market_orders = []
    
    # --- DAY PLAN (at Hour 0) ---
    if hour == 0 and day != AGENT_STATE["last_day"]:
        AGENT_STATE["last_day"] = day
        AGENT_STATE["planted_this_day"] = set()
        
        # Issue market orders
        market_orders.extend(market_manager.get_sell_orders())
        market_orders.extend(market_manager.get_buy_orders())
        
        hands_to_hire = market_manager.should_hire_hand()
        if hands_to_hire > 0:
            market_orders.append(["HIRE_HAND", hands_to_hire])
            
        if market_manager.should_buy_land():
            unlocked = state.unlocked_quadrants()
            if 1 not in unlocked:
                market_orders.append(["BUY_LAND", 1])
            elif 2 not in unlocked:
                market_orders.append(["BUY_LAND", 2])
                
        # Calculate daily crop mix
        AGENT_STATE["day_plan"]["should_plant"] = crop_manager.should_plant()
        
        # Clear queues for re-planning
        AGENT_STATE["unit_task_queues"] = {"farmer": [], "hand_0": [], "hand_1": []}

    # --- GET UNIT ACTIONS ---
    farmer_action = get_unit_action("farmer", state, crop_manager)
    
    hands_pos = obs.get("hands_pos", [])
    hands_actions = []
    for i in range(len(hands_pos)):
        hand_id = f"hand_{i}"
        action = get_unit_action(hand_id, state, crop_manager, is_hand=True)
        hands_actions.append([action])

    # --- COMPILE ACTION DICT ---
    action_dict = {
        "farmer": [farmer_action],
        "hands": hands_actions,
        "market": market_orders
    }
    
    # --- DEBUG LOG ---
    print(f"Day {day:02d} Hr {hour:02d} | Pos: {state.farmer_pos} | Act: {farmer_action} | Money: {money}")
    
    return action_dict

if __name__ == "__main__":
    try:
        from kaggle_environments import make
        env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=True)
        env.run([agent, "random"])
        print("Final Rewards:", env.steps[-1][0].reward, env.steps[-1][1].reward)
    except ImportError:
        print("kaggle_environments not installed, skipping test.")
