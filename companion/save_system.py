import json
import os
from companion.config import SAVE_FILENAME, DEFAULT_INVENTORY, DEFAULT_STATS

def get_save_path():
    # Save directly in the current working directory (workspace) for easy visibility/backup
    return SAVE_FILENAME

def load_game():
    """Loads save file or returns default state if file doesn't exist."""
    path = get_save_path()
    if not os.path.exists(path):
        return get_default_state()
        
    try:
        with open(path, "r") as f:
            state = json.load(f)
            
        # Ensure default structures exist to avoid key errors for legacy saves
        if "world" not in state:
            state["world"] = {"modified_blocks": {}, "structures": {}}
        if "structures" not in state["world"]:
            state["world"]["structures"] = {}
        if "modified_blocks" not in state["world"]:
            state["world"]["modified_blocks"] = {}
            
        # Merge missing default inventory keys
        if "inventory" in state:
            for k, v in DEFAULT_INVENTORY.items():
                if k not in state["inventory"]:
                    state["inventory"][k] = v
        else:
            state["inventory"] = DEFAULT_INVENTORY.copy()

        # Merge missing default statistics
        if "stats" in state:
            for k, v in DEFAULT_STATS.items():
                if k not in state["stats"]:
                    state["stats"][k] = v
        else:
            state["stats"] = DEFAULT_STATS.copy()

        return state
    except Exception as e:
        print(f"Error loading save file ({e}). Starting fresh.")
        return get_default_state()

def save_game(state):
    """Saves the state atomically using a temp file."""
    path = get_save_path()
    temp_path = path + ".tmp"
    try:
        with open(temp_path, "w") as f:
            json.dump(state, f, indent=4)
        
        # Atomically replace old file
        if os.path.exists(path):
            os.remove(path)
        os.rename(temp_path, path)
        return True
    except Exception as e:
        print(f"Error saving game ({e})")
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
        return False

def get_default_state():
    """Returns a completely fresh game state."""
    return {
        "version": "1.0",
        "day": 1,
        "time_of_day": 30.0,  # Start a little bit into the day
        "inventory": DEFAULT_INVENTORY.copy(),
        "stats": DEFAULT_STATS.copy(),
        "equipment": {
            "sword": "wood_sword",
            "pickaxe": "wood_pickaxe",
            "armor": "none"
        },
        "steve": {
            "x": 200.0,
            "y": 752.0,  # Fallback vertical ground position
            "health": 20,
            "hunger": 100,
            "level": 1,
            "xp": 0
        },
        "wolf": {
            "tamed": False,
            "sitting": False,
            "name": "Wolf",
            "health": 20
        },
        "world": {
            "modified_blocks": {},  # key: "x,y", value: "block_name" (e.g. "air", "stone")
            "structures": {}       # key: structure_name, value: bool
        }
    }
