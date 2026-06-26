import pygame
import win32gui
import win32con
import win32api
import ctypes
import random
import time
import sys
import os

# Create folders if not exists
os.makedirs("companion", exist_ok=True)

from companion.config import SCALE, SCALED_TILE, COLOR_KEY, DAY_DURATION, NIGHT_DURATION
from companion.sprites import get_sprite, get_block_sprite, get_steve_sprite
from companion.sound import init_sounds, play_sound
from companion.save_system import load_game, save_game, get_default_state
from companion.world import World
from companion.entities import Steve, Zombie, Creeper, Wolf, Villager, XPOrb

# Structure RECT for ctypes SystemParametersInfo
class RECT(ctypes.Structure):
    _fields_ = [
        ('left', ctypes.c_long),
        ('top', ctypes.c_long),
        ('right', ctypes.c_long),
        ('bottom', ctypes.c_long)
    ]

def get_desktop_work_area():
    """Retrieves work area exclusion bounds of bottom taskbar."""
    rect = RECT()
    ctypes.windll.user32.SystemParametersInfoW(48, 0, ctypes.byref(rect), 0)
    return rect.left, rect.top, rect.right, rect.bottom

def configure_overlay_window(title):
    """Sets window to transparent, click-through, and always on top."""
    hwnd = win32gui.FindWindow(None, title)
    if not hwnd:
        return None

    # Retrieve initial style
    styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    
    # Apply layered, transparent, toolwindow (no taskbar icon) styles
    overlay_styles = styles | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TOOLWINDOW
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, overlay_styles)
    
    # Set to always on top
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, 
                          win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)
    
    # Chromakey colorkey (magenta is transparent)
    win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(255, 0, 255), 0, win32con.LWA_COLORKEY)
    
    return hwnd

def toggle_window_click_through(hwnd, make_click_through):
    """Enables or disables click-through dynamically based on mouse hover state."""
    if not hwnd:
        return
    try:
        styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        if make_click_through:
            new_styles = styles | win32con.WS_EX_TRANSPARENT
        else:
            new_styles = styles & ~win32con.WS_EX_TRANSPARENT
        
        # Apply style only if changed
        if styles != new_styles:
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, new_styles)
    except Exception as e:
        print(f"Error toggling window click-through: {e}")

def main():
    # 1. Initialize Pygame & Audio
    pygame.init()
    init_sounds()
    
    # 2. Get Monitor bounds
    screen_w = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    screen_h = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
    
    # Get usable area (excluding bottom taskbar)
    work_left, work_top, work_right, work_bottom = get_desktop_work_area()
    print(f"Desktop Work Bounds: {work_left}, {work_top} to {work_right}, {work_bottom}")

    # Set title and open window covering full monitor
    title = "Steve AI Desktop Companion"
    pygame.display.set_caption(title)
    screen = pygame.display.set_mode((screen_w, screen_h), pygame.NOFRAME)
    
    # 3. Configure windows flags for transparency and click-through
    hwnd = configure_overlay_window(title)
    if not hwnd:
        print("Error: Could not locate overlay window handle.")
        sys.exit(1)

    # 4. Load save game state
    save_state = load_game()
    
    # 5. Initialize World and Entities
    world = World(screen_w, screen_h, work_bottom, save_state.get("world"))
    
    # Force load current time/day
    world.day = save_state.get("day", 1)
    world.time_of_day = save_state.get("time_of_day", 30.0)
    
    # Initialize Steve
    steve = Steve(200.0, work_bottom - 2 * SCALED_TILE, save_state)
    
    # Manage active entity lists
    entities = [steve]
    
    # Add Wolf if saved as tamed, or 30% chance to spawn a wild one on first start
    wolf_data = save_state.get("wolf", {})
    if wolf_data.get("tamed", False) or random.random() < 0.30:
        entities.append(Wolf(300, work_bottom - 2 * SCALED_TILE, save_state))
        
    # Spawner timers
    mob_spawn_timer = 20.0  # check mob spawn every 20 seconds
    save_timer = 60.0       # auto-save every 60 seconds
    
    # Particle and XP lists
    particles = []
    xp_orbs = []
    
    # Setup GUI
    from companion.gui import GUI
    gui = GUI(screen_w, screen_h, work_bottom)
    
    # Track drag state
    dragging_steve = False
    drag_offset_x = 0
    drag_offset_y = 0
    
    # Focus control
    is_currently_click_through = True
    
    # Run loop parameters
    clock = pygame.time.Clock()
    running = True
    
    play_sound("tame")  # Happy startup chime
    steve.say("Steve Companion active! Hello!", 4.0)

    # Main companion execution loop
    while running:
        # FPS capped at 30 to consume minimal CPU and GPU resources (~40MB RAM)
        dt = clock.tick(30) / 1000.0  
        dt_multiplier = dt * 60.0  # multiplier standardized for 60 FPS update speeds
        
        # Retrieve mouse position
        mx, my = pygame.mouse.get_pos()
        
        # 1. Focus Detection: check if cursor overlaps hoverable components
        is_hovering_interactive = False
        
        # Check active UI panels
        for rect in gui.get_interactive_rects():
            if rect.collidepoint(mx, my):
                is_hovering_interactive = True
                break
                
        # Check Steve hitbox (clickable to drag, feed, pet)
        if not is_hovering_interactive:
            steve_rect = steve.get_rect()
            if steve_rect.collidepoint(mx, my):
                is_hovering_interactive = True
                
        # Check Wolf hitbox (clickable to tame/sit)
        if not is_hovering_interactive:
            for e in entities:
                if isinstance(e, Wolf):
                    if e.get_rect().collidepoint(mx, my):
                        is_hovering_interactive = True
                        break

        # Toggle Windows window click-through state dynamically
        if is_hovering_interactive and is_currently_click_through:
            toggle_window_click_through(hwnd, False)
            is_currently_click_through = False
        elif not is_hovering_interactive and not is_currently_click_through and not dragging_steve:
            toggle_window_click_through(hwnd, True)
            is_currently_click_through = True

        # 2. Event polling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left Click
                    # Let GUI handle clicks first
                    if not gui.handle_click(event.pos, steve, world, entities):
                        # Check interaction with Wolf
                        interacted_mob = False
                        for e in entities:
                            if isinstance(e, Wolf) and e.get_rect().collidepoint(event.pos):
                                if e.interact_tame(steve, particles):
                                    interacted_mob = True
                                    break
                        
                        # Check interaction with Steve
                        if not interacted_mob and steve.get_rect().collidepoint(event.pos):
                            dragging_steve = True
                            steve.state = "drag"
                            steve.vx = 0
                            steve.vy = 0
                            drag_offset_x = steve.x - event.pos[0]
                            drag_offset_y = steve.y - event.pos[1]
                            play_sound("dig")
                            steve.say(random.choice(["Hey! Put me down!", "Whoa!", "Let me go!"]), 1.5)
                            
                elif event.button == 3:  # Right Click
                    # Open custom context menu at click location
                    gui.open_menu(event.pos)
                    
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if dragging_steve:
                        dragging_steve = False
                        steve.state = "wander"
                        steve.state_timer = 1.0
                        steve.say("Thanks!", 1.5)
                        # Spawn love hearts on release!
                        for _ in range(5):
                            particles.append(TextParticle(steve.x + 10, steve.y - 10, "<3", (240, 50, 80), 1.5))
                            
        # Handle dragging movement
        if dragging_steve:
            steve.x = mx + drag_offset_x
            steve.y = my + drag_offset_y
            # Clamp on screen
            steve.x = max(0, min(screen_w - steve.width, steve.x))
            steve.y = max(0, min(screen_h - steve.height, steve.y))

        # Update GUI hover state
        gui.update((mx, my))

        # 3. Environment & World Update
        world.update(dt)
        
        # Mobs and structures spawning logic (at night)
        if world.is_night():
            mob_spawn_timer -= dt
            if mob_spawn_timer <= 0:
                mob_spawn_timer = random.uniform(25.0, 45.0)
                # Count current hostile mobs
                hostile_count = sum(1 for e in entities if isinstance(e, (Zombie, Creeper)))
                if hostile_count < 2:  # max 2 hostile mobs at a time
                    # Spawn zombie or creeper at screen edges
                    mob_class = random.choice([Zombie, Creeper])
                    spawn_x = random.choice([10.0, float(screen_w - 50)])
                    entities.append(mob_class(spawn_x, work_bottom - 2 * SCALED_TILE))
        else:
            # Day time: spawn villager occasionally if house is built
            if world.structures.get("house", False):
                has_villager = any(isinstance(e, Villager) for e in entities)
                if not has_villager and random.random() < 0.001:  # slow spawn
                    entities.append(Villager(20 * SCALED_TILE, work_bottom - 2 * SCALED_TILE))

        # 4. Entities Update
        # Separate update loops to pass full contexts
        active_entities = []
        for e in entities:
            if e.health <= 0:
                # Spawn death smoke
                for _ in range(8):
                    particles.append(Particle(e.x + 16, e.y + 32, random.uniform(-2,2), random.uniform(-2,2), (100,100,100), 0.5))
                
                # Spawn XP orbs if hostile killed
                if isinstance(e, (Zombie, Creeper)):
                    play_sound("tame")
                    steve.stats["zombies_killed"] = steve.stats.get("zombies_killed", 0) + 1
                    for _ in range(random.randint(3, 6)):
                        xp_orbs.append(XPOrb(e.x + 16, e.y + 16, 20))
                continue
                
            # Class specific updates
            if isinstance(e, Steve):
                e.update(world, entities, particles, dt, dt_multiplier)
            elif isinstance(e, Zombie):
                e.update(world, steve, particles, dt, dt_multiplier)
            elif isinstance(e, Creeper):
                e.update(world, steve, entities, particles, dt, dt_multiplier)
            elif isinstance(e, Wolf):
                e.update(world, steve, entities, particles, dt, dt_multiplier)
            elif isinstance(e, Villager):
                e.update(world, steve, particles, dt, dt_multiplier)
                
            active_entities.append(e)
        entities = active_entities

        # Update particles
        particles = [p for p in particles if p.update(dt)]
        
        # Update XP Orbs
        xp_orbs = [orb for orb in xp_orbs if orb.update(steve, world, dt)]

        # 5. Periodic Auto-Save
        save_timer -= dt
        if save_timer <= 0:
            save_timer = 60.0
            # Sync structures
            save_state = {
                "version": "1.0",
                "day": world.day,
                "time_of_day": world.time_of_day,
                "inventory": steve.inventory,
                "stats": steve.stats,
                "equipment": steve.equipment,
                "steve": {
                    "x": steve.x,
                    "y": steve.y,
                    "health": steve.health,
                    "hunger": steve.hunger,
                    "level": steve.level,
                    "xp": steve.xp
                },
                "wolf": {
                    "tamed": any(e.tamed for e in entities if isinstance(e, Wolf)),
                    "sitting": any(e.sitting for e in entities if isinstance(e, Wolf)),
                    "health": next((e.health for e in entities if isinstance(e, Wolf)), 20)
                },
                "world": {
                    "modified_blocks": world.modified_blocks,
                    "structures": world.structures
                }
            }
            save_game(save_state)
            print("Auto-save completed.")

        # 6. Render
        # Clear with chromakey colorkey magenta to make window transparent
        screen.fill(COLOR_KEY)
        
        # Render Sun/Moon sky arc
        world.draw_sky_objects(screen)
        
        # Calculate shade factor based on day/night cycle to tint blocks & entities
        shade_factor = 1.0
        if world.is_night():
            # Dark shade at night
            shade_factor = 0.45
            # Draw tiny stars in sky arc area
            random.seed(9876)  # fixed stars positions
            for _ in range(15):
                sx = random.randint(50, screen_w - 50)
                sy = random.randint(work_bottom - 240, work_bottom - 130)
                # blink
                if (pygame.time.get_ticks() + sx) % 1000 < 500:
                    pygame.draw.rect(screen, COLOR_WHITE, (sx, sy, 2, 2))
            random.seed()
        elif world.weather in ["rain", "thunder"]:
            shade_factor = 0.75  # slightly darker on rainy days
            
        # Create shaded drawing buffer for blocks and entities
        draw_buffer = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        draw_buffer.fill((0, 0, 0, 0))
        
        # Draw world terrain onto buffer
        world.draw_landscape(draw_buffer)
        
        # Draw entities onto buffer
        for e in entities:
            e.draw(draw_buffer)
            
        # Draw XP Orbs onto buffer
        for orb in xp_orbs:
            orb.draw(draw_buffer)
            
        # Draw particles onto buffer
        for p in particles:
            p.draw(draw_buffer)

        # Apply shade multiplier (day/night lighting tint) to the buffer
        if shade_factor < 0.95:
            mult_val = int(255 * shade_factor)
            draw_buffer.fill((mult_val, mult_val, mult_val, 255), special_flags=pygame.BLEND_RGBA_MULT)
            
        # Blit buffer to screen
        screen.blit(draw_buffer, (0, 0))
        
        # Render speech bubbles (do not shade, text must remain readable!)
        if steve.speech_text:
            gui.draw_speech_bubble(screen, steve.speech_text, steve.x, steve.y, screen_w)
            
        for e in entities:
            if not isinstance(e, Steve) and hasattr(e, "fuse_timer") and e.is_fusing:
                gui.draw_speech_bubble(screen, "OH NO!! SSSssss...", e.x, e.y, screen_w)
            elif isinstance(e, Wolf) and e.tamed and e.sitting:
                if random.random() < 0.005:  # occasional bark/sit indicator
                    gui.draw_speech_bubble(screen, "Woof!", e.x, e.y, screen_w)

        # Draw weather particles directly (drawn on top, unshaded)
        world.draw_weather(screen)
        
        # Draw HUD UI windows directly (unshaded)
        gui.draw(screen, steve, world)
        
        # Update display
        pygame.display.flip()
        
    # 7. Exit save state execution
    print("Exiting companion. Saving final state...")
    save_state = {
        "version": "1.0",
        "day": world.day,
        "time_of_day": world.time_of_day,
        "inventory": steve.inventory,
        "stats": steve.stats,
        "equipment": steve.equipment,
        "steve": {
            "x": steve.x,
            "y": steve.y,
            "health": steve.health,
            "hunger": steve.hunger,
            "level": steve.level,
            "xp": steve.xp
        },
        "wolf": {
            "tamed": any(e.tamed for e in entities if isinstance(e, Wolf)),
            "sitting": any(e.sitting for e in entities if isinstance(e, Wolf)),
            "health": next((e.health for e in entities if isinstance(e, Wolf)), 20)
        },
        "world": {
            "modified_blocks": world.modified_blocks,
            "structures": world.structures
        }
    }
    save_game(save_state)
    pygame.quit()
    sys.exit(0)

# Supporting textual particle class definition
class TextParticle:
    def __init__(self, x, y, text, color, duration):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.max_life = duration
        self.life = duration
        self.font = pygame.font.SysFont("Courier New", 14, bold=True)

    def update(self, dt):
        self.y -= 1.0
        self.life -= dt
        return self.life > 0

    def draw(self, surface):
        lbl = self.font.render(self.text, False, self.color)
        surface.blit(lbl, (int(self.x), int(self.y)))

if __name__ == "__main__":
    main()
