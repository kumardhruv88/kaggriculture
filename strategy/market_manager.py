from utils.constants import CROPS, ANIMALS, LAND_COSTS, SHED_CAPACITY

class MarketManager:
    def __init__(self, state):
        self.state = state

    def get_sell_orders(self):
        """
        Returns a list of [SELL, item, qty] orders based on smart selling logic.
        """
        state = self.state
        orders = []
        
        shed = state.shed_contents
        total_items = sum(shed.values())
        emergency = total_items > (SHED_CAPACITY * 0.8)
        
        prices = state.market_prices
        sellable_items = []
        
        for item, qty in shed.items():
            if qty <= 0:
                continue
                
            price = prices.get(item, 0)
            
            # Emergency sell everything
            if emergency:
                sellable_items.append((price, item, qty))
                continue
                
            # Item specific logic
            if item == "MELON":
                # Hold melons if price < 150
                if price >= 150:
                    sellable_items.append((price, item, qty))
            elif item == "WHEAT":
                # Sell wheat freely
                sellable_items.append((price, item, qty))
            elif item == "fertilizer":
                # Sell fertilizer if price > 80 and shed has >5 units
                if price > 80 and qty > 5:
                    sellable_items.append((price, item, qty - 5))
            else:
                # Other items
                sellable_items.append((price, item, qty))
                
        # Priority: sell items with highest current market price first
        sellable_items.sort(key=lambda x: x[0], reverse=True)
        
        for price, item, total_qty in sellable_items:
            # Never sell everything at once — sell in batches of max 10
            qty_to_sell = total_qty
            while qty_to_sell > 0:
                batch = min(10, qty_to_sell)
                orders.append(["SELL", item, batch])
                qty_to_sell -= batch
                
        return orders

    def get_buy_orders(self):
        """
        Returns a list of [BUY_SEED/BUY_PRODUCT/BUY_ANIMAL, item, qty] orders.
        """
        state = self.state
        orders = []
        money = state.my_money
        day = state.current_day
        
        # --- Seed Buying ---
        wheat_seeds = state.seed_counts.get("WHEAT", 0)
        if wheat_seeds < 5:
            qty = 5 - wheat_seeds
            cost = CROPS["WHEAT"]["seed_cost"] * qty
            if money >= cost:
                orders.append(["BUY_SEED", "WHEAT", qty])
                money -= cost
                
        if money > 2000:
            melon_seeds = state.seed_counts.get("MELON", 0)
            if melon_seeds < 5:
                orders.append(["BUY_SEED", "MELON", 5])
                money -= CROPS["MELON"]["seed_cost"] * 5
                
        if money > 1500 and day < 25:
            carrot_seeds = state.seed_counts.get("CARROT", 0)
            if carrot_seeds < 5:
                orders.append(["BUY_SEED", "CARROT", 5])
                money -= CROPS["CARROT"]["seed_cost"] * 5
                
        if money > 4000 and 8 <= day <= 20:
            strawberry_seeds = state.seed_counts.get("STRAWBERRY", 0)
            if strawberry_seeds < 3:
                orders.append(["BUY_SEED", "STRAWBERRY", 3])
                money -= CROPS["STRAWBERRY"]["seed_cost"] * 3
                
        # --- Animal Buying ---
        if money > 4000:
            geese_count = len(state.find_all_tiles_of_type("animal", crop="GOOSE"))
            cows_count = len(state.find_all_tiles_of_type("animal", crop="COW"))
            
            if geese_count == 0:
                cost = ANIMALS["GOOSE"]["animal_cost"]
                if money > cost:
                    orders.append(["BUY_ANIMAL", "GOOSE", 1])
                    money -= cost
                    
            unlocked_shops = state.unlocked_shops
            if "BAKERY" in unlocked_shops or "BRUNCH_SPOT" in unlocked_shops:
                if cows_count == 0:
                    cost = ANIMALS["COW"]["animal_cost"]
                    if money > cost:
                        orders.append(["BUY_ANIMAL", "COW", 1])
                        money -= cost
                        
        # --- Product Buying ---
        has_animals = len(state.find_all_tiles_of_type("animal")) > 0
        if has_animals:
            wheat_in_shed = state.shed_contents.get("WHEAT", 0)
            if wheat_in_shed < 10:
                qty_to_buy = 10 - wheat_in_shed
                wheat_price = state.market_prices.get("WHEAT", 20)
                if money > wheat_price * qty_to_buy:
                    orders.append(["BUY_PRODUCT", "WHEAT", qty_to_buy])
                    money -= wheat_price * qty_to_buy
                    
        return orders

    def should_hire_hand(self):
        """
        Returns the number of extra hands to hire today (0, 1, or 2).
        """
        state = self.state
        money = state.my_money
        
        # Never hire if money < 1500
        if money < 1500:
            return 0
            
        crop_tiles = state.find_all_tiles_of_type("crop")
        needs_water = 0
        ready_to_harvest = 0
        
        for x, y in crop_tiles:
            tile = state.get_tile(x, y)
            if not tile.get("watered_today", False):
                needs_water += 1
            if tile.get("harvestable", False) or tile.get("yield_units", 0) > 0:
                ready_to_harvest += 1
                
        total_needs_attention = needs_water + ready_to_harvest
        
        # Hire 2 hands if: >25 plants need attention AND money > 3000
        if total_needs_attention > 25 and money > 3000:
            return 2
            
        # Hire 1 hand if: >15 plants need watering OR >10 plants ready to harvest
        if needs_water > 15 or ready_to_harvest > 10:
            return 1
            
        return 0

    def should_buy_land(self):
        """
        Returns True if the agent should buy a new land quadrant this turn.
        """
        state = self.state
        money = state.my_money
        day = state.current_day
        unlocked = state.unlocked_quadrants()
        
        # Quadrant logic: 0=NW (start), 1=NE, 2=SW, 3=SE
        NE_QUADRANT = 1
        SW_QUADRANT = 2
        
        num_unlocked_extra = max(0, len(unlocked) - 1)
        # Prevent index out of bounds if all are unlocked
        current_land_cost = LAND_COSTS[num_unlocked_extra] if num_unlocked_extra < len(LAND_COSTS) else 999999
        
        # Buy NE quadrant when money > 4000 and day < 15
        if NE_QUADRANT not in unlocked and money > 4000 and day < 15:
            if money - current_land_cost >= 2000:
                return True
                
        # Buy SW quadrant when money > 8000 and day < 20
        if SW_QUADRANT not in unlocked and money > 8000 and day < 20:
            if money - current_land_cost >= 2000:
                return True
                
        return False

    def analyze_shop_impact(self):
        """
        Calculates and returns the top 3 products with the highest demand based on unlocked shops.
        """
        state = self.state
        unlocked = state.unlocked_shops
        
        demand = {
            "egg": 0,
            "STRAWBERRY": 0,
            "milk": 0,
            "wool": 0
        }
        
        for shop in unlocked:
            if shop == "BAKERY":
                demand["egg"] += 2
            elif shop == "BRUNCH_SPOT":
                demand["egg"] += 2
                demand["STRAWBERRY"] += 2
            elif shop == "ICE_CREAM_SHOP":
                demand["STRAWBERRY"] += 2
            elif shop == "SMOOTHIE_SHOP":
                demand["STRAWBERRY"] += 2
                
        # Return top 3 products
        sorted_demand = sorted(demand.items(), key=lambda item: item[1], reverse=True)
        top_3 = {k: v for k, v in sorted_demand[:3]}
        
        return top_3
