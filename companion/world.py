import random
import datetime
import math
import pygame
from companion.config import SCALE, SCALED_TILE, DAY_DURATION, NIGHT_DURATION, COLOR_KEY
from companion.sprites import get_block_sprite, get_sprite
from companion.sound import play_sound

class World:
    def __init__(self, width, height, work_bottom, saved_world=None):
        self.width = width
        self.height = height
        self.work_bottom = work_bottom
        
        # Calculate columns based on width
        self.cols = width // SCALED_TILE
        self.rows = 3  # row 0 = Air/Structures, row 1 = Grass layer, row 2 = Stone layer
        
        # Grid dictionary: key (col, row), value block name
        self.grid = {}
        
        # Current time & day
        self.day = 1
        self.time_of_day = 0.0
        
        # Weather state: 'sunny', 'rain', 'snow', 'thunder'
        self.weather = "sunny"
        self.weather_timer = 300.0  # seconds until weather change
        self.weather_particles = []
        self.thunder_flash = 0
        
        # Seasons
        self.season = "normal"  # 'normal', 'christmas', 'halloween', 'diwali', 'new_year'
        
        # Saved structures and block overrides
        self.modified_blocks = {}
        self.structures = {}
        
        if saved_world:
            self.modified_blocks = saved_world.get("modified_blocks", {})
            self.structures = saved_world.get("structures", {})
            
        self.detect_real_season()
        self.generate_world()

    def detect_real_season(self):
        """Detects holidays based on current date, but can be overridden."""
        now = datetime.datetime.now()
        month = now.month
        day = now.day
        
        if month == 10 and day >= 24 or month == 11 and day <= 2:
            self.season = "halloween"
        elif month == 12 and day >= 15 or month == 1 and day <= 5:
            if month == 12 and day == 31 or month == 1 and day == 1:
                self.season = "new_year"
            else:
                self.season = "christmas"
        elif month == 11 and (10 <= day <= 20):  # Approximation for Diwali
            self.season = "diwali"
        else:
            self.season = "normal"

    def generate_world(self):
        """Generates the initial landscape columns."""
        self.grid.clear()
        
        # Build ground layers
        for col in range(self.cols):
            # Default layers
            # Row 2 (Bottom layer): Stone, with random Coal, Iron, Diamond ores
            r = random.random()
            if r < 0.03:
                bottom_block = "diamond_ore"
            elif r < 0.09:
                bottom_block = "iron_ore"
            elif r < 0.18:
                bottom_block = "coal_ore"
            else:
                bottom_block = "stone"
                
            self.grid[(col, 2)] = bottom_block
            
            # Row 1 (Top layer): Grass
            self.grid[(col, 1)] = "grass"
            
            # Row 0: Air
            self.grid[(col, 0)] = "air"

        # Apply saved modifications (overrides)
        for key_str, block in self.modified_blocks.items():
            try:
                col, row = map(int, key_str.split(","))
                if 0 <= col < self.cols and 0 <= row < 3:
                    self.grid[(col, row)] = block
            except Exception:
                pass

        # If it's Christmas season, put snow on top of grass
        if self.season == "christmas":
            # Add snow particles or snow cover blocks
            pass

        # Spawn initial trees if they don't overlap with saved structures
        # Trees typically spawn at intervals of 8-12 blocks
        # Let's seed them procedurally
        random.seed(12345)  # Seed for deterministic natural tree positions
        for col in range(3, self.cols - 3, 10):
            # Check if this area is modified
            if f"{col},1" not in self.modified_blocks and f"{col},0" not in self.modified_blocks:
                self.spawn_tree(col)
        # Restore random generator state
        random.seed()

    def spawn_tree(self, col):
        """Spawns an oak tree at column col. Leaf blocks sit on Row 0 and above."""
        # Row 1 must be grass or wood base, Row 0 is trunk
        self.grid[(col, 0)] = "wood_log"
        # We can dynamically place leaves above column col
        # In a 1D grid representation, we can just save it or render leaves relative to the trunk.
        # Let's make trunk go up 2 blocks.
        # Since our row grid is 3 rows deep, let's represent additional rows:
        # Row -1: Trunk top, Row -2: Leaves.
        # We can expand grid coordinates to negative rows!
        self.grid[(col, -1)] = "wood_log"
        self.grid[(col, -2)] = "leaves"
        self.grid[(col-1, -2)] = "leaves"
        self.grid[(col+1, -2)] = "leaves"
        self.grid[(col, -3)] = "leaves"

    def get_block(self, col, row):
        """Gets block at col, row. Returns 'air' if not defined."""
        return self.grid.get((col, row), "air")

    def set_block(self, col, row, block_name, save=True):
        """Sets a block in the grid and records it as modified."""
        self.grid[(col, row)] = block_name
        if save:
            key_str = f"{col},{row}"
            self.modified_blocks[key_str] = block_name

    def is_solid(self, col, row):
        """Checks if a block is solid (collidable)."""
        block = self.get_block(col, row)
        return block not in ["air", "leaves", "campfire", "portal", "wheat_farm"]

    def update(self, dt):
        """Updates the time of day, weather, and weather particles."""
        # Update day-night cycle
        self.time_of_day += dt
        cycle_len = DAY_DURATION + NIGHT_DURATION
        if self.time_of_day >= cycle_len:
            self.time_of_day = 0.0
            self.day += 1
            play_sound("levelup")  # Play a happy level up arpeggio for surviving a day!
            
        # Weather cycle
        self.weather_timer -= dt
        if self.weather_timer <= 0:
            # Change weather
            self.weather_timer = random.uniform(150, 400)
            # 60% sunny, 20% rain, 10% snow, 10% thunder
            r = random.random()
            if r < 0.60:
                self.weather = "sunny"
            elif r < 0.80:
                self.weather = "rain"
            elif r < 0.90:
                self.weather = "snow"
            else:
                self.weather = "thunder"
                play_sound("explode") # Thunder rumble on start

        # Seasons specific updates
        if self.season == "christmas" and self.weather == "sunny":
            # Force snow instead of rain in winter
            self.weather = "snow"

        # Update particles
        self.update_weather_particles(dt)
        
        # Thunder flashes
        if self.weather == "thunder" and random.random() < 0.005 and self.thunder_flash <= 0:
            self.thunder_flash = random.randint(3, 8)  # Number of frames to flash
            play_sound("explode")

        if self.thunder_flash > 0:
            self.thunder_flash -= 1

    def update_weather_particles(self, dt):
        """Spawns and moves rain/snow particles."""
        # Spawn particles
        if self.weather in ["rain", "thunder"]:
            # Spawn rain
            for _ in range(random.randint(1, 3)):
                self.weather_particles.append({
                    "x": random.uniform(0, self.width),
                    "y": 0,
                    "vx": -1.0,
                    "vy": random.uniform(8.0, 12.0),
                    "type": "rain"
                })
        elif self.weather == "snow":
            # Spawn snow
            for _ in range(random.randint(0, 2)):
                self.weather_particles.append({
                    "x": random.uniform(0, self.width),
                    "y": 0,
                    "vx": random.uniform(-0.5, 0.5),
                    "vy": random.uniform(1.5, 3.0),
                    "type": "snow"
                })

        # Update existing
        active_particles = []
        for p in self.weather_particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            
            # Check collision with ground/blocks
            col = int(p["x"] // SCALED_TILE)
            row1_y = self.work_bottom - 2 * SCALED_TILE
            row2_y = self.work_bottom - SCALED_TILE
            
            # Check collision with top solid block in column
            hit = False
            if 0 <= col < self.cols:
                # Find highest solid block
                for row in range(-3, 3):
                    if self.is_solid(col, row):
                        block_top_y = self.work_bottom - (3 - row) * SCALED_TILE
                        if p["y"] >= block_top_y:
                            hit = True
                            break
            
            if not hit and p["y"] < self.work_bottom and 0 <= p["x"] <= self.width:
                active_particles.append(p)
                
        self.weather_particles = active_particles

    def draw_sky_objects(self, surface):
        """Draws the moving Sun/Moon and Stars without blocking the screen."""
        cycle_len = DAY_DURATION + NIGHT_DURATION
        pct = self.time_of_day / cycle_len
        
        # Calculate Sun/Moon position in a low arc along the screen width
        # This sits just above the landscape, keeping it visible but clean.
        theta = pct * 2.0 * math.pi  # 0 to 2pi
        
        # Arc path: center at screen width / 2
        center_x = self.width / 2
        radius_x = self.width / 2 - 50
        radius_y = 120  # Keep it low so it doesn't float too high up the desktop
        
        # Sun position (day is first half of cycle)
        # Shift angle by pi/2 so it rises on left and sets on right
        sun_angle = theta - math.pi / 2
        sun_x = center_x + radius_x * math.cos(sun_angle)
        sun_y = (self.work_bottom - 150) + radius_y * math.sin(sun_angle)
        
        # Moon position (opposite to sun)
        moon_angle = sun_angle + math.pi
        moon_x = center_x + radius_x * math.cos(moon_angle)
        moon_y = (self.work_bottom - 150) + radius_y * math.sin(moon_angle)

        is_night = self.is_night()
        
        # Draw Sun (if above ground)
        if sun_y < self.work_bottom:
            # Draw golden pixel sun
            pygame.draw.rect(surface, (255, 200, 0), (int(sun_x) - 12, int(sun_y) - 12, 24, 24))
            pygame.draw.rect(surface, (255, 230, 100), (int(sun_x) - 8, int(sun_y) - 8, 16, 16))
            
        # Draw Moon (if above ground)
        if moon_y < self.work_bottom:
            # Draw white pixel moon
            pygame.draw.rect(surface, (220, 220, 240), (int(moon_x) - 10, int(moon_y) - 10, 20, 20))
            pygame.draw.rect(surface, (170, 170, 190), (int(moon_x) - 6, int(moon_y) - 6, 12, 12))
            
        # Draw Diwali Lanterns or decorations if Diwali Season
        if self.season == "diwali":
            # Draw hanging lanterns every 150 pixels
            for lx in range(80, self.width, 160):
                ly = self.work_bottom - 160
                # Draw small string
                pygame.draw.line(surface, (80, 80, 80), (lx, ly), (lx, ly + 20), 2)
                # Lantern body
                pygame.draw.rect(surface, (237, 28, 36), (lx - 6, ly + 20, 12, 14)) # Red border
                # Fire glow
                pygame.draw.rect(surface, (255, 201, 14), (lx - 3, ly + 23, 6, 8)) # Yellow core

    def draw_landscape(self, surface):
        """Draws all the blocks of the world grid onto the surface."""
        # Determine coordinate positions
        for (col, row), block in self.grid.items():
            if block == "air":
                continue
                
            x = col * SCALED_TILE
            # row 2 is bottom, row 1 is top, row 0 is structure base
            # Row 2 top is work_bottom - SCALED_TILE, Row 1 top is work_bottom - 2*SCALED_TILE
            # Row 0 top is work_bottom - 3*SCALED_TILE
            y = self.work_bottom - (3 - row) * SCALED_TILE
            
            # Don't draw if offscreen
            if x < -SCALED_TILE or x > self.width:
                continue

            # Draw block
            if block == "grass":
                surf = get_block_sprite("grass")
            elif block == "dirt":
                surf = get_block_sprite("dirt")
            elif block == "stone":
                surf = get_block_sprite("stone")
            elif block == "coal_ore":
                surf = get_block_sprite("coal_ore")
            elif block == "iron_ore":
                surf = get_block_sprite("iron_ore")
            elif block == "diamond_ore":
                surf = get_block_sprite("diamond_ore")
            elif block == "wood_log":
                surf = get_block_sprite("wood_log_side" if row == 0 or row == -1 else "wood_log")
            elif block == "leaves":
                surf = get_block_sprite("leaves")
            elif block == "planks":
                surf = get_block_sprite("planks")
            elif block == "crafting_table":
                surf = get_block_sprite("crafting_table")
            elif block == "furnace":
                surf = get_block_sprite("furnace")
            elif block == "chest":
                surf = get_block_sprite("chest")
            elif block == "portal":
                surf = get_block_sprite("portal")
            elif block == "campfire":
                surf = get_block_sprite("campfire")
            else:
                continue

            surface.blit(surf, (x, y))

    def draw_weather(self, surface):
        """Draws falling rain/snow particles."""
        for p in self.weather_particles:
            if p["type"] == "rain":
                pygame.draw.line(surface, (100, 150, 255), (p["x"], p["y"]), (p["x"] - 1, p["y"] + 6), 2)
            elif p["type"] == "snow":
                pygame.draw.circle(surface, (255, 255, 255), (int(p["x"]), int(p["y"])), 2)

        # Draw storm screen flash
        if self.thunder_flash > 0:
            flash_surface = pygame.Surface((self.width, self.height))
            flash_surface.fill((255, 255, 255))
            flash_surface.set_alpha(100) # Semi-transparent flash overlay
            surface.blit(flash_surface, (0, 0))

    def is_night(self):
        return self.time_of_day >= DAY_DURATION

    def get_sky_tint(self):
        """Returns the overlay color to represent day/night/weather mood."""
        # Calculate tint opacity
        is_night = self.is_night()
        
        # Transition duration (15 seconds)
        transition = 15.0
        
        # Default day tint (completely transparent)
        tint = (0, 0, 0, 0)
        
        if is_night:
            # Night is active
            time_in_night = self.time_of_day - DAY_DURATION
            if time_in_night < transition:
                # Sunset transition
                alpha = int((time_in_night / transition) * 110)
            elif self.time_of_day > (DAY_DURATION + NIGHT_DURATION - transition):
                # Sunrise transition
                time_to_day = (DAY_DURATION + NIGHT_DURATION) - self.time_of_day
                alpha = int((time_to_day / transition) * 110)
            else:
                # Full night
                alpha = 110
            # Dark navy night tint
            tint = (10, 10, 30, alpha)
        else:
            # Day is active
            if self.time_of_day < transition:
                # Morning sunrise fading out
                alpha = int(((transition - self.time_of_day) / transition) * 40)
                tint = (230, 120, 50, alpha)  # Warm morning orange glow
            
        # Weather adjustments (adds grey rainy overlay)
        if self.weather in ["rain", "thunder"]:
            # Mix in grey storm clouds
            tint_alpha = max(tint[3] if len(tint) > 3 else 0, 80)
            tint = (50, 50, 60, tint_alpha)
            
        return tint
