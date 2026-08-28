from utils.constants import CROPS, SHED_POSITIONS

class CropManager:
    def __init__(self, state):
        self.state = state

    def should_plant(self):
        """
        Returns a dict of {crop_type: count} to plant this turn based on priority logic.
        """
        state = self.state
        day = state.current_day
        money = state.my_money
        
        empty_tiles = len(state.empty_tiles())
        if empty_tiles < 2:
            return {}
            
        available_to_plant = empty_tiles - 2
        plan = {}
        
        if available_to_plant <= 0:
            return {"WHEAT": 2}
            
        # Always reserve 2 tiles near shed for wheat (animal feed buffer)
        plan["WHEAT"] = 2
        remaining_tiles = available_to_plant
        
        if 1 <= day <= 5:
            # Day 1-5: Plant wheat aggressively
            plan["WHEAT"] += remaining_tiles
            
        elif 6 <= day <= 15:
            # Day 6-15: Shift to melons
            melons_to_plant = self.plan_melon_waves()
            actual_melons = min(remaining_tiles, melons_to_plant)
            if actual_melons > 0:
                plan["MELON"] = actual_melons
                remaining_tiles -= actual_melons
                
            # Day 8+: Add carrots with fertilizer plan
            if day >= 8 and remaining_tiles > 0:
                plan["CARROT"] = remaining_tiles
            elif remaining_tiles > 0:
                plan["WHEAT"] += remaining_tiles
                
        elif day > 15:
            # Day 10+: Strawberries if money > 5000
            if day >= 10 and money > 5000:
                plan["STRAWBERRY"] = remaining_tiles
            elif day >= 8:
                plan["CARROT"] = remaining_tiles
            else:
                plan["WHEAT"] += remaining_tiles
                
        return plan

    def get_water_targets(self):
        """
        Returns list of (x,y) to water. Priority: ongoing first, then one-time.
        """
        state = self.state
        ongoing_targets = []
        one_time_targets = []
        
        crop_tiles = state.find_all_tiles_of_type("crop")
        for x, y in crop_tiles:
            tile = state.get_tile(x, y)
            if not tile.get("watered_today", False):
                crop_name = tile.get("crop")
                if crop_name in CROPS:
                    if CROPS[crop_name]["yield_type"] == "ongoing":
                        ongoing_targets.append((x, y))
                    else:
                        one_time_targets.append((x, y))
                else:
                    one_time_targets.append((x, y))
                    
        return ongoing_targets + one_time_targets

    def get_harvest_targets(self):
        """
        Returns list of (x,y) to harvest based on yield and decay.
        """
        state = self.state
        targets = []
        crop_tiles = state.find_all_tiles_of_type("crop")
        
        for x, y in crop_tiles:
            tile = state.get_tile(x, y)
            yield_units = tile.get("yield_units", 0)
            
            if yield_units > 0:
                # URGENT: harvest before decay starts
                max_lifespan = tile.get("max_lifespan_step", 999)
                current_step = tile.get("current_step", 0)
                if (max_lifespan - current_step) < 5:
                    targets.append((x, y))
                    continue
                    
                crop_name = tile.get("crop")
                if crop_name in CROPS:
                    crop_data = CROPS[crop_name]
                    if crop_data["yield_type"] == "ongoing":
                        # Harvest whenever yield_units > 0
                        targets.append((x, y))
                    elif crop_data["yield_type"] == "one-time":
                        # Harvest at max_yield_day or later
                        growth = tile.get("growth", 0)
                        if growth >= crop_data["max_yield_day"]:
                            targets.append((x, y))
                else:
                    targets.append((x, y))
                    
        return targets

    def get_fertilize_targets(self):
        """
        Returns list of (x,y) to fertilize, prioritized by ROI.
        """
        state = self.state
        targets = []
        fertilizer_count = state.shed_contents.get("fertilizer", 0)
        
        if fertilizer_count <= 0:
            return targets
            
        crop_tiles = state.find_all_tiles_of_type("crop")
        priorities = {"MELON": 3, "CARROT": 2, "WHEAT": 1}
        candidates = []
        
        for x, y in crop_tiles:
            tile = state.get_tile(x, y)
            crop_name = tile.get("crop")
            
            if crop_name in CROPS:
                crop_data = CROPS[crop_name]
                # One-time crops only in the [first_yield, max_yield] window
                if crop_data["yield_type"] == "one-time":
                    growth = tile.get("growth", 0)
                    if crop_data["first_yield_day"] <= growth <= crop_data["max_yield_day"]:
                        fertilized_until = tile.get("fertilized_until_day", -1)
                        if fertilized_until < state.current_day:
                            candidates.append((priorities.get(crop_name, 0), (x, y)))
                            
        # Sort by priority descending
        candidates.sort(key=lambda item: item[0], reverse=True)
        return [pos for _, pos in candidates]

    def get_dig_targets(self):
        """
        Returns list of (x,y) of weeds or dead crops to dig up.
        """
        state = self.state
        weed_tiles = state.find_all_tiles_of_type("weed")
        
        dead_crops = []
        for x, y in state.find_all_tiles_of_type("crop"):
            tile = state.get_tile(x, y)
            if tile.get("is_dead", False) or tile.get("harvested_one_time", False):
                dead_crops.append((x, y))
                
        return weed_tiles + dead_crops

    def plan_melon_waves(self):
        """
        Returns how many melons to plant this turn based on available tiles and money.
        """
        state = self.state
        day = state.current_day
        money = state.my_money
        
        # Melon takes 10 days to max yield, so last plant date is day 20
        if day > 20:
            return 0
            
        empty_tiles = len(state.empty_tiles())
        available_tiles = max(0, empty_tiles - 2)
        
        melon_cost = CROPS["MELON"]["seed_cost"]
        max_affordable = money // melon_cost if melon_cost > 0 else 0
        
        return min(available_tiles, max_affordable)
