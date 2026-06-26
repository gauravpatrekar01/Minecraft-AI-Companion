import os

# Grid & Tile setup
TILE_SIZE = 16          # 16x16 pixel textures
SCALE = 2               # Pixel-art scale multiplier (e.g., 2x scale makes tiles 32x32 on screen)
SCALED_TILE = TILE_SIZE * SCALE

# Screen and Layout Bounds
# Note: Screen dimensions are dynamically queried at startup via win32api, 
# but these serve as standard fallback values.
DEFAULT_WIDTH = 1920
DEFAULT_HEIGHT = 1080

# Day/Night Cycle Duration (in seconds)
DAY_DURATION = 180      # 3 minutes of daytime
NIGHT_DURATION = 120    # 2 minutes of nighttime

# Physics and Movement
GRAVITY = 0.4
JUMP_FORCE = -8.0
WALK_SPEED = 2.0
RUN_SPEED = 3.5

# Paths
SAVE_FILENAME = "steve_save.json"

# Progression levels (based on cumulative stats/days)
PROGRESSION_TIERS = {
    1: {"name": "Wood Age", "desc": "Wood Pickaxe, Tiny Campfire", "wood_req": 5},
    5: {"name": "Stone Age", "desc": "Stone Pickaxe, House, Furnace, Bed, Farm", "wood_req": 20, "stone_req": 15},
    20: {"name": "Iron & Diamond Age", "desc": "Iron/Diamond gear, Bridge, Village, Wolf", "wood_req": 50, "stone_req": 100, "iron_req": 10, "diamond_req": 5},
    50: {"name": "Nether Age", "desc": "Nether Portal, Huge Base, Enchants", "wood_req": 100, "stone_req": 200, "iron_req": 30, "diamond_req": 15}
}

# Items and Max Stacks
MAX_STACK = 64
DEFAULT_INVENTORY = {
    "wood": 0,
    "stone": 0,
    "coal": 0,
    "iron": 0,
    "gold": 0,
    "diamond": 0,
    "bread": 5,      # Start with some bread
    "bone": 0,
    "potion": 1      # Start with one healing potion
}

DEFAULT_STATS = {
    "trees_cut": 0,
    "blocks_mined": 0,
    "zombies_killed": 0,
    "buildings": 0,
    "distance_walked": 0.0,  # in meters/pixels converted
    "diamonds_found": 0,
    "creeper_explosions": 0,
    "xp": 0,
    "level": 1
}

# Palette definitions
COLOR_KEY = (255, 0, 255)  # Magenta for transparency
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_GREY = (120, 120, 120)
COLOR_DARK_GREY = (40, 40, 40)
COLOR_GREEN = (34, 177, 76)
COLOR_SKY_DAY = (135, 206, 235)
COLOR_SKY_NIGHT = (10, 10, 25)
COLOR_GOLD = (255, 215, 0)
COLOR_DIAMOND = (90, 220, 220)
COLOR_RED = (255, 50, 50)
COLOR_HEAL_HEART = (240, 50, 80)
