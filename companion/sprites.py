import pygame
from companion.config import SCALE, TILE_SIZE, SCALED_TILE, COLOR_KEY

# Palette mappings (RGB)
PALETTES = {
    "blocks": {
        ".": None,
        "g": (92, 142, 50),     # light grass green
        "G": (76, 120, 40),     # dark grass green
        "d": (134, 96, 67),     # light dirt brown
        "D": (87, 61, 38),      # dark dirt brown
        "s": (115, 115, 115),   # stone grey
        "S": (82, 82, 82),      # dark stone grey
        "c": (28, 28, 28),      # coal black
        "i": (216, 175, 147),   # iron ore peach
        "o": (252, 208, 60),    # gold yellow
        "x": (77, 237, 240),    # diamond cyan
        "w": (171, 127, 86),    # wood log brown
        "W": (122, 88, 58),     # dark wood log
        "l": (59, 94, 43),      # light leaf green
        "L": (44, 71, 32),      # dark leaf green
        "p": (180, 140, 100),   # wood plank light
        "P": (140, 105, 70),    # wood plank dark
        "v": (100, 30, 120),    # portal purple light
        "V": (60, 10, 80),      # portal purple dark
        "y": (255, 128, 0),     # fire orange
        "Y": (255, 230, 0),     # fire yellow
        "f": (70, 70, 70),      # furnace metal
        "F": (30, 30, 30),      # furnace metal dark
    },
    "steve": {
        ".": None,
        "h": (241, 194, 149),   # skin tan
        "H": (211, 163, 122),   # skin shadow
        "b": (75, 49, 23),      # brown hair / eyes
        "c": (0, 162, 232),     # cyan shirt
        "C": (0, 120, 180),     # dark cyan shirt
        "p": (63, 72, 204),     # blue pants
        "P": (40, 48, 150),     # dark blue pants
        "s": (85, 85, 85),      # grey shoes
        "e": (255, 255, 255),   # white (eyes)
        "E": (47, 54, 153),     # blue (eyes)
        "r": (255, 0, 0),       # red (hurt/Santa hat)
        "w": (255, 255, 255),   # white (Santa hat trim)
    },
    "mobs": {
        ".": None,
        "z": (92, 142, 50),     # zombie light green skin
        "Z": (65, 103, 34),     # zombie dark green skin
        "c": (0, 162, 232),     # zombie faded shirt
        "p": (63, 72, 204),     # zombie faded pants
        "h": (241, 194, 149),   # villager skin
        "H": (180, 130, 95),    # villager skin dark
        "r": (125, 92, 56),     # villager brown robe
        "R": (95, 68, 40),      # villager dark brown robe
        "w": (240, 240, 240),   # librarian white robe
        "P": (70, 60, 50),      # blacksmith apron
        "e": (10, 140, 30),     # villager green eyes
        "b": (163, 122, 82),    # big nose
        # Creeper
        "g": (80, 158, 47),     # creeper light green
        "G": (61, 130, 32),     # creeper dark green
        "k": (0, 0, 0),         # creeper black face
        # Wolf
        "w_w": (230, 230, 230), # wolf white
        "w_g": (179, 179, 179), # wolf grey
        "w_d": (128, 128, 128), # wolf dark grey
        "w_c": (237, 28, 36),   # wolf collar red
        "w_e": (0, 0, 0),       # wolf eyes black
        "w_h": (240, 50, 80),    # wolf love heart red
    },
    "items": {
        ".": None,
        "w": (140, 90, 60),     # wood brown
        "i": (220, 220, 220),   # iron grey
        "I": (170, 170, 170),   # dark iron
        "x": (77, 237, 240),    # diamond cyan
        "X": (40, 190, 190),    # dark diamond
        "g": (255, 215, 0),     # gold yellow
        "d": (80, 80, 80),      # dark wood stick
        "b": (214, 153, 92),    # bread light
        "B": (166, 108, 50),    # bread dark
        "r": (255, 50, 50),      # red potion
        "o": (255, 255, 255),   # bone white
    }
}

# Sprite string templates (16x16 for blocks/items, 16x32 for humanoid entities)

# BLOCKS (16x16)
BLOCK_TEMPLATES = {
    "grass": [
        "gggggggggggggggg",
        "gGgGgGgGgGgGgGgG",
        "GgGgGgGgGgGgGgGg",
        "dddddddddddddddd",
        "dDdDdDdDdDdDdDdD",
        "DdDdDdDdDdDdDdDd",
        "dDdDdDdDdDdDdDdD",
        "DdDdDdDdDdDdDdDd",
        "dddddddddddddddd",
        "dDdDdDdDdDdDdDdD",
        "DdDdDdDdDdDdDdDd",
        "dDdDdDdDdDdDdDdD",
        "DdDdDdDdDdDdDdDd",
        "dddddddddddddddd",
        "dDdDdDdDdDdDdDdD",
        "DdDdDdDdDdDdDdDd"
    ],
    "dirt": [
        "dddddddddddddddd",
        "dDdDdDdDdDdDdDdD",
        "DdDdDdDdDdDdDdDd",
        "dDdDdDdDdDdDdDdD",
        "DdDdDdDdDdDdDdDd",
        "dddddddddddddddd",
        "dDdDdDdDdDdDdDdD",
        "DdDdDdDdDdDdDdDd",
        "dDdDdDdDdDdDdDdD",
        "DdDdDdDdDdDdDdDd",
        "dddddddddddddddd",
        "dDdDdDdDdDdDdDdD",
        "DdDdDdDdDdDdDdDd",
        "dDdDdDdDdDdDdDdD",
        "DdDdDdDdDdDdDdDd",
        "dddddddddddddddd"
    ],
    "stone": [
        "ssssssssssssssss",
        "sSsSsSsSsSsSsSsS",
        "SsSsSsSsSsSsSsSs",
        "sSsSsSsSsSsSsSsS",
        "SsSsSsSsSsSsSsSs",
        "ssssssssssssssss",
        "sSsSsSsSsSsSsSsS",
        "SsSsSsSsSsSsSsSs",
        "sSsSsSsSsSsSsSsS",
        "SsSsSsSsSsSsSsSs",
        "ssssssssssssssss",
        "sSsSsSsSsSsSsSsS",
        "SsSsSsSsSsSsSsSs",
        "sSsSsSsSsSsSsSsS",
        "SsSsSsSsSsSsSsSs",
        "ssssssssssssssss"
    ],
    "coal_ore": [
        "ssssssssssssssss",
        "sSsScSsSsScSsSsS",
        "SsSsSsSsSsSsSsSs",
        "sSccSsSsSccSsSsS",
        "SsSsSsSsSsSsSsSs",
        "sssssssssccsssss",
        "sSsSsSsSsScSsSsS",
        "SsSsSsSsSsSsSsSs",
        "sSsScSsSsSsSsSsS",
        "SsSccSsSsSsSsSsS",
        "ssssssssssssssss",
        "sSsSsScScSsSsSsS",
        "SsSsSccSsSsSsSsS",
        "sSsSsSsSsSsSsSsS",
        "SsSsSsSsSsSsSsSs",
        "ssssssssssssssss"
    ],
    "iron_ore": [
        "ssssssssssssssss",
        "sSsSiSsSsSiSsSsS",
        "SsSsSsSsSsSsSsSs",
        "sSiiSsSsSiiSsSsS",
        "SsSsSsSsSsSsSsSs",
        "sssssssssiisssss",
        "sSsSsSsSsSiSsSsS",
        "SsSsSsSsSsSsSsSs",
        "sSsSiSsSsSsSsSsS",
        "SsSiiSsSsSsSsSsS",
        "ssssssssssssssss",
        "sSsSsSiSiSsSsSsS",
        "SsSsSiiSsSsSsSsS",
        "sSsSsSsSsSsSsSsS",
        "SsSsSsSsSsSsSsSs",
        "ssssssssssssssss"
    ],
    "diamond_ore": [
        "ssssssssssssssss",
        "sSsSxSsSsSxSsSsS",
        "SsSsSsSsSsSsSsSs",
        "sSxxSsSsSxxSsSsS",
        "SsSsSsSsSsSsSsSs",
        "sssssssssxxsssss",
        "sSsSsSsSsSxSsSsS",
        "SsSsSsSsSsSsSsSs",
        "sSsSxSsSsSsSsSsS",
        "SsSxxSsSsSsSsSsS",
        "ssssssssssssssss",
        "sSsSsSxSxSsSsSsS",
        "SsSsSxxSsSsSsSsS",
        "sSsSsSsSsSsSsSsS",
        "SsSsSsSsSsSsSsSs",
        "ssssssssssssssss"
    ],
    "wood_log": [
        "WWWWWWWWWWWWWWWW",
        "WwwwwwwwwwwwwwwW",
        "WwWWWWWWWWWWWWwW",
        "WwWwwwwwwwwwwWwW",
        "WwWwWWWWWWWWwWwW",
        "WwWwWwwwwwwWwWwW",
        "WwWwWwWWWWwWwWwW",
        "WwWwWwWwwWwWwWwW",
        "WwWwWwWwwWwWwWwW",
        "WwWwWwWWWWwWwWwW",
        "WwWwWwwwwwwWwWwW",
        "WwWwWWWWWWWWwWwW",
        "WwWwwwwwwwwwwWwW",
        "WwWWWWWWWWWWWWwW",
        "WwwwwwwwwwwwwwwW",
        "WWWWWWWWWWWWWWWW"
    ],
    "wood_log_side": [
        "WWWWWWWWWWWWWWWW",
        "wwwwwwwwwwwwwwww",
        "wwwwwwwwwwwwwwww",
        "WWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWW",
        "wwwwwwwwwwwwwwww",
        "wwwwwwwwwwwwwwww",
        "WWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWW",
        "wwwwwwwwwwwwwwww",
        "wwwwwwwwwwwwwwww",
        "WWWWWWWWWWWWWWWW",
        "WWWWWWWWWWWWWWWW",
        "wwwwwwwwwwwwwwww",
        "wwwwwwwwwwwwwwww",
        "WWWWWWWWWWWWWWWW"
    ],
    "leaves": [
        "lLLlLLlLlLlLLlLL",
        "LlLLlLLlLLlLLlLL",
        "lLLlLLlLlLlLLlLL",
        "LlLLlLLlLLlLLlLL",
        "lLLlLLlLlLlLLlLL",
        "LlLLlLLlLLlLLlLL",
        "lLLlLLlLlLlLLlLL",
        "LlLLlLLlLLlLLlLL",
        "lLLlLLlLlLlLLlLL",
        "LlLLlLLlLLlLLlLL",
        "lLLlLLlLlLlLLlLL",
        "LlLLlLLlLLlLLlLL",
        "lLLlLLlLlLlLLlLL",
        "LlLLlLLlLLlLLlLL",
        "lLLlLLlLlLlLLlLL",
        "LlLLlLLlLLlLLlLL"
    ],
    "planks": [
        "PPPPPPPPPPPPPPPP",
        "PppppppppppppppP",
        "PppppppppppppppP",
        "PPPPPPPPPPPPPPPP",
        "PPPPPPPPPPPPPPPP",
        "PppppppppppppppP",
        "PppppppppppppppP",
        "PPPPPPPPPPPPPPPP",
        "PPPPPPPPPPPPPPPP",
        "PppppppppppppppP",
        "PppppppppppppppP",
        "PPPPPPPPPPPPPPPP",
        "PPPPPPPPPPPPPPPP",
        "PppppppppppppppP",
        "PppppppppppppppP",
        "PPPPPPPPPPPPPPPP"
    ],
    "crafting_table": [
        "PPPPPPPPPPPPPPPP",
        "PppppppppppppppP",
        "PppsspssspsssppP",
        "PppsspssspsssppP",
        "PppppppppppppppP",
        "PppppppppppppppP",
        "PppWWpWWWWpWWppP",
        "PppWWpWWWWpWWppP",
        "PppppppppppppppP",
        "PppppppppppppppP",
        "PppWWpWWWWpWWppP",
        "PppWWpWWWWpWWppP",
        "PppppppppppppppP",
        "PppppppppppppppP",
        "PppppppppppppppP",
        "PPPPPPPPPPPPPPPP"
    ],
    "furnace": [
        "SSSSSSSSSSSSSSSS",
        "SssssssssssssssS",
        "SssFFFFFFFFFsssS",
        "SssFsssssssFsssS",
        "SssFsssssssFsssS",
        "SssFFFFFFFFFsssS",
        "SssssssssssssssS",
        "SssFFFFFFFFFsssS",
        "SssFfffffffFsssS",
        "SssFfYYYYYfFsssS",
        "SssFfyyyyyfFsssS",
        "SssFfffffffFsssS",
        "SssFFFFFFFFFsssS",
        "SssssssssssssssS",
        "SssssssssssssssS",
        "SSSSSSSSSSSSSSSS"
    ],
    "chest": [
        "WWWWWWWWWWWWWWWW",
        "WwwwwwwwwwwwwwwW",
        "WwWWWWWWWWWWWWwW",
        "WwWwwwwwwwwwwWwW",
        "WwWwWWWWWWWWwWwW",
        "WwWwWwsSwsSwWwWw",
        "WwWwWwsSwsSwWwWw",
        "WwWwWwWWWWWWwWwW",
        "WwWwWwwwwwwWwWwW",
        "WwWwWWWWWWWWwWwW",
        "WwWwwwwwwwwwwWwW",
        "WwWWWWWWWWWWWWwW",
        "WwwwwwwwwwwwwwwW",
        "WWWWWWWWWWWWWWWW",
        "................",
        "................"
    ],
    "portal": [
        "VVVVVVVVVVVVVVVV",
        "VvvvvvvvvvvvvvvV",
        "VvVVvvVVvvVVvvVV",
        "VvVvVvVvVvVvVvVV",
        "VvVvVvVvVvVvVvVV",
        "VvVVvvVVvvVVvvVV",
        "VvvvvvvvvvvvvvvV",
        "VvVVvvVVvvVVvvVV",
        "VvVvVvVvVvVvVvVV",
        "VvVvVvVvVvVvVvVV",
        "VvVVvvVVvvVVvvVV",
        "VvvvvvvvvvvvvvvV",
        "VvVVvvVVvvVVvvVV",
        "VvVvVvVvVvVvVvVV",
        "VvvvvvvvvvvvvvvV",
        "VVVVVVVVVVVVVVVV"
    ],
    "campfire": [
        "................",
        "......y.........",
        ".....yyy........",
        "....yYyYy.......",
        "....yYyYy.......",
        ".....yyy........",
        "....w.w.w.......",
        "...w..w..w......",
        "..wwwwwwwww.....",
        "....w.w.w.......",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................"
    ]
}

# HUMANOIDS (16x32)
STEVE_TEMPLATES = {
    "idle": [
        "................",
        "......bbbb......",
        ".....bbbbbb.....",
        ".....bhhhhb.....",
        ".....hheehh.....",
        ".....hhhhhh.....",
        "......hhhh......",
        ".....hhhhhh.....",
        "....cchhhhcc....",
        "....cchhhhcc....",
        "....cccccccc....",
        "....cccccccc....",
        "....cccccccc....",
        "....cccccccc....",
        "....cccccccc....",
        "....cccccccc....",
        "....cccccccc....",
        ".....cccccc.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....p.pp.p.....",
        ".....s.ss.s.....",
        "....ss.ss.ss....",
        "....ss.ss.ss....",
        "................"
    ],
    "walk1": [
        "................",
        "......bbbb......",
        ".....bbbbbb.....",
        ".....bhhhhb.....",
        ".....hheehh.....",
        ".....hhhhhh.....",
        "......hhhh......",
        ".....hhhhhh.....",
        "....cchhhhcc....",
        "....cchhhhcc....",
        "....c.cccc.c....",
        "....c.cccc.c....",
        "....c.cccc.c....",
        "....c.cccc.c....",
        "......cccc......",
        "......cccc......",
        "......cccc......",
        "......cccc......",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....p.pp.p.....",
        ".....p.pp.p.....",
        ".....p.pp.p.....",
        ".....p....p.....",
        "....pp....pp....",
        "....p......p....",
        "....p......p....",
        "....p......p....",
        "....s......s....",
        "....ss....ss....",
        "....ss....ss....",
        "................"
    ],
    "walk2": [
        "................",
        "......bbbb......",
        ".....bbbbbb.....",
        ".....bhhhhb.....",
        ".....hheehh.....",
        ".....hhhhhh.....",
        "......hhhh......",
        ".....hhhhhh.....",
        "....cchhhhcc....",
        "....cchhhhcc....",
        "....cccccccc....",
        "....cccccccc....",
        "....cccccccc....",
        "....cccccccc....",
        "....cccccccc....",
        "....cccccccc....",
        "....cccccccc....",
        ".....cccccc.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....p.pp.p.....",
        ".....s.ss.s.....",
        "....ss.ss.ss....",
        "....ss.ss.ss....",
        "................"
    ],
    "mine": [
        "................",
        "......bbbb......",
        ".....bbbbbb.....",
        ".....bhhhhb.....",
        ".....hheehh.....",
        ".....hhhhhh.....",
        "......hhhh......",
        ".....hhhhhh..c..",
        "....cchhhhc.cc..",
        "....cchhhhc.c...",
        "....cccccccc....",
        "....cccccccc....",
        "....cccccccc....",
        "....cccccccc....",
        "....cccccccc....",
        "....cccccccc....",
        "....cccccccc....",
        ".....cccccc.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....p.pp.p.....",
        ".....s.ss.s.....",
        "....ss.ss.ss....",
        "....ss.ss.ss....",
        "................"
    ],
    "sleep": [
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "................................",
        "......bbbb......................",
        ".....bbbbbb.....................",
        ".....bhhhhb....cccccccccc.......",
        ".....hheehh....cccccccccc.......",
        ".....hhhhhh..cccccccccccccc.....",
        "......hhhh...cccccccccccccc.....",
        ".....hhhhhh..cccccccccccccc.....",
        "....cchhhhcc.pppppppppppppp.....",
        "....cchhhhcc.pppppppppppppp.....",
        "....cccccccc.pppppppppppppp.....",
        "....cccccccc.pppppppppppppp.....",
        "....cccccccc.pppppppppppppp.....",
        "....cccccccc.s.ssssssssss.s.....",
        "....ccccccccss.ssssssssss.ss....",
        "................................",
        "................................",
        "................................"
    ],
    "drag": [
        "................",
        "......bbbb......",
        ".....bbbbbb.....",
        ".....bhhhhb.....",
        ".....hheehh.....",
        ".....hhhhhh.....",
        "......hhhh......",
        "....cchhhhcc....",
        "....cchhhhcc....",
        "....cc.cc.cc....",
        "....cc.cc.cc....",
        "....c..cc..c....",
        ".......cc.......",
        "......cccc......",
        "......cccc......",
        ".....cccccc.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....p....p.....",
        ".....p....p.....",
        "....pp....pp....",
        "....p......p....",
        "....p......p....",
        "....p......p....",
        "....p......p....",
        "....s......s....",
        "....s......s....",
        "....s......s....",
        "................",
        "................",
        "................"
    ]
}

MOB_TEMPLATES = {
    "zombie_idle": [
        "................",
        "......ZZZZ......",
        ".....ZZZZZZ.....",
        ".....bzzzzb.....",
        ".....zzeeZZ.....",
        ".....zzzzzz.....",
        "......zzzz......",
        ".....zzzzzz.....",
        "....cczzzzcc....",
        "....cczzzzcc....",
        "....cccccccc....",
        "....cccccccc....",
        "....cccccccc....",
        "....cccccccc....",
        "....cccccccc....",
        "....cccccccc....",
        "....cccccccc....",
        ".....cccccc.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....p.pp.p.....",
        ".....Z.ZZ.Z.....",
        "....ZZ.ZZ.ZZ....",
        "....ZZ.ZZ.ZZ....",
        "................"
    ],
    "zombie_walk1": [
        "................",
        "......ZZZZ......",
        ".....ZZZZZZ.....",
        ".....bzzzzb.....",
        ".....zzeeZZ.....",
        ".....zzzzzz.....",
        "......zzzz......",
        ".....zzzzzz.....",
        "....cczzzzcc....",
        "....cczzzzcc....",
        "....c.cccc.c....",
        "....c.cccc.c....",
        "....c.cccc.c....",
        "....c.cccc.c....",
        "......cccc......",
        "......cccc......",
        "......cccc......",
        "......cccc......",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....p.pp.p.....",
        ".....p.pp.p.....",
        ".....p.pp.p.....",
        ".....p....p.....",
        "....pp....pp....",
        "....p......p....",
        "....p......p....",
        "....p......p....",
        "....Z......Z....",
        "....ZZ....ZZ....",
        "....ZZ....ZZ....",
        "................"
    ],
    "zombie_walk2": [
        "................",
        "......ZZZZ......",
        ".....ZZZZZZ.....",
        ".....bzzzzb.....",
        ".....zzeeZZ.....",
        ".....zzzzzz.....",
        "......zzzz......",
        ".....zzzzzz.....",
        "....cczzzzcc....",
        "....cczzzzcc....",
        "....cccccccc....",
        "....cccccccc....",
        "....cccccccc....",
        "....cccccccc....",
        "....cccccccc....",
        "....cccccccc....",
        "....cccccccc....",
        ".....cccccc.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....pppppp.....",
        ".....p.pp.p.....",
        ".....Z.ZZ.Z.....",
        "....ZZ.ZZ.ZZ....",
        "....ZZ.ZZ.ZZ....",
        "................"
    ],
    "creeper_idle": [
        "................",
        ".....gggggg.....",
        "....gggggggg....",
        "....gGkggkGg....",
        "....ggkkkkgg....",
        "....gggkkggg....",
        "....gggggggg....",
        ".....gggggg.....",
        ".....gggggg.....",
        ".....gggggg.....",
        ".....gggggg.....",
        ".....gggggg.....",
        ".....gggggg.....",
        ".....gggggg.....",
        ".....gggggg.....",
        ".....gggggg.....",
        ".....gggggg.....",
        ".....gggggg.....",
        ".....gggggg.....",
        ".....gggggg.....",
        ".....gggggg.....",
        ".....gggggg.....",
        "....gggggggg....",
        "....gggggggg....",
        "....gGg..gGg....",
        "....gGg..gGg....",
        "....G.G..G.G....",
        "....G.G..G.G....",
        "....g.g..g.g....",
        "....g.g..g.g....",
        "....G.G..G.G....",
        "................"
    ],
    "creeper_walk": [
        "................",
        ".....gggggg.....",
        "....gggggggg....",
        "....gGkggkGg....",
        "....ggkkkkgg....",
        "....gggkkggg....",
        "....gggggggg....",
        ".....gggggg.....",
        ".....gggggg.....",
        ".....gggggg.....",
        ".....gggggg.....",
        ".....gggggg.....",
        ".....gggggg.....",
        ".....gggggg.....",
        ".....gggggg.....",
        ".....gggggg.....",
        ".....gggggg.....",
        ".....gggggg.....",
        ".....gggggg.....",
        ".....gggggg.....",
        ".....gggggg.....",
        ".....gggggg.....",
        "....gggggggg....",
        "....gggggggg....",
        "....gG....gG....",
        "....gG....gG....",
        "....G......G....",
        "....G......G....",
        "....g......g....",
        "....g......g....",
        "....G......G....",
        "................"
    ],
    "villager_idle": [
        "................",
        "......hhhh......",
        ".....hhhhhh.....",
        ".....heeehh.....",
        ".....hbbbbh.....",
        ".....hbbbbh.....",
        "......hhhh......",
        ".....rrrrrr.....",
        "....rrrrrrrr....",
        "....rrrrrrrr....",
        "....rrRRRRrr....",
        "....rrRRRRrr....",
        "....rrRRRRrr....",
        "....rrRRRRrr....",
        "....rrRRRRrr....",
        "....rrRRRRrr....",
        "....rrRRRRrr....",
        "....rrrrrrrr....",
        "....rrrrrrrr....",
        "....rrrrrrrr....",
        "....rrrrrrrr....",
        "....rrrrrrrr....",
        "....rrrrrrrr....",
        "....rrrrrrrr....",
        "....rrrrrrrr....",
        "....rrrrrrrr....",
        "....rrrrrrrr....",
        "....r.rr.rr.r...",
        "....H.HH.HH.H...",
        "....H.HH.HH.H...",
        "....r.rr.rr.r...",
        "................"
    ],
    "wolf_idle": [
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        ".........w_ww_w.",
        ".........w_ww_w.",
        ".......w_ww_ww_w",
        ".......w_ww_ww_w",
        ".......w_ee_ee_w",
        "........w_ww_w..",
        ".....w_ww_ww_w..",
        "....w_w_cw_w_w..",
        "....w_w_cw_w_w..",
        "....w_ww_ww_w...",
        "....w_ww_ww_w...",
        "....w_ww_ww_w...",
        "....w_ww_ww_w...",
        "....w_ww_ww_w...",
        "....w_ww_ww_w...",
        ".....w_ww_w_w...",
        ".....w..w.w.w...",
        ".....w..w.w.w...",
        ".....w_dw_dw_d..",
        ".....w_dw_dw_d..",
        "................",
        "................"
    ],
    "wolf_sit": [
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        ".........w_ww_w.",
        ".........w_ww_w.",
        ".......w_ww_ww_w",
        ".......w_ee_ee_w",
        "........w_ww_w..",
        ".....w_ww_ww_w..",
        "....w_w_cw_w_w..",
        "....w_w_cw_w_w..",
        "....w_ww_ww_w...",
        "....w_ww_ww_w...",
        "....w_ww_ww_w...",
        "....w_ww_ww_w...",
        ".....w_ww_w.....",
        "......w_w_w.....",
        "......w_w_w.....",
        ".....w_dw_d.....",
        ".....w_dw_d.....",
        "................",
        "................",
        "................"
    ],
    "cow": [
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        ".....S..S.......",
        "....SSssSS......",
        "....SssSssS.....",
        "....SssSssS.....",
        "....SssSssS.....",
        ".....SssS.......",
        ".....ssss.......",
        "....ssssss......",
        "...ssssssss.....",
        "..ssssssssss....",
        "..ssssssssss....",
        "..ssssssssss....",
        "..ssssssssss....",
        "...ssssssss.....",
        "....s....s......",
        "....s....s......",
        "....s....s......",
        "....S....S......",
        "....S....S......",
        "................",
        "................",
        "................"
    ],
    "sheep": [
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        ".....wwww.......",
        "....wwwwww......",
        "....w.ww.w......",
        "....wwwwww......",
        ".....wwww.......",
        "....wwwwww......",
        "...wwwwwwww.....",
        "..wwwwwwwwww....",
        "..wwwwwwwwww....",
        "..wwwwwwwwww....",
        "..wwwwwwwwww....",
        "..wwwwwwwwww....",
        "...wwwwwwww.....",
        "....w....w......",
        "....w....w......",
        "....w....w......",
        "....w....w......",
        "....d....d......",
        "....d....d......",
        "................",
        "................",
        "................"
    ],
    "dragon": [
        "......k.........",
        ".....kkk........",
        "....kkkkk.......",
        "...kkkkkkk......",
        "..kkkkkkkkk.....",
        "...kkkkkkk......",
        "....kkkkk.......",
        ".....kkk........",
        "......k.........",
        ".....kkk........",
        "....kkkkk.......",
        "...kkkkkkk......",
        "..kkkkkkkkk.....",
        "...kkkkkkk......",
        "....kkkkk.......",
        ".....kkk........",
        "......k.........",
        ".....kkk........",
        "....kkkkk.......",
        "...kkkkkkk......",
        "..kkkkkkkkk.....",
        "...kkkkkkk......",
        "....kkkkk.......",
        ".....kkk........",
        "......k.........",
        ".....kkk........",
        "....kkkkk.......",
        "...kkkkkkk......",
        "..kkkkkkkkk.....",
        "....kkkkk.......",
        ".....kkk........",
        "......k........."
    ]
}

# ITEMS (16x16)
ITEM_TEMPLATES = {
    "wood_sword": [
        ".............w.",
        "............ww.",
        "...........ww..",
        "..........ww...",
        ".........ww....",
        "........ww.....",
        ".......ww......",
        "......ww.......",
        ".....ww........",
        "....ww.........",
        "...ww..........",
        "..ww...........",
        ".ww............",
        "wd.............",
        "d..............",
        "..............."
    ],
    "iron_sword": [
        ".............i.",
        "............ii.",
        "...........ii..",
        "..........ii...",
        ".........ii....",
        "........ii.....",
        ".......ii......",
        "......ii.......",
        ".....ii........",
        "....ii.........",
        "...ii..........",
        "..ii...........",
        ".ii............",
        "wd.............",
        "d..............",
        "..............."
    ],
    "diamond_sword": [
        ".............x.",
        "............xx.",
        "...........xx..",
        "..........xx...",
        ".........xx....",
        "........xx.....",
        ".......xx......",
        "......xx.......",
        ".....xx........",
        "....xx.........",
        "...xx..........",
        "..xx...........",
        ".xx............",
        "wd.............",
        "d..............",
        "..............."
    ],
    "wood_pickaxe": [
        "......wwwww....",
        "....wwwwwwwww..",
        "....ww.ww.ww...",
        ".......d.......",
        "......d........",
        "......d........",
        ".....d.........",
        ".....d.........",
        "....d..........",
        "....d..........",
        "...d...........",
        "...d...........",
        "..d............",
        "..d............",
        ".d.............",
        "..............."
    ],
    "iron_pickaxe": [
        "......iiiii....",
        "....iiiiiiiii..",
        "....ii.ii.ii...",
        ".......d.......",
        "......d........",
        "......d........",
        ".....d.........",
        ".....d.........",
        "....d..........",
        "....d..........",
        "...d...........",
        "...d...........",
        "..d............",
        "..d............",
        ".d.............",
        "..............."
    ],
    "diamond_pickaxe": [
        "......xxxxx....",
        "....xxxxxxxxx..",
        "....xx.xx.xx...",
        ".......d.......",
        "......d........",
        "......d........",
        ".....d.........",
        ".....d.........",
        "....d..........",
        "....d..........",
        "...d...........",
        "...d...........",
        "..d............",
        "..d............",
        ".d.............",
        "..............."
    ],
    "bread": [
        "...............",
        "......bbb......",
        "....bbbbbbb....",
        "...bbBBBBBbb...",
        "..bbBBBBBBBbb..",
        "..bBBBBBBBBBb..",
        "..bBBBBBBBBBb..",
        "..bbBBBBBBBbb..",
        "...bbBBBBBbb...",
        "....bbbbbbb....",
        "......bbb......",
        "...............",
        "...............",
        "...............",
        "...............",
        "..............."
    ],
    "potion": [
        "......iii......",
        "......iii......",
        ".....iiiii.....",
        ".....iiiii.....",
        "....iiiiiii....",
        "....irrrrri....",
        "...irrrrrrri...",
        "...irrrrrrri...",
        "...irrrrrrri...",
        "...irrrrrrri...",
        "...irrrrrrri...",
        "....irrrrri....",
        "....iiiiiii....",
        ".....iiiii.....",
        "......iii......",
        "..............."
    ],
    "bone": [
        "...............",
        "...oo.....oo...",
        "..oooo...oooo..",
        "..oooo...oooo..",
        "...oo.ooo.oo...",
        "......ooo......",
        "......ooo......",
        "......ooo......",
        "......ooo......",
        "......ooo......",
        "......ooo......",
        "...oo.ooo.oo...",
        "..oooo...oooo..",
        "..oooo...oooo..",
        "...oo.....oo...",
        "..............."
    ],
    "diamond": [
        "......xxx......",
        "....xxxxxxx....",
        "...xxxxxxxxx...",
        "..xxxxxxxxxxx..",
        "..xxxxxxxxxxx..",
        "..xxxxxxxxxxx..",
        "...xxxxxxxxx...",
        "....xxxxxxx....",
        "......xxx......",
        ".......x.......",
        "...............",
        "...............",
        "...............",
        "...............",
        "...............",
        "..............."
    ]
}

# Accessory: Santa Hat Overlay (16x16)
SANTA_HAT_TEMPLATE = [
    "......rrr.......",
    ".....rrrr.......",
    "....rrrrrr......",
    "....rrrrrrww....",
    "...rrrrrrrww....",
    "...rrrrrrrr.....",
    "..rrrrrrrrrr....",
    ".wwwwwwwwwwww...",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................"
]

# Cache of generated surfaces
_sprite_cache = {}

def get_sprite(category, name, facing_right=True, santa_hat=False):
    """
    Retrieves a compiled sprite surface. 
    Applies mirror flip if facing left.
    Applies Santa Hat overlay if santa_hat is True (only for humanoids).
    """
    cache_key = (category, name, facing_right, santa_hat)
    if cache_key in _sprite_cache:
        return _sprite_cache[cache_key]

    # Get templates and palettes
    template = None
    palette = PALETTES.get(category, {})

    if category == "blocks":
        template = BLOCK_TEMPLATES.get(name)
    elif category == "steve":
        template = STEVE_TEMPLATES.get(name)
    elif category == "mobs":
        template = MOB_TEMPLATES.get(name)
    elif category == "items":
        template = ITEM_TEMPLATES.get(name)

    if not template:
        # Fallback empty surface
        size = 32 if category in ["steve", "mobs"] else 16
        surf = pygame.Surface((size * SCALE, size * SCALE))
        surf.fill(COLOR_KEY)
        _sprite_cache[cache_key] = surf
        return surf

    h = len(template)
    w = len(template[0])
    
    # Parse template
    surf = pygame.Surface((w, h))
    surf.fill(COLOR_KEY)
    surf.set_colorkey(COLOR_KEY)

    for y in range(h):
        for x in range(w):
            char = template[y][x]
            if char in palette:
                color = palette[char]
                if color:
                    surf.set_at((x, y), color)

    # Apply Santa Hat if requested (only on head of humanoid sprites)
    if santa_hat and category in ["steve", "mobs"] and name != "sleep":
        hat_palette = PALETTES["steve"]
        # Draw Santa hat on top
        for y in range(len(SANTA_HAT_TEMPLATE)):
            for x in range(len(SANTA_HAT_TEMPLATE[0])):
                char = SANTA_HAT_TEMPLATE[y][x]
                if char in hat_palette:
                    color = hat_palette[char]
                    if color:
                        # Shift hat up slightly relative to Steve's head
                        # Steve's head starts at y=1, width of hat is 16
                        hx = x
                        hy = y - 6 # draw shifted up
                        if 0 <= hx < w and 0 <= hy < h:
                            surf.set_at((hx, hy), color)

    # Flip if facing left (only humanoids/mobs/items might face left)
    if not facing_right:
        surf = pygame.transform.flip(surf, True, False)

    # Scale up
    scaled_surf = pygame.transform.scale(surf, (w * SCALE, h * SCALE))
    scaled_surf.set_colorkey(COLOR_KEY)

    # Cache and return
    _sprite_cache[cache_key] = scaled_surf
    return scaled_surf

def get_block_sprite(name):
    return get_sprite("blocks", name)

def get_steve_sprite(state_name, facing_right=True, santa_hat=False):
    return get_sprite("steve", state_name, facing_right, santa_hat)

def get_mob_sprite(name, facing_right=True):
    return get_sprite("mobs", name, facing_right)

def get_item_sprite(name):
    return get_sprite("items", name)
