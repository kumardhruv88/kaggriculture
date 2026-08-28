from .constants import SHED_POSITIONS, BOARD_SIZE

class GameState:
    def __init__(self, obs):
        self.obs = obs

    @property
    def player(self):
        return self.obs.get("player", 0)

    @property
    def current_day(self):
        return self.obs.get("day", 0)

    @property
    def current_hour(self):
        return self.obs.get("hour", 0)

    @property
    def my_farm(self):
        farms = self.obs.get("farms", [])
        if isinstance(farms, dict):
            return farms.get(str(self.player), farms.get(self.player, {}))
        elif isinstance(farms, list) and len(farms) > self.player:
            return farms[self.player]
        return {}

    @property
    def my_money(self):
        return self.my_farm.get("money", 3000)

    @property
    def my_tiles(self):
        return self.my_farm.get("tiles", [[{} for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)])

    @property
    def farmer_pos(self):
        pos = self.my_farm.get("farmer", [0, 0])
        return tuple(pos) if isinstance(pos, list) else pos

    @property
    def shed_contents(self):
        return self.obs.get("private", {}).get("shed", {})

    @property
    def seed_counts(self):
        return self.obs.get("private", {}).get("seeds", {})

    @property
    def inventories(self):
        return self.obs.get("private", {}).get("inventories", {})

    @property
    def market_prices(self):
        return self.obs.get("market", {}).get("prices", {})

    @property
    def market_inventory(self):
        return self.obs.get("market", {}).get("inventory", {})

    @property
    def unlocked_shops(self):
        return self.obs.get("unlocked_shops", [])

    def get_tile(self, x, y):
        """Returns the tile dict at (x, y)."""
        if 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE:
            try:
                # If tiles is a flat list in some versions, this might fail, assuming 2D list
                return self.my_tiles[y][x]
            except (IndexError, KeyError, TypeError):
                pass
        return {}

    def is_shed_adjacent(self, x, y):
        """Returns True if the given tile is adjacent to any shed position."""
        for sx, sy in SHED_POSITIONS:
            if abs(sx - x) + abs(sy - y) == 1:
                return True
        return False

    def unlocked_quadrants(self):
        return self.obs.get("unlocked_quadrants", [])

    def find_all_tiles_of_type(self, kind, crop=None):
        """Returns a list of (x, y) coordinates of tiles matching the given kind and optionally crop."""
        found = []
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                tile = self.get_tile(x, y)
                if tile and tile.get("kind") == kind:
                    if crop is None or tile.get("crop") == crop:
                        found.append((x, y))
        return found

    def empty_tiles(self):
        """Returns a list of (x, y) coordinates of unlocked empty tiles."""
        found = []
        unlocked_quads = self.unlocked_quadrants()
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                tile = self.get_tile(x, y)
                if tile and tile.get("kind") == "empty":
                    # Determine quadrant: 0 (top-left), 1 (top-right), 2 (bottom-left), 3 (bottom-right)
                    quad_x = x // (BOARD_SIZE // 2)
                    quad_y = y // (BOARD_SIZE // 2)
                    quadrant_idx = quad_y * 2 + quad_x
                    
                    if not unlocked_quads or quadrant_idx in unlocked_quads:
                        if (x, y) not in SHED_POSITIONS:
                            found.append((x, y))
        return found
