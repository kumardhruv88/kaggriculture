from .constants import SHED_POSITIONS, BOARD_SIZE

class GameState:
    def __init__(self, obs):
        self.obs = obs

    @property
    def current_day(self):
        return self.obs.get("current_day", 0)

    @property
    def current_hour(self):
        return self.obs.get("current_hour", 0)

    @property
    def my_farm(self):
        return self.obs.get("my_farm", {})

    @property
    def my_money(self):
        return self.obs.get("my_money", 0)

    @property
    def my_tiles(self):
        # 2D list of tiles representing the 10x10 board
        return self.obs.get("my_tiles", [[{} for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)])

    @property
    def farmer_pos(self):
        return self.obs.get("farmer_pos", (0, 0))

    @property
    def shed_contents(self):
        return self.obs.get("shed_contents", {})

    @property
    def seed_counts(self):
        return self.obs.get("seed_counts", {})

    @property
    def inventories(self):
        return self.obs.get("inventories", {})

    @property
    def market_prices(self):
        return self.obs.get("market_prices", {})

    @property
    def market_inventory(self):
        return self.obs.get("market_inventory", {})

    @property
    def unlocked_shops(self):
        return self.obs.get("unlocked_shops", [])

    def get_tile(self, x, y):
        """Returns the tile dict at (x, y)."""
        if 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE:
            return self.my_tiles[y][x]
        return None

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
                    
                    if quadrant_idx in unlocked_quads and (x, y) not in SHED_POSITIONS:
                        found.append((x, y))
        return found
