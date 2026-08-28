# utils/constants.py

BOARD_SIZE = 10
TURNS_PER_DAY = 24
SHED_CAPACITY = 100
STARTING_MONEY = 3000
LAND_COSTS = [1000, 2000, 4000]

# Center tiles
SHED_POSITIONS = [(4, 4), (5, 4), (4, 5), (5, 5)]

CROPS = {
    "WHEAT": {
        "seed_cost": 10,
        "base_price": 20,
        "first_yield_day": 3,
        "max_yield_day": 3,
        "yield_type": "one-time",
        "max_yield": 1
    },
    "CARROT": {
        "seed_cost": 20,
        "base_price": 45,
        "first_yield_day": 4,
        "max_yield_day": 4,
        "yield_type": "one-time",
        "max_yield": 1
    },
    "TOMATO": {
        "seed_cost": 30,
        "base_price": 25,
        "first_yield_day": 5,
        "max_yield_day": 12,
        "yield_type": "ongoing",
        "max_yield": 5
    },
    "STRAWBERRY": {
        "seed_cost": 40,
        "base_price": 35,
        "first_yield_day": 6,
        "max_yield_day": 15,
        "yield_type": "ongoing",
        "max_yield": 6
    },
    "MELON": {
        "seed_cost": 100,
        "base_price": 300,
        "first_yield_day": 8,
        "max_yield_day": 8,
        "yield_type": "one-time",
        "max_yield": 1
    }
}

ANIMALS = {
    "GOOSE": {
        "animal_cost": 100,
        "product_base_price": 20,
        "yield_interval": 1,
        "build_cost": 1, # 1 turn to build coop
        "product_name": "egg"
    },
    "COW": {
        "animal_cost": 500,
        "product_base_price": 80,
        "yield_interval": 2,
        "build_cost": 1, # 1 turn to build pasture
        "product_name": "milk"
    },
    "SHEEP": {
        "animal_cost": 800,
        "product_base_price": 150,
        "yield_interval": 4,
        "build_cost": 1, # 1 turn to build pasture
        "product_name": "wool"
    }
}
