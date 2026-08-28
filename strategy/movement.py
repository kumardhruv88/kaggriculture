from collections import deque

def manhattan(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def bfs_path(grid, start, goal, board_size=10):
    """
    BFS pathfinding function.
    Grid is tiles[y][x], locked tiles ARE passable (movement only, no actions).
    Returns list like ["NORTH", "EAST", "EAST"] or [] if already there.
    goal can be a single (x,y) or a list of targets (find nearest).
    """
    if isinstance(goal, tuple) and len(goal) == 2 and isinstance(goal[0], int):
        targets = {goal}
    else:
        targets = set(goal)
        
    if start in targets:
        return []
        
    queue = deque([(start, [])])
    visited = {start}
    
    # Directions: (dx, dy) assuming (0,0) is top-left
    directions = {
        "NORTH": (0, -1),
        "SOUTH": (0, 1),
        "EAST": (1, 0),
        "WEST": (-1, 0)
    }
    
    while queue:
        curr, path = queue.popleft()
        cx, cy = curr
        
        for d_name, (dx, dy) in directions.items():
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < board_size and 0 <= ny < board_size:
                nxt = (nx, ny)
                if nxt not in visited:
                    new_path = path + [d_name]
                    if nxt in targets:
                        return new_path
                    visited.add(nxt)
                    queue.append((nxt, new_path))
    return []

def next_move_toward(state, unit_pos, target_pos):
    """Returns the first step of BFS path or 'PASS' if already there."""
    path = bfs_path(state.my_tiles, unit_pos, target_pos)
    if path:
        return path[0]
    return "PASS"

def find_nearest_empty_tile(state, from_pos):
    """Returns the (x,y) of the nearest unlocked empty tile or None."""
    empty_tiles = state.empty_tiles()
    if not empty_tiles:
        return None
    return min(empty_tiles, key=lambda t: manhattan(from_pos, t))

def find_nearest_plant(state, from_pos, crop_type=None, condition=None):
    """
    Returns the (x,y) of the nearest plant matching the given criteria.
    condition can be 'needs_water', 'ready_to_harvest', 'needs_fertilize'.
    """
    crop_tiles = state.find_all_tiles_of_type("crop", crop_type)
    
    valid_tiles = []
    for x, y in crop_tiles:
        tile = state.get_tile(x, y)
        if not tile:
            continue
            
        if condition == "needs_water":
            if not tile.get("watered", False):
                valid_tiles.append((x, y))
        elif condition == "ready_to_harvest":
            if tile.get("harvestable", False):
                valid_tiles.append((x, y))
        elif condition == "needs_fertilize":
            if not tile.get("fertilized", False):
                valid_tiles.append((x, y))
        else:
            valid_tiles.append((x, y))
            
    if not valid_tiles:
        return None
        
    return min(valid_tiles, key=lambda t: manhattan(from_pos, t))

def find_shed_adjacent_tile(state, from_pos):
    """Returns the nearest shed tile from (4,4), (5,4), (4,5), (5,5)."""
    from utils.constants import SHED_POSITIONS
    return min(SHED_POSITIONS, key=lambda t: manhattan(from_pos, t))

class Unit:
    """Class to manage multiple units (farmer + hands)."""
    def __init__(self, unit_id, position):
        self.unit_id = unit_id
        self.position = position
        self.current_task_queue = []
        
    def assign_task(self, task_list):
        """Sets the current task queue."""
        self.current_task_queue = list(task_list)
        
    def get_next_action(self, state):
        """Returns the next action from the queue (and pops it) or 'PASS'."""
        if self.current_task_queue:
            return self.current_task_queue.pop(0)
        return "PASS"
