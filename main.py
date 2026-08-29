AGENT_STATE = {}

def agent(obs):
    player = obs["player"]
    me = obs["farms"][player]
    private = obs["private"]
    day = obs["day"]
    hour = obs["hour"]
    fx, fy = me["farmer"]
    tile = me["tiles"][fy][fx]
    money = me["money"]
    
    market = []
    
    # Buy wheat seeds if we have none
    if private["seeds"].get("WHEAT", 0) < 3 and money >= 10:
        market.append(["BUY_SEED", "WHEAT", 5])
    
    # Sell wheat in shed
    wheat_shed = private["shed"].get("WHEAT", 0)
    if wheat_shed > 0:
        market.append(["SELL", "WHEAT", wheat_shed])
    
    print(f"Day {day:02d} Hr {hour:02d} | Pos: ({fx},{fy}) | Money: {money:.0f} | Tile: {tile}")
    
    # If on empty unlocked tile and have seeds: plant
    if tile is None and private["seeds"].get("WHEAT", 0) > 0:
        return {"farmer": ["PLANT", "WHEAT"], "hands": [], "market": market}
    
    # If on a plant
    if isinstance(tile, dict) and tile.get("kind") == "PLANT":
        age = day - tile.get("planted_day", day)
        if tile.get("yield_units", 0) > 0 and age >= 2:
            return {"farmer": ["HARVEST"], "hands": [], "market": market}
        if not tile.get("watered_today", False):
            return {"farmer": ["WATER"], "hands": [], "market": market}
    
    # If on weed: dig it
    if isinstance(tile, dict) and tile.get("kind") == "WEED":
        return {"farmer": ["DIG"], "hands": [], "market": market}
    
    # Move to explore — go south then wrap east
    board = me["tiles"]
    # Find nearest empty or plant tile
    for dy in range(10):
        for dx in range(10):
            nx, ny = (fx + dx) % 10, (fy + dy) % 10
            t = board[ny][nx]
            if t == "LOCKED":
                continue
            if t is None and private["seeds"].get("WHEAT", 0) > 0:
                # move toward it
                if ny > fy: return {"farmer": ["SOUTH"], "hands": [], "market": market}
                if ny < fy: return {"farmer": ["NORTH"], "hands": [], "market": market}
                if nx > fx: return {"farmer": ["EAST"], "hands": [], "market": market}
                if nx < fx: return {"farmer": ["WEST"], "hands": [], "market": market}
            if isinstance(t, dict) and t.get("kind") == "PLANT":
                if not t.get("watered_today", False) or t.get("yield_units", 0) > 0:
                    if ny > fy: return {"farmer": ["SOUTH"], "hands": [], "market": market}
                    if ny < fy: return {"farmer": ["NORTH"], "hands": [], "market": market}
                    if nx > fx: return {"farmer": ["EAST"], "hands": [], "market": market}
                    if nx < fx: return {"farmer": ["WEST"], "hands": [], "market": market}
    
    return {"farmer": ["PASS"], "hands": [], "market": market}
