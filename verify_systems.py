import pygame
import sys
import os

# Set window dummy environment to initialize pygame headless for tests
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

def run_tests():
    print("=== RUNNING SYSTEM VERIFICATION TESTS ===")
    
    # 1. Config Check
    try:
        from companion.config import TILE_SIZE, SCALE, DEFAULT_INVENTORY
        print(f"[-] Config imported. Tile size: {TILE_SIZE}, Scale: {SCALE}")
        assert TILE_SIZE == 16
        assert SCALE == 2
        assert "bread" in DEFAULT_INVENTORY
        print("[+] Config tests passed!")
    except Exception as e:
        print(f"[X] Config test failed: {e}")
        return False

    # 2. Sprites Check
    try:
        pygame.init()
        from companion.sprites import get_block_sprite, get_steve_sprite, get_mob_sprite, get_item_sprite
        # Retrieve random blocks
        g_surf = get_block_sprite("grass")
        s_surf = get_steve_sprite("idle")
        z_surf = get_mob_sprite("zombie_idle")
        i_surf = get_item_sprite("iron_sword")
        
        print(f"[-] Sprites compiled. Grass surface size: {g_surf.get_size()}")
        assert g_surf.get_width() == 32  # 16px * 2 scale = 32
        assert s_surf.get_height() == 64  # 32px * 2 scale = 64
        print("[+] Sprites tests passed!")
    except Exception as e:
        print(f"[X] Sprites test failed: {e}")
        return False

    # 3. Sound Check
    try:
        from companion.sound import init_sounds, play_sound, is_muted
        init_sounds()
        play_sound("levelup")
        print("[-] Sound initialized and levelup played without crashes.")
        print("[+] Sound tests passed!")
    except Exception as e:
        print(f"[X] Sound test failed: {e}")
        return False

    # 4. Save/Load Check
    try:
        from companion.save_system import load_game, save_game, get_default_state
        state = get_default_state()
        state["steve"]["health"] = 15
        state["inventory"]["wood"] = 42
        
        # Save mock state
        save_game(state)
        print("[-] Mock state saved successfully.")
        
        # Load state
        loaded_state = load_game()
        print(f"[-] State loaded. Loaded health: {loaded_state['steve']['health']}, Loaded wood: {loaded_state['inventory']['wood']}")
        assert loaded_state["steve"]["health"] == 15
        assert loaded_state["inventory"]["wood"] == 42
        
        # Clean up mock file
        if os.path.exists("steve_save.json"):
            os.remove("steve_save.json")
            print("[-] Save file cleaned up.")
            
        print("[+] Save system tests passed!")
    except Exception as e:
        print(f"[X] Save system test failed: {e}")
        return False

    # 5. World Logic Check
    try:
        from companion.world import World
        # Create a mock world of width 1000, height 500, taskbar 450
        world = World(1000, 500, 450)
        print(f"[-] World generated. Cols: {world.cols}, Rows: {world.rows}")
        
        # Check basic properties
        assert world.cols == 1000 // 32
        assert world.is_solid(2, 1)  # Grass layer is solid
        assert not world.is_solid(2, 0)  # Air row above grass is not solid
        
        # Update world time
        world.update(1.0)
        print(f"[-] World updated time of day: {world.time_of_day:.2f}")
        
        print("[+] World tests passed!")
    except Exception as e:
        print(f"[X] World test failed: {e}")
        return False

    pygame.quit()
    print("=== ALL SYSTEM TESTS COMPLETED SUCCESSFULLY! ===")
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
