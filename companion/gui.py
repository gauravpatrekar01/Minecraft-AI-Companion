import pygame
from companion.config import SCALE, SCALED_TILE, COLOR_WHITE, COLOR_BLACK, COLOR_GREY, COLOR_DARK_GREY, COLOR_GOLD
from companion.sprites import get_item_sprite, get_block_sprite
from companion.sound import play_sound, toggle_mute, is_muted

class GUI:
    def __init__(self, width, height, work_bottom):
        self.width = width
        self.height = height
        self.work_bottom = work_bottom
        
        # UI Windows states
        self.inventory_open = False
        self.stats_open = False
        self.menu_open = False
        
        # Dimensions
        self.panel_width = 380
        self.panel_height = 320
        
        self.inventory_rect = pygame.Rect(
            (width - self.panel_width) // 2,
            (height - self.panel_height) // 2,
            self.panel_width,
            self.panel_height
        )
        self.stats_rect = pygame.Rect(
            (width - self.panel_width) // 2,
            (height - self.panel_height) // 2,
            self.panel_width,
            self.panel_height
        )
        
        # Context Menu
        self.menu_rect = pygame.Rect(0, 0, 180, 160)
        self.menu_options = [
            "Open Inventory",
            "Open Statistics",
            "Mute/Unmute Audio",
            "Summon Mob",
            "Trigger Boss Event",
            "Toggle Santa Hat",
            "Exit Companion"
        ]
        self.menu_hover_idx = -1
        
        # Fonts
        self.font_title = pygame.font.SysFont("Courier New", 18, bold=True)
        self.font_text = pygame.font.SysFont("Courier New", 14, bold=True)
        self.font_small = pygame.font.SysFont("Courier New", 12, bold=True)
        
        # Clickable buttons rects inside panels
        self.buttons = {}
        self.recalculate_buttons()

    def recalculate_buttons(self):
        self.buttons.clear()
        
        # Close button for Inventory
        self.buttons["inv_close"] = pygame.Rect(
            self.inventory_rect.right - 25, self.inventory_rect.top + 5, 20, 20
        )
        # Give Bread button
        self.buttons["give_bread"] = pygame.Rect(
            self.inventory_rect.left + 20, self.inventory_rect.bottom - 45, 90, 25
        )
        # Give Bone button
        self.buttons["give_bone"] = pygame.Rect(
            self.inventory_rect.left + 120, self.inventory_rect.bottom - 45, 90, 25
        )
        # Give Diamond button
        self.buttons["give_diamond"] = pygame.Rect(
            self.inventory_rect.left + 220, self.inventory_rect.bottom - 45, 110, 25
        )
        
        # Close button for Stats
        self.buttons["stats_close"] = pygame.Rect(
            self.stats_rect.right - 25, self.stats_rect.top + 5, 20, 20
        )

    def get_interactive_rects(self):
        """Returns all screen-space rectangles that should capture mouse clicks."""
        rects = []
        if self.inventory_open:
            rects.append(self.inventory_rect)
        if self.stats_open:
            rects.append(self.stats_rect)
        if self.menu_open:
            rects.append(self.menu_rect)
        return rects

    def open_menu(self, pos):
        self.menu_open = True
        self.menu_rect.topleft = pos
        # Clamp to screen bounds
        if self.menu_rect.right > self.width:
            self.menu_rect.right = self.width
        if self.menu_rect.bottom > self.height:
            self.menu_rect.bottom = self.height
        play_sound("click")

    def close_all(self):
        self.inventory_open = False
        self.stats_open = False
        self.menu_open = False

    def handle_click(self, pos, steve, world, entities):
        """Processes clicks on GUI elements. Returns True if click was handled by GUI."""
        # Check context menu
        if self.menu_open:
            if self.menu_rect.collidepoint(pos):
                idx = (pos[1] - self.menu_rect.top) // 22
                if 0 <= idx < len(self.menu_options):
                    self.execute_menu_option(idx, steve, world, entities)
                self.menu_open = False
                return True
            else:
                self.menu_open = False
                return True # Close menu click counts as handled
                
        # Check Inventory Window
        if self.inventory_open and self.inventory_rect.collidepoint(pos):
            if self.buttons["inv_close"].collidepoint(pos):
                self.inventory_open = False
                play_sound("click")
            elif self.buttons["give_bread"].collidepoint(pos):
                # Spawn bread in Steve's inventory
                steve.inventory["bread"] = steve.inventory.get("bread", 0) + 1
                play_sound("levelup")
                steve.say("YUM! Bread added to inventory!", 2.0)
            elif self.buttons["give_bone"].collidepoint(pos):
                steve.inventory["bone"] = steve.inventory.get("bone", 0) + 1
                play_sound("levelup")
                steve.say("A bone! Let's find a wolf!", 2.5)
            elif self.buttons["give_diamond"].collidepoint(pos):
                steve.inventory["diamond"] = steve.inventory.get("diamond", 0) + 1
                play_sound("levelup")
                steve.say("Wow! Diamond! THANK YOU!", 3.0)
            return True
            
        # Check Stats Window
        if self.stats_open and self.stats_rect.collidepoint(pos):
            if self.buttons["stats_close"].collidepoint(pos):
                self.stats_open = False
                play_sound("click")
            return True
            
        return False

    def execute_menu_option(self, idx, steve, world, entities):
        option = self.menu_options[idx]
        play_sound("click")
        
        if option == "Open Inventory":
            self.close_all()
            self.inventory_open = True
        elif option == "Open Statistics":
            self.close_all()
            self.stats_open = True
        elif option == "Mute/Unmute Audio":
            toggle_mute()
            mute_txt = "muted" if is_muted() else "unmuted"
            steve.say(f"Audio is now {mute_txt}.", 2.0)
        elif option == "Summon Mob":
            # Spawn zombie or creeper near screen bounds
            from companion.entities import Zombie, Creeper
            mob_class = random.choice([Zombie, Creeper])
            spawn_x = random.choice([20, self.width - 60])
            entities.append(mob_class(spawn_x, self.work_bottom - 2 * SCALED_TILE))
            steve.say("I hear something spawning...", 2.0)
        elif option == "Trigger Boss Event":
            # Set time to night, alert, spawn boss dragon pathing
            world.time_of_day = world.DAY_DURATION + 5.0 # force night
            from companion.entities import Zombie, Creeper
            # Spawn 2 zombies
            entities.append(Zombie(50, world.work_bottom - 2 * SCALED_TILE))
            entities.append(Zombie(self.width - 100, world.work_bottom - 2 * SCALED_TILE))
            steve.say("Boss Event: The Night is Dark!", 3.0)
            play_sound("explode")
        elif option == "Toggle Santa Hat":
            steve.stats["season_santa"] = not steve.stats.get("season_santa", False)
            steve.say("Do you like my hat?", 2.5)
        elif option == "Exit Companion":
            # Send exit signal via pygame event
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def update(self, pos):
        """Updates hover indexes for UI highlights."""
        if self.menu_open:
            if self.menu_rect.collidepoint(pos):
                self.menu_hover_idx = (pos[1] - self.menu_rect.top) // 22
            else:
                self.menu_hover_idx = -1

    def draw(self, surface, steve, world):
        """Draws all open panels and speech bubbles."""
        # 1. Draw Context Menu
        if self.menu_open:
            self.draw_beveled_box(surface, self.menu_rect)
            for i, opt in enumerate(self.menu_options):
                opt_rect = pygame.Rect(self.menu_rect.left + 5, self.menu_rect.top + i*22 + 4, self.menu_rect.width - 10, 20)
                if i == self.menu_hover_idx:
                    pygame.draw.rect(surface, (100, 100, 150), opt_rect)
                    text_color = COLOR_GOLD
                else:
                    text_color = COLOR_WHITE
                # Draw text
                txt = self.font_small.render(opt, False, text_color)
                surface.blit(txt, (opt_rect.left + 5, opt_rect.top + 2))
                
        # 2. Draw Inventory Window
        if self.inventory_open:
            self.draw_beveled_box(surface, self.inventory_rect)
            
            # Title
            title = self.font_title.render("Steve's Inventory", False, COLOR_GOLD)
            surface.blit(title, (self.inventory_rect.left + 15, self.inventory_rect.top + 10))
            
            # Close button
            pygame.draw.rect(surface, (180, 50, 50), self.buttons["inv_close"])
            pygame.draw.rect(surface, COLOR_BLACK, self.buttons["inv_close"], 1)
            close_lbl = self.font_small.render("X", False, COLOR_WHITE)
            surface.blit(close_lbl, (self.buttons["inv_close"].left + 6, self.buttons["inv_close"].top + 3))

            # Render item slots (grid layout)
            items = list(steve.inventory.items())
            start_x = self.inventory_rect.left + 20
            start_y = self.inventory_rect.top + 45
            
            for idx in range(12):  # 12 slots (4x3 grid)
                col = idx % 4
                row = idx // 4
                slot_rect = pygame.Rect(start_x + col*85, start_y + row*65, 75, 55)
                self.draw_slot_box(surface, slot_rect)
                
                if idx < len(items):
                    item_name, qty = items[idx]
                    # Draw item icon
                    icon = get_item_sprite(item_name)
                    surface.blit(icon, (slot_rect.left + 6, slot_rect.top + 6))
                    # Draw count
                    lbl = self.font_small.render(str(qty), False, COLOR_WHITE)
                    # Text shadow
                    lbl_shadow = self.font_small.render(str(qty), False, COLOR_BLACK)
                    surface.blit(lbl_shadow, (slot_rect.right - 21, slot_rect.bottom - 17))
                    surface.blit(lbl, (slot_rect.right - 22, slot_rect.bottom - 18))
                    # Label name
                    name_lbl = self.font_small.render(item_name.replace("_", " "), False, COLOR_GREY)
                    surface.blit(name_lbl, (slot_rect.left + 4, slot_rect.top + 38))

            # Action Buttons
            self.draw_gui_button(surface, self.buttons["give_bread"], "Give Bread", (200, 200, 200))
            self.draw_gui_button(surface, self.buttons["give_bone"], "Give Bone", (200, 200, 200))
            self.draw_gui_button(surface, self.buttons["give_diamond"], "Give Diamond", (200, 200, 200))

        # 3. Draw Statistics Window
        if self.stats_open:
            self.draw_beveled_box(surface, self.stats_rect)
            
            # Title
            title = self.font_title.render("Statistics", False, COLOR_GOLD)
            surface.blit(title, (self.stats_rect.left + 15, self.stats_rect.top + 10))
            
            # Close button
            pygame.draw.rect(surface, (180, 50, 50), self.buttons["stats_close"])
            pygame.draw.rect(surface, COLOR_BLACK, self.buttons["stats_close"], 1)
            close_lbl = self.font_small.render("X", False, COLOR_WHITE)
            surface.blit(close_lbl, (self.buttons["stats_close"].left + 6, self.buttons["stats_close"].top + 3))

            # Stats text list
            stats_list = [
                f"Trees Chopped:   {steve.stats.get('trees_cut', 0)}",
                f"Blocks Mined:    {steve.stats.get('blocks_mined', 0)}",
                f"Zombies Slain:   {steve.stats.get('zombies_killed', 0)}",
                f"Buildings Built: {steve.stats.get('buildings', 0)}",
                f"Diamonds Found:  {steve.stats.get('diamonds_found', 0)}",
                f"Days Survived:   {world.day}",
                f"Level:           {steve.level} ({steve.xp % 100}/100 XP)",
                f"Creepers Blown:  {steve.stats.get('creeper_explosions', 0)}"
            ]
            
            for idx, stat in enumerate(stats_list):
                txt_surf = self.font_text.render(stat, False, COLOR_WHITE)
                surface.blit(txt_surf, (self.stats_rect.left + 30, self.stats_rect.top + 50 + idx * 28))

    def draw_beveled_box(self, surface, rect):
        """Draws classic Minecraft UI dark grey look with beveled double border."""
        # Dark fill
        pygame.draw.rect(surface, COLOR_DARK_GREY, rect)
        
        # Outer light bevel
        pygame.draw.rect(surface, (198, 198, 198), rect, 3)
        
        # Inner dark indent border
        inner_rect = rect.inflate(-6, -6)
        pygame.draw.rect(surface, COLOR_BLACK, inner_rect, 2)

    def draw_slot_box(self, surface, rect):
        """Draws slot recess shape."""
        pygame.draw.rect(surface, (139, 139, 139), rect)
        # Inner shadow
        pygame.draw.rect(surface, COLOR_DARK_GREY, rect, 2)
        # bottom highlight
        pygame.draw.line(surface, COLOR_WHITE, rect.bottomleft, rect.bottomright, 1)
        pygame.draw.line(surface, COLOR_WHITE, rect.topright, rect.bottomright, 1)

    def draw_gui_button(self, surface, rect, label, base_color):
        """Draws classic Minecraft rectangular click button."""
        mx, my = pygame.mouse.get_pos()
        hover = rect.collidepoint(mx, my)
        
        bg_color = (150, 150, 150) if hover else (120, 120, 120)
        pygame.draw.rect(surface, bg_color, rect)
        
        # Borders
        pygame.draw.rect(surface, COLOR_BLACK, rect, 1)
        
        # Highlight highlight lines
        pygame.draw.line(surface, COLOR_WHITE, rect.topleft, (rect.right - 1, rect.top), 1)
        pygame.draw.line(surface, COLOR_WHITE, rect.topleft, (rect.left, rect.bottom - 1), 1)
        pygame.draw.line(surface, COLOR_DARK_GREY, (rect.left + 1, rect.bottom - 1), rect.bottomright, 1)
        pygame.draw.line(surface, COLOR_DARK_GREY, (rect.right - 1, rect.top + 1), rect.bottomright, 1)
        
        text_color = COLOR_GOLD if hover else COLOR_WHITE
        lbl = self.font_small.render(label, False, text_color)
        surface.blit(lbl, (rect.left + (rect.width - lbl.get_width()) // 2, rect.top + 5))

    @staticmethod
    def draw_speech_bubble(surface, text, entity_x, entity_y, screen_width):
        """Draws speech bubble with pixelated borders above entity."""
        # Calculate bounds
        font = pygame.font.SysFont("Courier New", 12, bold=True)
        # Wrap words if long
        words = text.split(" ")
        lines = []
        curr_line = ""
        for w in words:
            test_line = curr_line + (" " if curr_line else "") + w
            if font.size(test_line)[0] > 180:
                lines.append(curr_line)
                curr_line = w
            else:
                curr_line = test_line
        if curr_line:
            lines.append(curr_line)
            
        # Size
        max_w = max(font.size(l)[0] for l in lines)
        box_w = max_w + 16
        box_h = len(lines) * 16 + 12
        
        # Position centered above entity head
        bx = int(entity_x + 16 - box_w // 2)
        by = int(entity_y - box_h - 12)
        
        # Clamp to screen borders
        bx = max(10, min(screen_width - box_w - 10, bx))
        by = max(10, by)
        
        box_rect = pygame.Rect(bx, by, box_w, box_h)
        
        # Draw pixelated speech box
        pygame.draw.rect(surface, COLOR_WHITE, box_rect)
        pygame.draw.rect(surface, COLOR_BLACK, box_rect, 2)
        
        # Draw triangle tip pointer pointing to entity
        tip_x = int(entity_x + 16)
        tip_y = int(entity_y - 3)
        # Tip points (drawn as simple pixel lines)
        pygame.draw.polygon(surface, COLOR_WHITE, [
            (tip_x - 6, by + box_h),
            (tip_x + 6, by + box_h),
            (tip_x, tip_y)
        ])
        pygame.draw.line(surface, COLOR_BLACK, (tip_x - 6, by + box_h), (tip_x, tip_y), 2)
        pygame.draw.line(surface, COLOR_BLACK, (tip_x + 6, by + box_h), (tip_x, tip_y), 2)
        
        # Draw text lines
        for idx, line in enumerate(lines):
            lbl = font.render(line, False, COLOR_BLACK)
            surface.blit(lbl, (bx + 8, by + 6 + idx * 16))
