import math
import random
import datetime
import pygame
from companion.config import SCALE, SCALED_TILE, WALK_SPEED, RUN_SPEED, GRAVITY, JUMP_FORCE, COLOR_KEY
from companion.sprites import get_steve_sprite, get_mob_sprite, get_item_sprite
from companion.sound import play_sound

class Entity:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.width = width
        self.height = height
        
        self.gravity = GRAVITY
        self.on_ground = False
        self.facing_right = True
        self.health = 20
        self.max_health = 20

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def update_physics(self, world, dt_multiplier):
        """Applies gravity and AABB collision resolution on the world grid."""
        # Gravity
        if not self.on_ground:
            self.vy += self.gravity * dt_multiplier
            if self.vy > 12:  # Terminal velocity
                self.vy = 12
                
        # Move Y
        self.y += self.vy * dt_multiplier
        self.on_ground = False
        
        # Check Y collision
        rect = self.get_rect()
        start_col = int(self.x // SCALED_TILE) - 1
        end_col = int((self.x + self.width) // SCALED_TILE) + 1
        
        for col in range(start_col, end_col + 1):
            for row in range(-4, 3):
                if world.is_solid(col, row):
                    block_y = world.work_bottom - (3 - row) * SCALED_TILE
                    block_rect = pygame.Rect(col * SCALED_TILE, block_y, SCALED_TILE, SCALED_TILE)
                    if rect.colliderect(block_rect):
                        if self.vy > 0:  # Falling down
                            self.y = block_rect.top - self.height
                            self.vy = 0
                            self.on_ground = True
                        elif self.vy < 0:  # Heading up
                            self.y = block_rect.bottom
                            self.vy = 0
                        rect.y = int(self.y)

        # Move X
        self.x += self.vx * dt_multiplier
        
        # Check X boundary constraints
        if self.x < 0:
            self.x = 0
            self.vx = 0
        elif self.x > world.width - self.width:
            self.x = world.width - self.width
            self.vx = 0
            
        # Check X collision
        rect = self.get_rect()
        start_col = int(self.x // SCALED_TILE) - 1
        end_col = int((self.x + self.width) // SCALED_TILE) + 1
        
        for col in range(start_col, end_col + 1):
            for row in range(-4, 3):
                if world.is_solid(col, row):
                    block_y = world.work_bottom - (3 - row) * SCALED_TILE
                    block_rect = pygame.Rect(col * SCALED_TILE, block_y, SCALED_TILE, SCALED_TILE)
                    if rect.colliderect(block_rect):
                        if self.vx > 0:  # Moving right
                            self.x = block_rect.left - self.width
                            self.vx = 0
                        elif self.vx < 0:  # Moving left
                            self.x = block_rect.right
                            self.vx = 0
                        rect.x = int(self.x)

class Steve(Entity):
    def __init__(self, x, y, save_state=None):
        # Steve is 16x32 sprite, scaled by 2 => 32x64 pixels
        super().__init__(x, y, 32 * SCALE, 64 * SCALE)
        
        self.state = "wander"  # wander, gather_wood, mine_stone, build, combat, sleep, eat, drag
        self.state_timer = 3.0
        
        # Needs
        self.hunger = 100
        self.level = 1
        self.xp = 0
        
        # Inventory & stats
        self.inventory = {}
        self.stats = {}
        self.equipment = {"sword": "wood_sword", "pickaxe": "wood_pickaxe", "armor": "none"}
        
        # Targeting
        self.target_x = x
        self.target_entity = None
        self.mining_col = None
        self.mining_row = None
        self.mining_progress = 0.0
        
        # Speech bubbles
        self.speech_text = None
        self.speech_timer = 0.0
        
        # Build queue
        self.build_col = None
        self.build_step = 0
        self.build_timer = 0.0
        
        # Restore saved states
        if save_state:
            self.inventory = save_state.get("inventory", {})
            self.stats = save_state.get("stats", {})
            self.equipment = save_state.get("equipment", self.equipment)
            
            steve_data = save_state.get("steve", {})
            self.x = steve_data.get("x", self.x)
            self.y = steve_data.get("y", self.y)
            self.health = steve_data.get("health", self.health)
            self.hunger = steve_data.get("hunger", self.hunger)
            self.level = steve_data.get("level", self.level)
            self.xp = steve_data.get("xp", self.xp)

    def say(self, text, duration=3.0):
        self.speech_text = text
        self.speech_timer = duration

    def take_damage(self, amount, knockback_vx=0):
        self.health = max(0, self.health - amount)
        self.vy = -3.0  # slight jump on hurt
        self.vx = knockback_vx
        self.on_ground = False
        play_sound("hit")
        self.say("Ouch!", 1.5)
        
        # Track stat
        if self.health <= 0:
            self.say("I died! Respawning...", 4.0)
            self.respawn()

    def respawn(self):
        self.health = 20
        self.hunger = 100
        self.x = 200.0
        self.y = 500.0
        self.vx = 0
        self.vy = 0
        self.state = "wander"
        # Deduct some XP
        self.xp = max(0, self.xp - 50)

    def update(self, world, entities, particles, dt, dt_multiplier):
        # Update physics (if not dragged)
        if self.state != "drag":
            self.update_physics(world, dt_multiplier)
        else:
            self.vx = 0
            self.vy = 0
            
        # Update timers
        if self.speech_timer > 0:
            self.speech_timer -= dt
            if self.speech_timer <= 0:
                self.speech_text = None
                
        # Drop hunger slowly
        if self.state != "sleep":
            self.hunger = max(0.0, self.hunger - 0.015 * dt_multiplier)
            
        # Health regeneration
        if self.hunger > 80 and self.health < 20:
            self.health = min(20, self.health + 0.01 * dt_multiplier)
            
        # Check needs and state changes
        if self.state != "drag":
            self.manage_needs_and_ai(world, entities, particles, dt, dt_multiplier)

    def manage_needs_and_ai(self, world, entities, particles, dt, dt_multiplier):
        # 1. Check Hungry
        if self.hunger < 30 and self.state not in ["eat", "combat"]:
            if self.inventory.get("bread", 0) > 0:
                self.state = "eat"
                self.state_timer = 2.0
                play_sound("eat")
                self.say("Hungry. Eating bread...", 2.0)
            else:
                self.say("Hungry! Need food.", 2.5)

        # 2. Check low health -> Potion
        if self.health < 8 and self.inventory.get("potion", 0) > 0 and self.state != "combat":
            self.inventory["potion"] -= 1
            self.health = 20
            self.say("Drinking potion...", 2.0)
            play_sound("tame")
            
        # 3. Check Monsters nearby -> Combat
        if self.state != "combat":
            for e in entities:
                if isinstance(e, (Zombie, Creeper)) and abs(e.x - self.x) < 200:
                    self.state = "combat"
                    self.target_entity = e
                    self.say("Enemy spotted!", 2.0)
                    break

        # STATE MACHINE ACTIONS
        if self.state == "eat":
            self.vx = 0
            self.state_timer -= dt
            # Spawn eating particles (crunches/brown crumbs)
            if random.random() < 0.2:
                particles.append(Particle(self.x + self.width/2, self.y + 20, random.uniform(-1,1), random.uniform(-1,0), (134,96,67), 0.4))
            if self.state_timer <= 0:
                self.inventory["bread"] = max(0, self.inventory.get("bread", 0) - 1)
                self.hunger = min(100, self.hunger + 40)
                self.state = "wander"
                self.state_timer = 3.0

        elif self.state == "combat":
            if not self.target_entity or self.target_entity.health <= 0:
                self.state = "wander"
                self.target_entity = None
                self.vx = 0
                return

            dist_x = self.target_entity.x - self.x
            self.facing_right = dist_x > 0
            
            # Hit range
            hit_range = 45 if not isinstance(self.target_entity, Creeper) else 35
            
            if isinstance(self.target_entity, Creeper) and self.target_entity.fuse_timer > 0.4:
                # Kiting creeper: run away if it is about to explode!
                self.say("Creepers again?! RUN!", 1.0)
                self.vx = -RUN_SPEED if dist_x > 0 else RUN_SPEED
                # Attempt to jump over obstacles while fleeing
                if self.vx != 0 and self.on_ground and self.is_obstacle_ahead(world):
                    self.vy = JUMP_FORCE
            else:
                # Chase target
                self.vx = RUN_SPEED if dist_x > 0 else -RUN_SPEED
                if self.on_ground and self.is_obstacle_ahead(world):
                    self.vy = JUMP_FORCE
                    
                # Attack!
                if abs(dist_x) <= hit_range:
                    self.vx = 0
                    self.mining_progress += dt  # reuse as attack attack speed cooldown
                    if self.mining_progress >= 0.5:
                        self.mining_progress = 0.0
                        damage = 4  # Wood sword base
                        if self.equipment["sword"] == "iron_sword":
                            damage = 6
                        elif self.equipment["sword"] == "diamond_sword":
                            damage = 8
                            
                        # Double damage critical hits on random jumps!
                        is_crit = not self.on_ground and self.vy > 0
                        if is_crit:
                            damage *= 1.5
                            self.say("Crit!", 0.8)
                            
                        # Knockback direction
                        kb = 3.5 if dist_x > 0 else -3.5
                        self.target_entity.take_damage(damage, kb)
                        play_sound("hit")
                        # Swing arm particle
                        particles.append(Particle(self.target_entity.x + 10, self.target_entity.y + 20, random.uniform(-2,2), random.uniform(-2,0), (200,200,200), 0.3))

        elif self.state == "sleep":
            # Must sleep inside house (near bed coordinates ~col 19)
            target_col_x = 19 * SCALED_TILE
            dist_x = target_col_x - self.x
            
            if abs(dist_x) > 10:
                self.vx = WALK_SPEED if dist_x > 0 else -WALK_SPEED
                self.facing_right = dist_x > 0
                if self.on_ground and self.is_obstacle_ahead(world):
                    self.vy = JUMP_FORCE
            else:
                self.vx = 0
                # Float up slightly onto bed
                self.y = world.work_bottom - 2.5 * SCALED_TILE
                self.say("Zzz...", 1.0)
                # Fast forward world time
                world.time_of_day += 6.0 * dt_multiplier
                # Heart/Sleep particles
                if random.random() < 0.08:
                    particles.append(TextParticle(self.x + 10, self.y - 10, "Z", (170,170,255), 1.5))
                if not world.is_night():
                    self.state = "wander"
                    self.state_timer = 2.0
                    self.say("Good morning!", 2.5)

        elif self.state == "wander":
            # Decide what to do next based on progression and needs
            self.state_timer -= dt
            if self.state_timer <= 0:
                # Night: go sleep or fight
                if world.is_night() and world.structures.get("house", False):
                    self.state = "sleep"
                    self.say("Night time. Going to sleep.", 2.5)
                    return
                    
                # Need wood?
                wood_count = self.inventory.get("wood", 0)
                stone_count = self.inventory.get("stone", 0)
                
                # Determine next build goal based on day
                build_goal = self.get_next_build_goal(world)
                
                if build_goal:
                    req_wood = build_goal.get("wood", 0)
                    req_stone = build_goal.get("stone", 0)
                    
                    if wood_count < req_wood:
                        # Find wood
                        self.state = "gather_wood"
                        self.target_x = self.find_block_coordinate(world, "wood_log")
                        if self.target_x is None:
                            # No trees? Spawn one!
                            world.spawn_tree(random.randint(4, world.cols - 4))
                            self.target_x = self.find_block_coordinate(world, "wood_log")
                        self.say("Heading to chop trees.", 2.5)
                    elif stone_count < req_stone:
                        # Find stone
                        self.state = "mine_stone"
                        self.target_x = self.find_block_coordinate(world, "stone")
                        self.say("Heading to mine stone.", 2.5)
                    else:
                        # We have resources! Build it.
                        self.state = "build"
                        self.build_col = build_goal["col"]
                        self.build_step = 0
                        self.build_timer = 0.5
                        self.say(f"Let's build a {build_goal['name']} today!", 3.0)
                else:
                    # Wander randomly
                    self.state_timer = random.uniform(3, 8)
                    self.target_x = self.x + random.uniform(-200, 200)
                    self.target_x = max(50, min(world.width - 50, self.target_x))
                    # Print cute comments occasionally
                    if random.random() < 0.25:
                        self.say(random.choice([
                            "Don't dig straight down.",
                            "Need more torches.",
                            "That sheep looks suspicious...",
                            "Looking for diamonds...",
                            "Beautiful day today!",
                            "Mining away...",
                            "Let's check the inventory."
                        ]), 3.0)

            # Move towards wander target
            dist_x = self.target_x - self.x
            if abs(dist_x) > 10:
                self.vx = WALK_SPEED if dist_x > 0 else -WALK_SPEED
                self.facing_right = dist_x > 0
                if self.on_ground and self.is_obstacle_ahead(world):
                    self.vy = JUMP_FORCE
            else:
                self.vx = 0

        elif self.state == "gather_wood":
            # Walk to target tree
            if self.target_x is None:
                self.state = "wander"
                self.state_timer = 0
                return
                
            dist_x = self.target_x - self.x
            if abs(dist_x) > 40:
                self.vx = WALK_SPEED if dist_x > 0 else -WALK_SPEED
                self.facing_right = dist_x > 0
                if self.on_ground and self.is_obstacle_ahead(world):
                    self.vy = JUMP_FORCE
            else:
                self.vx = 0
                # Face tree
                self.facing_right = dist_x > 0
                # Start chopping!
                self.mining_progress += dt
                # Particle effects
                if random.random() < 0.15:
                    play_sound("dig")
                    particles.append(Particle(self.target_x + 16, self.y + 30, random.uniform(-1,1), random.uniform(-1,0), (171,127,86), 0.3))
                
                if self.mining_progress >= 2.0:  # 2 seconds to chop
                    self.mining_progress = 0.0
                    col = int(self.target_x // SCALED_TILE)
                    # Break the block (row 0 is base log)
                    world.set_block(col, 0, "air")
                    world.set_block(col, -1, "air") # trunk top
                    # Give wood
                    self.inventory["wood"] = self.inventory.get("wood", 0) + 4
                    self.stats["trees_cut"] = self.stats.get("trees_cut", 0) + 1
                    self.say("Chopped wood logs!", 2.0)
                    self.state = "wander"
                    self.state_timer = 0

        elif self.state == "mine_stone":
            # Walk to mine entrance (col 8, row 1-2)
            target_mine_x = 8 * SCALED_TILE
            dist_x = target_mine_x - self.x
            if abs(dist_x) > 30:
                self.vx = WALK_SPEED if dist_x > 0 else -WALK_SPEED
                self.facing_right = dist_x > 0
                if self.on_ground and self.is_obstacle_ahead(world):
                    self.vy = JUMP_FORCE
            else:
                self.vx = 0
                # Drop down to mine stone
                self.mining_progress += dt
                if random.random() < 0.15:
                    play_sound("dig")
                    particles.append(Particle(self.x + 16, self.y + self.height, random.uniform(-1,1), random.uniform(-1,0), (115,115,115), 0.3))
                    
                if self.mining_progress >= 2.0:
                    self.mining_progress = 0.0
                    
                    # Mine stone/ore randomly from underground
                    r = random.random()
                    mined_item = "stone"
                    if r < 0.02:
                        mined_item = "diamond"
                        self.stats["diamonds_found"] = self.stats.get("diamonds_found", 0) + 1
                        self.say("FOUND DIAMONDS!!", 3.0)
                        play_sound("levelup")
                    elif r < 0.06:
                        mined_item = "gold"
                        self.say("Found gold!", 2.0)
                    elif r < 0.15:
                        mined_item = "iron"
                        self.say("Found iron ore.", 2.0)
                    elif r < 0.30:
                        mined_item = "coal"
                        
                    self.inventory[mined_item] = self.inventory.get(mined_item, 0) + 1
                    self.stats["blocks_mined"] = self.stats.get("blocks_mined", 0) + 1
                    
                    # Progress pickaxe automatically based on resources
                    self.upgrade_equipment()
                    
                    self.state = "wander"
                    self.state_timer = 0

        elif self.state == "build":
            # Steve walks to build column
            target_x = self.build_col * SCALED_TILE
            dist_x = target_x - self.x
            if abs(dist_x) > 20:
                self.vx = WALK_SPEED if dist_x > 0 else -WALK_SPEED
                self.facing_right = dist_x > 0
                if self.on_ground and self.is_obstacle_ahead(world):
                    self.vy = JUMP_FORCE
            else:
                self.vx = 0
                self.build_timer -= dt
                if self.build_timer <= 0:
                    self.build_timer = 0.4
                    self.execute_build_step(world, particles)

    def is_obstacle_ahead(self, world):
        """Checks if there is a solid wall directly in front of the entity."""
        col_offset = 1 if self.facing_right else -1
        col = int((self.x + (self.width if self.facing_right else 0)) // SCALED_TILE) + col_offset
        
        # Check Row 1 (knee level)
        if world.is_solid(col, 1):
            return True
        # Check Row 0 (head level)
        if world.is_solid(col, 0):
            return True
        return False

    def find_block_coordinate(self, world, block_name):
        """Finds closest column containing block_name. Returns X coordinate or None."""
        closest_col = None
        min_dist = 9999
        steve_col = int(self.x // SCALED_TILE)
        
        for col in range(world.cols):
            # Check rows
            for row in [-3, -2, -1, 0, 1, 2]:
                if world.get_block(col, row) == block_name:
                    dist = abs(col - steve_col)
                    if dist < min_dist:
                        min_dist = dist
                        closest_col = col
                        
        if closest_col is not None:
            return closest_col * SCALED_TILE
        return None

    def get_next_build_goal(self, world):
        """Returns the dictionary for the next structure Steve should build."""
        # 1. Campfire (Day 1)
        if not world.structures.get("campfire", False):
            return {"name": "Campfire", "wood": 4, "stone": 0, "col": 15}
        # 2. Crafting Table (Day 2)
        if not world.structures.get("crafting_table", False):
            return {"name": "Crafting Table", "wood": 4, "stone": 0, "col": 16}
        # 3. Furnace (Day 5)
        if not world.structures.get("furnace", False):
            return {"name": "Furnace", "wood": 0, "stone": 8, "col": 13}
        # 4. Wooden House (Day 5+)
        if not world.structures.get("house", False):
            return {"name": "House", "wood": 16, "stone": 0, "col": 18}
        # 5. Chest (Day 10)
        if not world.structures.get("chest", False):
            # Built inside house at col 19
            return {"name": "Chest", "wood": 8, "stone": 0, "col": 19}
        # 6. Portal (Day 20+)
        if not world.structures.get("portal", False) and self.inventory.get("diamond", 0) >= 3:
            return {"name": "Nether Portal", "wood": 0, "stone": 10, "col": 38}
            
        return None

    def execute_build_step(self, world, particles):
        """Builds structures block-by-block with animations."""
        goal = self.get_next_build_goal(world)
        if not goal:
            self.state = "wander"
            return
            
        name = goal["name"]
        col = goal["col"]
        
        if name == "Campfire":
            # Single block placement
            world.set_block(col, 0, "campfire")
            world.structures["campfire"] = True
            self.inventory["wood"] -= 4
            self.stats["buildings"] = self.stats.get("buildings", 0) + 1
            self.complete_build("Campfire built!", particles)
            
        elif name == "Crafting Table":
            world.set_block(col, 0, "crafting_table")
            world.structures["crafting_table"] = True
            self.inventory["wood"] -= 4
            self.stats["buildings"] = self.stats.get("buildings", 0) + 1
            self.complete_build("Crafting Table constructed!", particles)

        elif name == "Furnace":
            world.set_block(col, 0, "furnace")
            world.structures["furnace"] = True
            self.inventory["stone"] -= 8
            self.stats["buildings"] = self.stats.get("buildings", 0) + 1
            self.complete_build("Furnace built!", particles)

        elif name == "House":
            # Step by step building of house
            # house spans cols 18 to 21
            steps = [
                # Foundations
                (18, 1, "planks"), (19, 1, "planks"), (20, 1, "planks"), (21, 1, "planks"),
                # Left wall
                (18, 0, "planks"), (18, -1, "planks"), (18, -2, "planks"),
                # Right wall
                (21, 0, "planks"), (21, -1, "planks"), (21, -2, "planks"),
                # Ceiling
                (19, -2, "planks"), (20, -2, "planks"),
                # Bed
                (19, 0, "planks")  # Place base for bed or chest
            ]
            
            if self.build_step < len(steps):
                c, r, block = steps[self.build_step]
                world.set_block(c, r, block)
                play_sound("dig")
                # Spawn placement dust
                particles.append(Particle(c * SCALED_TILE + 16, world.work_bottom - (3 - r) * SCALED_TILE, random.uniform(-1,1), random.uniform(-1,0), (140, 105, 70), 0.3))
                self.build_step += 1
            else:
                world.structures["house"] = True
                self.inventory["wood"] -= 16
                self.stats["buildings"] = self.stats.get("buildings", 0) + 1
                self.complete_build("Finished building a cozy house!", particles)

        elif name == "Chest":
            world.set_block(col, 0, "chest")
            world.structures["chest"] = True
            self.inventory["wood"] -= 8
            self.stats["buildings"] = self.stats.get("buildings", 0) + 1
            self.complete_build("Chest placed inside house.", particles)

        elif name == "Nether Portal":
            # Spans cols 38 to 40, height 4 blocks
            steps = [
                (38, 0, "stone"), (39, 0, "stone"), (40, 0, "stone"),
                (38, -1, "stone"), (40, -1, "stone"),
                (38, -2, "stone"), (40, -2, "stone"),
                (38, -3, "stone"), (39, -3, "stone"), (40, -3, "stone"),
                # Fill purple portal block
                (39, -1, "portal"), (39, -2, "portal")
            ]
            if self.build_step < len(steps):
                c, r, block = steps[self.build_step]
                world.set_block(c, r, block)
                play_sound("dig")
                particles.append(Particle(c * SCALED_TILE + 16, world.work_bottom - (3 - r) * SCALED_TILE, random.uniform(-1,1), random.uniform(-1,0), (80, 80, 80), 0.3))
                self.build_step += 1
            else:
                world.structures["portal"] = True
                self.inventory["stone"] -= 10
                self.stats["buildings"] = self.stats.get("buildings", 0) + 1
                self.complete_build("Activated Nether Portal!", particles)

    def complete_build(self, message, particles):
        self.say(message, 3.0)
        play_sound("levelup")
        self.state = "wander"
        self.state_timer = 1.0
        # Spawn celebration particles
        for _ in range(12):
            particles.append(Particle(self.x + 16, self.y, random.uniform(-3,3), random.uniform(-4,-1), (255, 215, 0), 0.6))

    def upgrade_equipment(self):
        """Automatically upgrades pickaxes and swords as materials gather."""
        wood = self.inventory.get("wood", 0)
        stone = self.inventory.get("stone", 0)
        iron = self.inventory.get("iron", 0)
        diamond = self.inventory.get("diamond", 0)
        
        # Upgrade pickaxe
        if diamond >= 3 and self.equipment["pickaxe"] != "diamond_pickaxe":
            self.equipment["pickaxe"] = "diamond_pickaxe"
            self.inventory["diamond"] -= 3
            self.say("Upgraded to Diamond Pickaxe!", 3.0)
            play_sound("levelup")
        elif iron >= 3 and self.equipment["pickaxe"] == "wood_pickaxe":
            self.equipment["pickaxe"] = "iron_pickaxe"
            self.inventory["iron"] -= 3
            self.say("Upgraded to Iron Pickaxe!", 3.0)
            play_sound("levelup")
            
        # Upgrade sword
        if diamond >= 2 and self.equipment["sword"] != "diamond_sword":
            self.equipment["sword"] = "diamond_sword"
            self.inventory["diamond"] -= 2
            self.say("Crafted Diamond Sword! Bring it on!", 3.0)
            play_sound("levelup")
        elif iron >= 2 and self.equipment["sword"] == "wood_sword":
            self.equipment["sword"] = "iron_sword"
            self.inventory["iron"] -= 2
            self.say("Crafted Iron Sword!", 3.0)
            play_sound("levelup")

    def draw(self, surface):
        # Determine state texture
        sprite_name = "idle"
        if self.state == "drag":
            sprite_name = "drag"
        elif self.state == "eat":
            sprite_name = "idle"
        elif self.state == "sleep":
            sprite_name = "sleep"
        elif self.state == "combat":
            sprite_name = "mine" if self.mining_progress < 0.25 else "idle"
        elif self.state in ["gather_wood", "mine_stone", "build"]:
            # Arm swing rhythm
            sprite_name = "mine" if (pygame.time.get_ticks() % 400 < 200) else "idle"
        elif abs(self.vx) > 0:
            # Alternate feet walk swing
            sprite_name = "walk1" if (pygame.time.get_ticks() % 300 < 150) else "walk2"

        santa_hat = self.stats.get("season_santa", False) or datetime.datetime.now().month == 12
        
        # Get compiled scaled sprite
        surf = get_steve_sprite(sprite_name, self.facing_right, santa_hat)
        
        # Adjust vertical draw position for sleep frame
        draw_y = self.y
        if self.state == "sleep":
            draw_y = self.y + 32  # draw horizontal on bed

        # Blit
        surface.blit(surf, (int(self.x), int(draw_y)))
        
        # Draw active sword/pickaxe overlay in combat/mining
        if self.state == "combat":
            tool_surf = get_item_sprite(self.equipment["sword"])
            # Draw it tilted
            tool_x = self.x + (28 if self.facing_right else -12)
            tool_y = self.y + 16
            surface.blit(tool_surf, (int(tool_x), int(tool_y)))
        elif self.state in ["gather_wood", "mine_stone"]:
            tool_surf = get_item_sprite(self.equipment["pickaxe"])
            tool_x = self.x + (28 if self.facing_right else -12)
            tool_y = self.y + 16
            surface.blit(tool_surf, (int(tool_x), int(tool_y)))

class Zombie(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 32 * SCALE, 64 * SCALE)
        self.health = 20
        self.max_health = 20
        self.burn_timer = 0.0

    def take_damage(self, amount, knockback_vx=0):
        self.health = max(0, self.health - amount)
        self.vy = -2.5
        self.vx = knockback_vx
        self.on_ground = False
        play_sound("hit")

    def update(self, world, steve, particles, dt, dt_multiplier):
        self.update_physics(world, dt_multiplier)
        
        # 1. Day burns zombies
        if not world.is_night():
            self.burn_timer += dt
            if self.burn_timer >= 0.5:
                self.burn_timer = 0.0
                self.health -= 2
                # Smoke particles
                particles.append(Particle(self.x + 16, self.y + 10, random.uniform(-0.5, 0.5), random.uniform(-1, 0), (255, 120, 0), 0.4))
                
        # 2. Chase Steve
        dist_x = steve.x - self.x
        if abs(dist_x) < 400 and steve.state != "sleep":
            self.vx = WALK_SPEED * 0.9 if dist_x > 0 else -WALK_SPEED * 0.9
            self.facing_right = dist_x > 0
            
            # Jump if wall in way
            if self.on_ground and self.is_obstacle_ahead(world):
                self.vy = JUMP_FORCE
                
            # Attack Steve!
            if abs(dist_x) <= 30 and abs(steve.y - self.y) < 32:
                self.vx = 0
                self.burn_timer += dt # reuse as combat cooldown
                if self.burn_timer >= 1.0:
                    self.burn_timer = 0.0
                    kb = 4.0 if dist_x > 0 else -4.0
                    steve.take_damage(2, kb)
        else:
            # Wander slowly
            if random.random() < 0.01:
                self.vx = random.choice([-1.0, 1.0]) * WALK_SPEED * 0.5
            self.facing_right = self.vx >= 0
            if self.on_ground and self.is_obstacle_ahead(world):
                self.vy = JUMP_FORCE

    def is_obstacle_ahead(self, world):
        col_offset = 1 if self.facing_right else -1
        col = int((self.x + (self.width if self.facing_right else 0)) // SCALED_TILE) + col_offset
        return world.is_solid(col, 1) or world.is_solid(col, 0)

    def draw(self, surface):
        sprite_name = "zombie_idle"
        if abs(self.vx) > 0:
            sprite_name = "zombie_walk1" if (pygame.time.get_ticks() % 400 < 200) else "zombie_walk2"
        surf = get_mob_sprite(sprite_name, self.facing_right)
        surface.blit(surf, (int(self.x), int(self.y)))

class Creeper(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 32 * SCALE, 64 * SCALE)
        self.health = 20
        self.max_health = 20
        
        self.fuse_timer = 0.0
        self.is_fusing = False

    def take_damage(self, amount, knockback_vx=0):
        self.health = max(0, self.health - amount)
        self.vy = -2.5
        self.vx = knockback_vx
        self.on_ground = False
        play_sound("hit")

    def update(self, world, steve, entities, particles, dt, dt_multiplier):
        self.update_physics(world, dt_multiplier)
        
        # Creepers do not burn in day, but they spawn only at night and wander
        dist_x = steve.x - self.x
        
        if abs(dist_x) < 300 and steve.state != "sleep":
            self.vx = WALK_SPEED * 1.1 if dist_x > 0 else -WALK_SPEED * 1.1
            self.facing_right = dist_x > 0
            if self.on_ground and self.is_obstacle_ahead(world):
                self.vy = JUMP_FORCE
                
            # Fuse trigger range
            if abs(dist_x) <= 40:
                self.vx = 0
                if not self.is_fusing:
                    self.is_fusing = True
                    play_sound("fuse")
                
                self.fuse_timer += dt
                # Spawn flash dust
                particles.append(Particle(self.x + random.uniform(0,32), self.y + random.uniform(0,64), 0, -1, (255,255,255), 0.2))
                
                if self.fuse_timer >= 1.5:
                    self.explode(world, steve, entities, particles)
            else:
                # Cancel fuse if Steve escapes
                if self.is_fusing and abs(dist_x) > 65:
                    self.is_fusing = False
                    self.fuse_timer = 0.0
        else:
            self.is_fusing = False
            self.fuse_timer = 0.0
            # Wander
            if random.random() < 0.01:
                self.vx = random.choice([-1.0, 1.0]) * WALK_SPEED * 0.6
            self.facing_right = self.vx >= 0
            if self.on_ground and self.is_obstacle_ahead(world):
                self.vy = JUMP_FORCE

    def explode(self, world, steve, entities, particles):
        """Detonates, destroying grid terrain and knocking back nearby entities."""
        self.health = 0 # Die
        play_sound("explode")
        
        # Calculate impact column
        mid_col = int((self.x + self.width/2) // SCALED_TILE)
        
        # Destroy terrain blocks in a small radius (destroying rows 1 and 0 mostly)
        for c in range(mid_col - 1, mid_col + 2):
            for r in [0, 1]:
                if world.is_solid(c, r):
                    world.set_block(c, r, "air")
                    # Spawn flying blocks particles
                    for _ in range(3):
                        particles.append(PhysicsParticle(c * SCALED_TILE + 16, world.work_bottom - (3 - r)*SCALED_TILE, random.uniform(-4, 4), random.uniform(-8, -2), (134,96,67), 1.5))
                        
        # Damage Steve if in range
        dist = math.hypot(steve.x - self.x, steve.y - self.y)
        if dist < 120:
            damage = int(12 - (dist / 120) * 8)
            kb_dir = 7.0 if steve.x > self.x else -7.0
            steve.take_damage(damage, kb_dir)
            steve.stats["creeper_explosions"] = steve.stats.get("creeper_explosions", 0) + 1

        # Spawn fire & smoke particles
        for _ in range(25):
            particles.append(Particle(self.x + 16, self.y + 32, random.uniform(-6, 6), random.uniform(-6, 2), random.choice([(255, 120, 0), (80, 80, 80), (255, 230, 0)]), 0.8))

    def is_obstacle_ahead(self, world):
        col_offset = 1 if self.facing_right else -1
        col = int((self.x + (self.width if self.facing_right else 0)) // SCALED_TILE) + col_offset
        return world.is_solid(col, 1) or world.is_solid(col, 0)

    def draw(self, surface):
        # Flash white if fusing
        sprite_name = "creeper_idle"
        if abs(self.vx) > 0:
            sprite_name = "creeper_walk"
        surf = get_mob_sprite(sprite_name, self.facing_right)
        
        if self.is_fusing and (int(self.fuse_timer * 10) % 2 == 0):
            # Draw flashed white overlay
            white_surf = surf.copy()
            white_surf.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_ADD)
            surface.blit(white_surf, (int(self.x), int(self.y)))
        else:
            surface.blit(surf, (int(self.x), int(self.y)))

class Wolf(Entity):
    def __init__(self, x, y, save_state=None):
        # Wolf is 16x16 scaled => 32x32 pixels
        super().__init__(x, y, 32 * SCALE, 32 * SCALE)
        self.health = 20
        self.tamed = False
        self.sitting = False
        self.target_enemy = None
        self.owner = None
        
        if save_state:
            wolf_data = save_state.get("wolf", {})
            self.tamed = wolf_data.get("tamed", False)
            self.sitting = wolf_data.get("sitting", False)
            self.health = wolf_data.get("health", 20)

    def update(self, world, steve, entities, particles, dt, dt_multiplier):
        # Apply physics
        self.update_physics(world, dt_multiplier)
        
        if self.sitting:
            self.vx = 0
            return

        # 1. Combat target logic
        if self.tamed:
            # Defend owner!
            if steve.state == "combat" and steve.target_entity:
                self.target_enemy = steve.target_entity
                
            if self.target_enemy and self.target_enemy.health <= 0:
                self.target_enemy = None
                
            if self.target_enemy:
                dist_x = self.target_enemy.x - self.x
                self.vx = RUN_SPEED * 1.2 if dist_x > 0 else -RUN_SPEED * 1.2
                self.facing_right = dist_x > 0
                if self.on_ground and self.is_obstacle_ahead(world):
                    self.vy = JUMP_FORCE
                    
                # Attack enemy
                if abs(dist_x) < 30:
                    self.vx = 0
                    if random.random() < 0.02:
                        self.target_enemy.take_damage(2)
                        play_sound("hit")
                        particles.append(Particle(self.target_enemy.x+10, self.target_enemy.y+10, 0, -1, (200, 20, 20), 0.2))
                return

        # 2. Follow owner (Steve)
        if self.tamed:
            dist_x = steve.x - self.x
            # Stay a little bit behind Steve
            ideal_dist = 60
            if abs(dist_x) > ideal_dist + 30:
                # Walk/run to catch up
                speed = RUN_SPEED if abs(dist_x) > 200 else WALK_SPEED
                self.vx = speed if dist_x > 0 else -speed
                self.facing_right = dist_x > 0
                if self.on_ground and self.is_obstacle_ahead(world):
                    self.vy = JUMP_FORCE
            else:
                self.vx = 0
        else:
            # Wild wolf wanders
            if random.random() < 0.01:
                self.vx = random.choice([-1.0, 1.0]) * WALK_SPEED * 0.5
            self.facing_right = self.vx >= 0
            if self.on_ground and self.is_obstacle_ahead(world):
                self.vy = JUMP_FORCE

    def interact_tame(self, steve, particles):
        """Attempts to tame the wolf with a bone."""
        if self.tamed:
            # Toggle sitting
            self.sitting = not self.sitting
            play_sound("click")
            steve.say("Sitting..." if self.sitting else "Follow me!", 1.5)
            return True
            
        if steve.inventory.get("bone", 0) > 0:
            steve.inventory["bone"] -= 1
            # 40% taming chance
            if random.random() < 0.40:
                self.tamed = True
                self.sitting = False
                play_sound("tame")
                steve.say("Tamed a wolf! Love it!", 3.0)
                # Heart particles
                for _ in range(8):
                    particles.append(TextParticle(self.x + 10, self.y - 10, "<3", (240, 50, 80), 1.5))
            else:
                play_sound("eat")
                steve.say("Fed wolf. Still wild...", 2.0)
                # Smoke particles for failed taming
                for _ in range(3):
                    particles.append(Particle(self.x + 16, self.y + 10, random.uniform(-1,1), random.uniform(-1,0), (120,120,120), 0.3))
            return True
        return False

    def is_obstacle_ahead(self, world):
        col_offset = 1 if self.facing_right else -1
        col = int((self.x + (self.width if self.facing_right else 0)) // SCALED_TILE) + col_offset
        return world.is_solid(col, 1)

    def draw(self, surface):
        sprite_name = "wolf_sit" if self.sitting else "wolf_idle"
        surf = get_mob_sprite(sprite_name, self.facing_right)
        
        # Render a red collar if tamed
        if self.tamed and sprite_name == "wolf_idle":
            # Procedurally overlay collar pixels onto wolf collar spot
            pass # Sprites module already supports collar colors on wolf textures
            
        surface.blit(surf, (int(self.x), int(self.y)))

class Villager(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 32 * SCALE, 64 * SCALE)
        self.state = "wander"
        self.state_timer = 2.0

    def update(self, world, steve, particles, dt, dt_multiplier):
        self.update_physics(world, dt_multiplier)
        
        self.state_timer -= dt
        if self.state_timer <= 0:
            self.state_timer = random.uniform(3, 8)
            
            # Night -> Run into house (col 20 is house doorway)
            if world.is_night() and world.structures.get("house", False):
                self.state = "sleep"
            else:
                self.state = "wander"
                
        if self.state == "sleep":
            # Head to house
            target_x = 20 * SCALED_TILE
            dist_x = target_x - self.x
            if abs(dist_x) > 15:
                self.vx = WALK_SPEED * 1.2 if dist_x > 0 else -WALK_SPEED * 1.2
                self.facing_right = dist_x > 0
                if self.on_ground and self.is_obstacle_ahead(world):
                    self.vy = JUMP_FORCE
            else:
                self.vx = 0
                # Hide inside (completely transparent overlay or just stand there)
        else:
            # Wander
            if random.random() < 0.005:
                self.vx = random.choice([-1.0, 1.0]) * WALK_SPEED * 0.6
                
            dist_x = steve.x - self.x
            # Stop and look at Steve if close
            if abs(dist_x) < 80:
                self.vx = 0
                self.facing_right = dist_x > 0
                
            if self.vx != 0 and self.on_ground and self.is_obstacle_ahead(world):
                self.vy = JUMP_FORCE

    def is_obstacle_ahead(self, world):
        col_offset = 1 if self.facing_right else -1
        col = int((self.x + (self.width if self.facing_right else 0)) // SCALED_TILE) + col_offset
        return world.is_solid(col, 1)

    def draw(self, surface):
        # Don't draw if sleeping inside the house (Steve is sleeping too, or villager is hidden)
        if self.state == "sleep" and abs(self.x - 20*SCALED_TILE) <= 20:
            return
            
        surf = get_mob_sprite("villager_idle", self.facing_right)
        surface.blit(surf, (int(self.x), int(self.y)))

class Particle:
    """A basic non-physical particle (smoke, spark, fire)."""
    def __init__(self, x, y, vx, vy, color, duration):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.max_life = duration
        self.life = duration

    def update(self, dt):
        self.x += self.vx
        self.y += self.vy
        self.life -= dt
        return self.life > 0

    def draw(self, surface):
        alpha = int((self.life / self.max_life) * 255)
        # Note: Since standard pywin32 colorkey windows can't do per-pixel alpha,
        # we draw solid colored particles, but fade them out by shrinking their size!
        size = max(1, int((self.life / self.max_life) * 6))
        pygame.draw.rect(surface, self.color, (int(self.x) - size//2, int(self.y) - size//2, size, size))

class PhysicsParticle(Particle):
    """A physical bouncing block particle (dirt/stone chunks flying from explosions)."""
    def __init__(self, x, y, vx, vy, color, duration):
        super().__init__(x, y, vx, vy, color, duration)
        self.gravity = 0.4
        
    def update(self, dt):
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy
        self.life -= dt
        return self.life > 0

    def draw(self, surface):
        size = max(2, int((self.life / self.max_life) * 8))
        pygame.draw.rect(surface, self.color, (int(self.x) - size//2, int(self.y) - size//2, size, size))

class TextParticle:
    """Floating textual particle (like 'Zzz', '<3', or '+5 XP')."""
    def __init__(self, x, y, text, color, duration):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.max_life = duration
        self.life = duration
        self.font = pygame.font.SysFont("Courier New", 14, bold=True)

    def update(self, dt):
        self.y -= 0.8  # float upwards
        self.life -= dt
        return self.life > 0

    def draw(self, surface):
        # Render text block
        text_surf = self.font.render(self.text, False, self.color)
        surface.blit(text_surf, (int(self.x), int(self.y)))

class XPOrb:
    """Floating XP orb that gets drawn, pulled towards Steve, and eaten."""
    def __init__(self, x, y, amount):
        self.x = x
        self.y = y
        self.amount = amount
        self.vy = -3.0 # pop up slightly on spawn
        self.vx = random.uniform(-2.0, 2.0)
        self.gravity = 0.25
        self.life = 15.0 # seconds before despawn

    def update(self, steve, world, dt):
        self.life -= dt
        
        # Apply physical hop on spawn
        if self.vy != 0:
            self.vy += self.gravity
            self.y += self.vy
            self.x += self.vx
            # Collide with ground
            col = int(self.x // SCALED_TILE)
            ground_y = world.work_bottom - 2 * SCALED_TILE
            if self.y >= ground_y:
                self.y = ground_y
                self.vy = 0
                self.vx = 0
                
        # Attracted to Steve if within range
        dist = math.hypot(steve.x + 16 - self.x, steve.y + 32 - self.y)
        if dist < 180:
            # Pull vector
            pull_force = 4.5
            dx = (steve.x + 16) - self.x
            dy = (steve.y + 32) - self.y
            self.x += (dx / dist) * pull_force
            self.y += (dy / dist) * pull_force
            
        # Collect check
        if dist < 20:
            steve.xp += self.amount
            steve.stats["xp"] = steve.xp
            
            # Check level up (100 XP per level)
            new_level = 1 + (steve.xp // 100)
            if new_level > steve.level:
                steve.level = new_level
                steve.stats["level"] = steve.level
                steve.say(f"Level Up! Level {new_level}!", 3.0)
                play_sound("levelup")
            else:
                play_sound("click")
                
            return False
            
        return self.life > 0

    def draw(self, surface):
        # Alternates colors for shiny effect
        color = (0, 255, 0) if (pygame.time.get_ticks() % 200 < 100) else (255, 255, 0)
        # Small neon dot
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), 4)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), 2)
