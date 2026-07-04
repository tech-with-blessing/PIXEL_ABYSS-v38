import pygame
import json
from os.path import join

from .settings import Settings
from .assets import Assets
from .data import text
from .functions import ( RPGMenu, My_Text, TypeText,
        parallax_bg, get_dynamic_color, draw_vertical_gradient,
        cache_font, cache_img, refresh_joysticks, get_block,
        cache_assets
)

class Windows:

    def update_start_btns_pos(self):
        self.game_name.x, self.game_name.y = Settings.WIDTH // 2, 10
        self.game_name.update()

    def start(self):

        global game_started, message_text, message_timer
        
        typewriter = TypeText(
            "You awake in the dark.\nA voice whispers:\n'Five floors down... then I let you go.'",
            pos=(10, 10),
            font=Settings.font,
            color=(50, 50, 50),
            speed=15  # 20 characters per second
        )

        self.game_name = My_Text("PIXEL ABYSS")

        bg_particles = []
        master_clock = 0
        height = 2

        message_timer = 0
        message_text = ""
        self.displaying = True
        game_started = True

        times = 0

        font = pygame.font.SysFont("serif", 36)

        def start():
            global game_started, message_text, message_timer
            print("Start Game!")
            message_text = "Starting Game..."  # Replace with actual scene transition
            message_timer = pygame.time.get_ticks()  # Start message timer
            game_started = True

        def mode(object_):
            print("Select preferred mode!")
            object_.modes()

        def game_info(object_):
            print("Select preferred game_info!")
            object_.game_info()

        def author_info(object_):
            print("Select preferred author_info!")
            object_.author_info()

        def store(object_):
            print("Select preferred store!")
            return object_.store()

        def game_settings(object_):
            print("Select preferred game_settings!")
            object_.game_settings(1)

        def quit_(object_):
            print("Quit Game!")
            object_.running = False
            object_.displaying = False

        button_data = [
            ("Start", start, None), ("Mode", mode, [self]),
            ("game_info", game_info, [self]), ("author_info", author_info, [self]),
            ("store", store, [self]), ("game_settings", game_settings, [self]),
            ("Quit", quit_, [self])
        ]
        layout = [
            (0.5, 0.15, 0.3, 0.06),
            (0.3, 0.25, 0.3, 0.06),
            (0.5, 0.35, 0.3, 0.06),
            (0.3, 0.45, 0.3, 0.06),
            (0.5, 0.55, 0.3, 0.06),
            (0.3, 0.65, 0.3, 0.06),
            (0.5, 0.75, 0.3, 0.06),
            (0.5, 0.95, 0.3, 0.06)
        ]

        menu = RPGMenu(self.window, font, button_data, layout)

        while self.displaying:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.VIDEORESIZE or event.type == pygame.WINDOWDISPLAYCHANGED:
                        print(event)
                        self.fix_orientation([self.game_name])
                        continue
                
                if event.type == pygame.QUIT:
                    self.displaying = False
                    del self
                    return

                if event.type == (pygame.JOYDEVICEADDED or pygame.JOYDEVICEREMOVED):
                    refresh_joysticks(self)
                    
                if event.type == pygame.JOYAXISMOTION:
                    # HANDLE MENU JOY_BUTTONS EVENTS
                    menu.handle_joy(event, "axis")
                    
                if event.type == pygame.JOYBUTTONDOWN:
                    
                    # HANDLE MENU JOY_BUTTONS EVENTS
                    menu.handle_joy(event)
                    
                if event.type == pygame.KEYDOWN:
                    menu.handle_key(event.key)

                    # EXIT KEYS
                    if event.key == pygame.K_ESCAPE:
                        self.displaying = False
                        del self
                        return

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if not typewriter.done:
                        typewriter.skip()  # Skip to full text

                    menu.handle_mouse(event)

            self.game_name.update()

            # Clear the message after 2 seconds
            if message_text and pygame.time.get_ticks() - message_timer > 2000:
                message_text = ""
                if game_started:
                    '''if self.MULTIPLAYER:
                        if self.SERVER:'''
                    from . import server as game
                    '''    else:
                            import client as game
                    else:
                        import offline as game'''
                    game.main(self, code=times)
                    times += 1
                    game_started = False

            self.window.fill(self.bg_color)

            bg_particles = parallax_bg(
                self.window, 
                Settings.WIDTH, Settings.HEIGHT, 
                bg_particles, master_clock,
                threshold=20, height=0,
                parallax_color=Settings.PARALLAX, bg_color=Settings.BG_COLOR
            )
            
            self.game_name.draw()

            # Show feedback message if any
            if message_text:
                msg = Settings.SMALL_FONT.render(message_text, True, Settings.RED)
                msg_rect = msg.get_rect(center=(Settings.WIDTH // 2, Settings.HEIGHT - 100))
                Settings.window.blit(msg, msg_rect)

            typewriter.update()
            typewriter.draw(self.window, True)

            menu.update(mouse_pos)
            menu.draw()

            self.get_fps()

            pygame.display.flip()

            # HANDLE DELTA TIME
            raw_dt = self.clock.tick(self.FPS) / 1000.0
            self.game_speed = min(self.max_game_speed, self.game_speed + 0.1)
            self.dt = min(0.1, raw_dt * self.game_speed)
            master_clock += int(raw_dt * 80)


    # Changing game modes
    def modes(self, code=0):

        displaying = True

        self.menu_btn_text = 'BACK'

        txt = My_Text("CURRENT MODE")

        font = pygame.font.SysFont("serif", 36)

        def change_type_(object_):
            print("Quit Game Settings!")
            object_.SERVER = not object_.SERVER

        def change_mode_(object_):
            print("Quit Game Settings!")
            object_.MULTIPLAYER = not object_.MULTIPLAYER

        def back_(object_):
            print("Quit Game Settings!")
            object_.modes_window = False

        button_data = [
            ("Back", back_, [self]),
            ("CHANGE MODE", change_mode_, [self]),
            ("CHANGE TYPE", change_type_, [self])]

        layout = [
            (1 - 0.02 - 0.1, 0.02 + 0.06, 0.1, 0.06),
            (0.5 - 0.1, 0.5 - 0.03, 0.2, 0.06),
            (0.5 - 0.1, 0.5 + 0.03*2, 0.2, 0.06)]

        menu = RPGMenu(self.window, font, button_data, layout)
        self.modes_window = True

        while self.modes_window:

            menu.exclude((2, not self.MULTIPLAYER))

            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.modes_window = False
                    break
                
                if event.type == pygame.JOYAXISMOTION:
                    # HANDLE MENU JOY_BUTTONS EVENTS
                    menu.handle_joy(event, "axis")
                    
                if event.type == pygame.JOYBUTTONDOWN:
                    
                    # HANDLE MENU JOY_BUTTONS EVENTS
                    menu.handle_joy(event)
                    
                if event.type == pygame.KEYDOWN:
                    menu.handle_key(event.key)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    menu.handle_mouse(event)

            self.fix_orientation([txt])

            if self.SERVER:
                self.CONNECTION_TYPE = 'HOST (server)'
            else:
                self.CONNECTION_TYPE = 'JOIN (client)'

            self.window.fill((200, 0, 200))

            # Bg
            self.window.blit(self.menu_bg, (0, 0))

            txt.draw()

            text_surface_ = Settings.display_font.render(f'SOLO' if not self.MULTIPLAYER else 'MULTIPLAYER', True,
                                                         Settings.BLACK)
            rect = text_surface_.get_rect()
            rect2 = pygame.Rect(0, 100, rect.width, rect.height)

            rect2.centerx = Settings.WIDTH / 2

            Settings.window.blit(text_surface_, (rect2.x, rect2.y))

            if self.MULTIPLAYER:
                text_surface = Settings.display_font.render(f'CLIENT' if not self.SERVER else 'SERVER', True,
                                                            Settings.BLACK)
                rect = text_surface.get_rect()
                rect = pygame.Rect(0, 200, rect.width, rect.height)

                rect.centerx = Settings.WIDTH / 2

                Settings.window.blit(text_surface, (rect.x, rect.y))

            menu.update(mouse_pos)
            menu.draw()

            self.get_fps()

            pygame.display.flip()

            self.clock.tick(self.FPS)

    def entity_info(self, entity):

        self.info_displaying = True
        
        txt = My_Text("ENTITY INFO")

        text_line_height = 200
        text_box = pygame.Rect(Settings.WIDTH / 2 - 200, Settings.HEIGHT / 2 - 100, 400, text_line_height)


        sw, sh = self.window.get_rect().size
        font = cache_font(("impact", int(sw * 0.02)))
        
        def befriend_(object_):
            print("Quit Game Settings!")
            if menu.buttons[1].text == 'UNFRIEND':
                menu.buttons[1].text = "BEFRIEND"
                if entity in object_.player.friends:
                    object_.player.friends.remove(entity)
                if object_.player in entity.friends:
                    entity.friends.remove(object_.player)
                entity.color = entity.original_color

            elif menu.buttons[1].text == 'BEFRIEND':
                menu.buttons[1].text = "UNFRIEND"
                if entity not in object_.player.friends:
                    object_.player.friends.append(entity)

                if object_.player not in entity.friends:
                    entity.friends.append(object_.player)

                entity.original_color = entity.color
                entity.color = object_.player.color

        def back_(object_):
            print("Quit Game Settings!")
            object_.info_displaying = False

        button_data = [
            ("Back", back_, [self]),
            ("BEFRIEND", befriend_, [self])]

        layout = [
            (1 - 0.02 - 0.1, 0.02 + 0.06, 0.1, 0.06),
            (0.5 - 0.1, (text_box.bottom + 20) / sh, 0.2, 0.06)
        ]

        menu = RPGMenu(self.window, font, button_data, layout)

        menu.buttons[1].text = "BEFRIEND"

        details = [f'Name : {entity.name}', f'Type : {entity.type.title()}', f'Colour : {entity.color}',
                   f'Health : {entity.health}', f'Title : The {entity.color} {entity.name} number {entity.entity_id}',
                   f'{entity.kills} Kills', entity.type.title() + f' id : {entity.id}',
                   f'Entity id : {entity.entity_id}', f'Friends : {len(entity.friends)}']
        
        layout = list()

        for i, detail in enumerate(details):
            layout.append(Settings.menu_font.render(detail, True, (0, 0, 0)))

        while self.info_displaying:
            # CAPTURE EVENTS
            self.mouse_pos = pygame.mouse.get_pos()
            self.events = pygame.event.get()

            text_box.x, text_box.y = Settings.WIDTH / 2 - 200, Settings.HEIGHT / 2 - 100
            menu.buttons[1].rect.y = text_box.bottom + 20

            if self.player in entity.friends:
                menu.buttons[1].text = "UNFRIEND"

            for event in self.events:
                if event.type == pygame.QUIT:
                    self.info_displaying = False
                    break
                    
                if event.type == pygame.VIDEORESIZE or event.type == pygame.WINDOWDISPLAYCHANGED:
                    try:
                        print(event)
                        self.fix_orientation()
                        continue
                    except Exception as e:
                        print(e)

                if event.type == pygame.KEYUP:
                    self.keys = pygame.key.get_pressed()

                if event.type == pygame.KEYDOWN:
                    self.keys = pygame.key.get_pressed()

                    # HANDLE MENU BUTTONS EVENTS
                    menu.handle_key(event.key)

                    # EXIT KEYS
                    if self.keys[pygame.K_ESCAPE]:
                        self.info_displaying = False
                        return
                
                if event.type == pygame.JOYAXISMOTION:
                    # HANDLE MENU JOY_BUTTONS EVENTS
                    menu.handle_joy(event, "axis")
                    
                if event.type == pygame.JOYBUTTONDOWN:
                    
                    # HANDLE MENU JOY_BUTTONS EVENTS
                    menu.handle_joy(event)

                if event.type == pygame.MOUSEBUTTONDOWN:        
                    # HANDLE BUTTON EVENTS
                    menu.handle_mouse(event)


            bg_color = get_dynamic_color(-25)
            color_top = get_dynamic_color()
            color_bottom = get_dynamic_color(time_offset=4.14)  # Opposite phase for contrast
            draw_vertical_gradient(color_top, color_bottom, self.window, self.HEIGHT, self.WIDTH)

            self.draw_sub()

            # MENU BUTTONS
            menu.update(self.mouse_pos)
            menu.draw()

            txt.draw()

            pygame.draw.rect(self.window, bg_color, text_box, border_radius=20)

            for i, detail in enumerate(layout):
                text_line = detail.get_rect()
                text_line_height = text_box.y + 20 + (i * text_line.height + 10)
                self.window.blit(detail, (text_box.centerx - text_line.width / 2, text_line_height))
                text_line_height = text_box.y + 20 + ((i + 1) * text_line.height) + 10

            text_box.height = text_line_height + 20 - text_box.y         

            self.get_fps()

            pygame.display.flip()

            self.clock.tick(self.FPS)


    def game_settings(self, code=0):

        self.menu_btn_text = 'BACK'

        font = pygame.font.SysFont("serif", 36)

        def volume_settings(object_):
            print("Volume settings selected!")
            object_.volumes.main()

        def back_(object_):
            print("Quit Game Settings!")
            object_.game_settings_window = False

        def world_editor(object_):
            print("Selected Level Editor!")
            object_.edit_world()

        button_data = [
            ("Back", back_, [self]),
            ("VOLUME", volume_settings, [self]),
            ("WORLD EDITOR", world_editor, [self])
        ]

        layout = [
            (1 - 0.02 - 0.1, 0.02 + 0.06, 0.1, 0.06),
            (1 - 0.5 - 0.1, 0.5 - 0.03 - 0.06 - 0.02, 0.2, 0.06),
            (1 - 0.5 - 0.15, 0.5 - 0.03, 0.3, 0.06)
        ]

        menu = RPGMenu(self.window, font, button_data, layout)
        self.game_settings_window = True

        while self.game_settings_window:

            self.fix_orientation()

            mouse_pos = pygame.mouse.get_pos()

            menu.exclude((2, bool(code)))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    displaying = False
                    break
                
                if event.type == pygame.JOYAXISMOTION:
                    # HANDLE MENU JOY_BUTTONS EVENTS
                    menu.handle_joy(event, "axis")
                    
                if event.type == pygame.JOYBUTTONDOWN:
                    
                    # HANDLE MENU JOY_BUTTONS EVENTS
                    menu.handle_joy(event)
                    
                if event.type == pygame.KEYDOWN:
                    menu.handle_key(event.key)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    menu.handle_mouse(event)

            self.window.fill((200, 0, 200))

            # Bg
            self.window.blit(self.menu_bg, (0, 0))

            menu.update(mouse_pos)
            menu.draw()

            self.get_fps()

            pygame.display.flip()

            self.clock.tick(self.FPS)

    def game_info(self):

        font = pygame.font.SysFont("serif", 36)

        def back_(object_):
            print("Quit Game Settings!")
            object_.game_info_window = False

        button_data = [
            ("Back", back_, [self])]

        layout = [
            (1 - 0.02 - 0.1, 0.02 + 0.06, 0.1, 0.06)]

        menu = RPGMenu(self.window, font, button_data, layout)
        self.game_info_window = True

        while self.game_info_window:

            self.fix_orientation()

            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    displaying = False
                    break
                
                if event.type == pygame.JOYAXISMOTION:
                    # HANDLE MENU JOY_BUTTONS EVENTS
                    menu.handle_joy(event, "axis")
                    
                if event.type == pygame.JOYBUTTONDOWN:
                    
                    # HANDLE MENU JOY_BUTTONS EVENTS
                    menu.handle_joy(event)
                    
                if event.type == pygame.KEYDOWN:
                    menu.handle_key(event.key)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    menu.handle_mouse(event)

            self.window.fill((200, 0, 200))

            # Bg
            self.window.blit(self.menu_bg, (0, 0))

            self.get_fps()

            menu.update(mouse_pos)
            menu.draw()

            pygame.display.flip()

            self.clock.tick(self.FPS)

    def edit_world(self):

        self.editing_level = True

        self.EDIT_WORLD = True

        self.lastx = self.offset_x
        self.lasty = self.offset_y

        self.menu_btn_text = 'BACK'
        self.clicked = False

        self.size_rect = pygame.Rect(0, 0, 60, 40)
        self.item_size = '0;0'

        surf = cache_img((64, 64))

        self.skip = False

        font = pygame.font.SysFont("serif", 36)

        def type_(object_):
            print("Changed type!")
            if object_.shift:
                if object_.block_num == 0:
                    object_.block_num = len(object_.block_types[object_.type_num]) - 1
                else:
                    object_.block_num -= 1
            else:
                object_.block_num += 1

            object_.skip = True

        def size(object_):
            print("Changed size or colour!")
            if object_.shift:
                object_.size_num -= 1
            else:
                object_.size_num += 1

            object_.skip = True

        def category(object_):
            print("Changed category!")
            object_.EDIT_GRID = (object_.EDIT_GRID + 1) % len(object_.edit_grid_settings)
            settings = object_.edit_grid_settings[object_.EDIT_GRID]
            # object_.EDIT_GRID_BTN.text = settings['button_text']
            # object_.CHANGE_SIZE_BTN.text = settings['change_size_text']
            object_.block_types = settings['block_types']
            object_.block_sizes = settings['block_sizes']

            object_.skip = True

        def save(object_):
            print("Saved World!")
            # Save block coordinates
            with open(join('levels', f'{object_.level}.json'), "w") as f:
                json.dump(object_.world, f, indent=2)

            object_.skip = True

        def back_(object_):
            print("Quit Level Editor!")
            object_.offset_x = object_.lastx
            object_.offset_y = object_.lasty
            object_.EDIT_WORLD = False
            object_.editing_level = False

            object_.skip = True

        def change_mode(object_):
            object_.INSERT = not object_.INSERT
            if object_.INSERT:
                print("Insert Mode Activated!")
            else:
                print("Delete Mode Activated!")
                object_.platform = []

            object_.skip = True

        def zoom_in(object_):
            print("Zoomed In!")
            object_.zoom -= object_.zoom_speed
            if object_.zoom < object_.min_zoom:
                object_.zoom = object_.min_zoom
            
            object_.skip = True

        def zoom_out(object_):
            print("Zoomed Out!")
            object_.zoom += object_.zoom_speed
            if object_.zoom > object_.max_zoom:
                object_.zoom = object_.max_zoom
            
            object_.skip = True

        button_data = [
            ("Back", back_, [self]), ("Insert Mode", change_mode, [self]),
            ("Size", size, [self]), ("Type", type_, [self]),
            ("Category", category, [self]), ("Save", save, [self]),
            ("+", zoom_out, [self]), ("-", zoom_in, [self])
        ]

        layout = [
            (1 - 0.02 - 0.1, 0.02 + 0.06, 0.1, 0.06),
            (1 - 0.02 * 2 - 0.3, 0.02 + 0.06, 0.2, 0.06),
            (1 - 0.02 * 2 - 0.1, 0.02 * 2 + 0.06 * 2 + 0.05, 0.1, 0.06),
            (1 - 0.02 * 2 - 0.4, 0.02 * 2 + 0.06 * 2 + 0.05, 0.1, 0.06),
            (1 - 0.02 * 2 - 0.3, 0.35, 0.2, 0.06),
            (0.02, 0.18, 0.1, 0.06),
            (0.035, 0.1, 0.07, 0.05),
            (0.035, 0.02, 0.07, 0.05)
        ]

        rel_rect = (1 - 0.02 * 2 - 0.3, 0.02 * 2 + 0.06 + 0.06, 0.2, 0.06 * 3)

        sw, sh = self.window.get_size()
        display_rect = pygame.Rect(
            int(rel_rect[0] * sw),
            int(rel_rect[1] * sh),
            int(rel_rect[2] * sw),
            int(rel_rect[3] * sh)
        )

        menu = RPGMenu(self.window, font, button_data, layout)

        mode = "all"
        self.shift = False
        self._draw_list_dirty = True
        
        while self.editing_level:
            mouse_pos = pygame.mouse.get_pos()
            events = pygame.event.get()

            for event in events:
                try:
                    if event.type == pygame.VIDEORESIZE:
                        print(event)
                        self.fix_orientation()

                    elif event.type == pygame.WINDOWDISPLAYCHANGED:
                        print(event)
                        self.fix_orientation()
                except Exception as e:
                    print(e)

                if event.type == pygame.QUIT:
                    self.editing_level = False
                    break
                
                if event.type == pygame.JOYAXISMOTION:
                    # HANDLE MENU JOY_BUTTONS EVENTS
                    menu.handle_joy(event, "axis")
                    
                if event.type == pygame.JOYBUTTONDOWN:
                    
                    # HANDLE MENU JOY_BUTTONS EVENTS
                    menu.handle_joy(event)
                    
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RSHIFT or event.key == pygame.K_LSHIFT:
                        self.shift = not self.shift
                    
                    if event.key == pygame.K_i:
                        self.INSERT = not self.INSERT
                    
                    if event.key == pygame.K_o:
                        self.perspective = "fore" if self.perspective == "back" else "back"
            
                    menu.handle_key(event.key)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    menu.handle_mouse(event)

                if not self.skip:
                    self.grid_settings_manager(event, events)

            self.skip = False

            self.size_num = max(0, self.size_num)
            self.type_num = max(0, self.type_num)
            self.block_num = max(0, self.block_num)

            if self.size_num > len(self.block_sizes) - 1:
                self.size_num = 0

            if self.type_num > len(self.block_types) - 1:
                self.type_num = 0

            if self.block_num > len(self.block_types[self.type_num]) - 1:
                self.type_num += 1
                self.block_num = 0

            if self.type_num > len(self.block_types) - 1:
                self.type_num = 0

            try:
                # Grid block settings
                self.type = self.block_types[self.type_num][self.block_num]
                self.size = self.block_sizes[self.size_num]
            except Exception as e:
                print(e,"In windows.edit_world")
                pass
            
            self.offset_x = max(self.minx, min(self.offset_x, self.maxx - (Settings.WIDTH / self.zoom)))
            self.offset_y = max(self.miny, min(self.offset_y, self.maxy - (Settings.HEIGHT / self.zoom)))
            # --------------------------------------------------------------------------------------------------------------
            # DRAWING THE SCREEN
            # --------------------------------------------------------------------------------------------------------------
            self.window.fill((200, 200, 200))

            # PARALLAX BACKGROUND
            self.bg_particles = parallax_bg(
                self.window, 
                Settings.WIDTH, Settings.HEIGHT, 
                self.bg_particles, self.master_clock,
                threshold=20, height=0,
                parallax_color=Settings.PARALLAX, bg_color=Settings.BG_COLOR
            )
            
            if self.EDIT_GRID:
                color = (0, 150, 150)
            else:
                color = (180, 180, 0)

            # Grid Settings
            for grid_info in self.grid:
                rect = pygame.Rect(
                                int(grid_info[0].x - self.offset_x) * self.zoom,
                                int(grid_info[0].y - self.offset_y) * self.zoom,
                                int(grid_info[0].width) * self.zoom,
                                int(grid_info[0].height) * self.zoom
                            )
                if grid_info[1] == self.RED:
                    """
                    if not self.hide(rect, "rect"):
                        pygame.draw.rect(self.window, color, (
                            int(rect.x - self.offset_x) * self.zoom, int(rect.y - self.offset_y) * self.zoom,
                            int(rect.width * self.zoom), int(rect.height * self.zoom)), width=3)
                    """
                    pass

                else:
                    if not mode == "all":
                        if mode in grid_info[2]:
                            if not self.hide(rect, "rect"):
                                pygame.draw.rect(self.window, grid_info[1], rect, width=3)
                    else:
                        if not self.hide(rect, "rect"):
                            pygame.draw.rect(self.window, grid_info[1], rect, width=3)

            self.draw_sub()
            pygame.draw.rect(self.window, (50, 20, 50), display_rect)

            #try:
            if self.EDIT_GRID == 0:
                self.window.blit(get_block(self.type, self.size),
                                    (display_rect.centerx - 32, display_rect.centery - 32))

            elif self.EDIT_GRID == 1:
                sprites = cache_assets((self.type, self.size, 'idle_right'))
                self.sprite_index = (self.animation_count //
                                        self.ANIMATION_DELAY) % len(sprites)
                self.sprite = sprites[self.sprite_index]
                self.animation_count += 1

                self.window.blit(self.sprite, (display_rect.centerx - 96, display_rect.centery - 96))

            elif self.EDIT_GRID == 2:
                sprites = Assets.GEM_SPRITES[self.type]
                self.sprite_index = (self.animation_count //
                                        3) % len(sprites)
                self.sprite = sprites[self.sprite_index]
                self.animation_count += 1

                self.window.blit(pygame.transform.scale(self.sprite, (50, 50)),
                                    (display_rect.centerx - 25, display_rect.centery - 25))

            elif self.EDIT_GRID == 3:
                if self.block_types[self.type_num][self.block_num] == 'tree':
                    sprites = Assets.TREE_SPRITES['idle_left']
                    self.sprite_index = (self.animation_count //
                                            3) % len(sprites)
                    self.sprite = sprites[self.sprite_index]
                    self.animation_count += 1

                    self.window.blit(pygame.transform.scale(self.sprite, (120, 120)),
                                        (display_rect.centerx - 60, display_rect.centery - 60))
                else:
                    sprites = Assets.DECO_SPRITES[self.block_types[self.type_num][self.block_num]]

                    self.window.blit(pygame.transform.scale(sprites, (120, 120)),
                                        (display_rect.centerx - 60, display_rect.centery - 60))

            elif self.EDIT_GRID == 4:
                surf.fill(self.color_zones.get(self.type, (50, 200, 50)))
                surf.set_alpha(120)
                self.window.blit(surf, (display_rect.centerx - 32, display_rect.centery - 32))

            else:
                scaled_rect = pygame.Rect(display_rect.centerx - 45, display_rect.centery - 10, 90, 20)
                pygame.draw.rect(self.window, (50, 200, 50), scaled_rect)
                # Add support lines to platforms
                for i in range(3):
                    pygame.draw.line(self.window, (100, 80, 60),
                                        (
                                            int(scaled_rect.x + i * (scaled_rect.width // 2)),
                                            int(scaled_rect.y + scaled_rect.height)
                                        ),
                                        (
                                            int(scaled_rect.x + i * (scaled_rect.width // 2)),
                                            int(scaled_rect.y + scaled_rect.height + 10)
                                        ),
                                        2)
            #except Exception as e:
            #    print("In display map elements ", e)

            if self.thing:
                self.thing.update_sprite()
                self.thing.draw(game=self)

            menu.update(mouse_pos)
            menu.draw()

            self.get_fps()
            # fps_surface = self.font.render(f"{self.item_size}", True, (255, 255, 255))
            # elf.window.blit(fps_surface, (10, 10))

            text.show_text(
                f"X: {self.selectedx} | Y: {self.selectedy}", 10, 40, 1, 99999, self.font_, self.window, 2)
            # pygame.draw.rect(self.window, (255, 5, 255), self.size_rect)
            text.show_text(
                f"{[o.left if i == 0 else o.right for i, o in enumerate(self.platform)]}", 10, 60, 1, 99999, self.font_,
                self.window, 2)

            pygame.display.flip()

            self.clock.tick(self.FPS)

    def author_info(self):

        font = pygame.font.SysFont("serif", 36)

        def back_(object_):
            print("Quit Game Settings!")
            object_.game_info_window = False

        button_data = [
            ("Back", back_, [self])]

        layout = [
            (1 - 0.02 - 0.1, 0.02 + 0.06, 0.1, 0.06)]

        menu = RPGMenu(self.window, font, button_data, layout)
        self.game_info_window = True

        while self.game_info_window:

            self.fix_orientation()

            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    displaying = False
                    break
                    
                if event.type == pygame.JOYAXISMOTION:
                    # HANDLE MENU JOY_BUTTONS EVENTS
                    menu.handle_joy(event, "axis")
                    
                if event.type == pygame.JOYBUTTONDOWN:
                    
                    # HANDLE MENU JOY_BUTTONS EVENTS
                    menu.handle_joy(event)
                    
                if event.type == pygame.KEYDOWN:
                    menu.handle_key(event.key)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    menu.handle_mouse(event)

            self.window.fill((200, 0, 200))

            # Bg
            self.window.blit(self.menu_bg, (0, 0))

            self.get_fps()

            menu.update(mouse_pos)
            menu.draw()

            pygame.display.flip()

            self.clock.tick(self.FPS)

    def player_settings(self):

        displaying = True

        lastx = self.offset_x
        lasty = self.offset_y

        def remove(object_, id_):
            print("Select preferred author_info!")
            try:
                object_.players.remove(players[id_]['player'])
                object_._draw_list_dirty = True
                object_._entities_dirty = True

            except:
                pass
                '''
                players[id_]['remove_player'].text = 'REMOVED'
                '''
                return

        def save(object_, id_):
            print("Saved player {id_} settings!")
            object_.players_config[id_]['player'].name = players[id_]['player_type']
            object_.players_config[id_]['player'].color = players[id_]['player_color']
            object_.players_config[id_]['player'].personalise(2)

        def change_color(object_, id_):
            print("Select preferred game_settings!")
            object_.players_config[id_]['player_color_num'] += 1

        def change_type(object_, id_):
            object_.player_types = [['TNT'], ['Pawn'], ['Warrior'], ['Torch'], ['Archer']]
            object_.player_colors = ['Blue', 'Yellow', 'Red', 'Purple']
            print("Select preferred player_settings!")

            object_.players_config[id_]['player_num'] += 1

        def back_(object_):
            print("Quit Player Edit!")
            object_.editing_player = False

        button_data = [
            ("Back", back_, [self])
        ]

        layout = [
            (1 - 0.02 - 0.1, 0.02 + 0.06, 0.1, 0.06)
        ]

        rel_rect = (0.5 - 0.1, 0.15, 0.2, 0.3)

        self.editing_player = True

        player_types = ['TNT', 'Pawn', 'Warrior', 'Torch', 'Archer']
        player_colors = list(entity_pallete.keys()) #['Blue', 'Yellow', 'Red', 'Purple']
        while self.editing_player:
            for player_ in self.players:
                if player_.id not in self.players_config:
                    for player in self.players:
                        self.players_config[player.id] = {
                            'player': player,
                            'confirm_player': None,
                            'player_type_num': player_types.index(player.name),
                            'player_num': 0,
                            'player_color_num': player_colors.index(player.color),

                        }

                        data = self.players_config[player.id]

                        view_rect = player.viewport.clip(self.window_rect)
                        viewport = self.window.subsurface(view_rect)

                        sw, sh = viewport.get_size()
                        font = pygame.font.SysFont("impact", int(sw * 0.02))
                        menu = RPGMenu(viewport, font, button_data, layout)

                        width = 0.12
                        height = 0.06
                        menu.add([('TYPE', change_type, [self, player.id])],
                                 [(0.5 - (width / 2) - 0.15, 0.2, width, height)])
                        menu.add([('COLOR', change_color, [self, player.id])],
                                 [(0.5 - (width / 2) + 0.15, 0.2, width, height)])

                        menu.add([('SAVE', save, [self, player.id])],
                                 [(0.5 - (width / 2) - 0.12, 0.3, width, height)])
                        menu.add([('REMOVE', remove, [self, player.id])],
                                 [(0.5 - (width / 2) + 0.12, 0.3, width, height)])

                        data['window'] = viewport
                        data['menu'] = menu

                        display_rect = pygame.Rect(
                            int(rel_rect[0] * sw),
                            int(rel_rect[1] * sh),
                            int(rel_rect[2] * sw),
                            int(rel_rect[3] * sh)
                        )
                        data['display_rect'] = display_rect
                    break

            mouse_pos = pygame.mouse.get_pos()

            players = self.players_config
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    for id_ in players:
                        players[id_]['menu'].handle_key(event.key, players[id_]['player'].keyboard_num)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for id_ in players:
                        players[id_]['menu'].handle_mouse(event, players[id_]['player'].viewport.topleft,
                                                          players[id_]['player'].keyboard_num)

                self.player_settings_manager(event)

            self.window.fill((200, 0, 200))

            self.window.blit(self.menu_bg, (0, 0))
            
            self.get_fps()

            pygame.display.flip()

            self.clock.tick(self.FPS)

    def store(self):

        font = pygame.font.SysFont("serif", 36)

        def back_(object_):
            print("Quit Game Settings!")
            object_.game_info_window = False

        button_data = [
            ("Back", back_, [self])]

        layout = [
            (1 - 0.02 - 0.1, 0.02 + 0.06, 0.1, 0.06)]

        menu = RPGMenu(self.window, font, button_data, layout)
        self.game_info_window = True

        while self.game_info_window:

            self.fix_orientation()

            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    displaying = False
                    break
                
                if event.type == pygame.JOYAXISMOTION:
                    # HANDLE MENU JOY_BUTTONS EVENTS
                    menu.handle_joy(event, "axis")
                    
                if event.type == pygame.JOYBUTTONDOWN:
                    
                    # HANDLE MENU JOY_BUTTONS EVENTS
                    menu.handle_joy(event)
                    
                elif event.type == pygame.KEYDOWN:
                    menu.handle_key(event.key)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    menu.handle_mouse(event)

            self.window.fill((200, 0, 200))

            # Bg
            self.window.blit(self.menu_bg, (0, 0))

            self.get_fps()

            menu.update(mouse_pos)
            menu.draw()

            pygame.display.flip()

            self.clock.tick(self.FPS)

    def loading(self):

        font = pygame.font.SysFont("serif", 36)

        self.loading_window = True
        dots = ""
        dt = 0
        while not self.env_ready:

            self.fix_orientation()

            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    displaying = False
                    break
                
                if event.type == pygame.JOYAXISMOTION:
                    pass
                if event.type == pygame.JOYBUTTONDOWN:
                    pass
                elif event.type == pygame.KEYDOWN:
                    pass
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pass

            self.window.fill((200, 0, 200))
            if dt % 20 == 0:
                if len(dots) < 4:
                    dots += "."
                else:
                    dots = ""
            # Bg
            self.window.blit(self.menu_bg, (0, 0))

            label = font.render(f"Loading{dots}", True, (0, 0, 0))
            self.window.blit(label, (self.WIDTH // 2 - label.get_width() // 2, self.HEIGHT // 2 - label.get_height() // 2))

            self.get_fps()

            pygame.display.flip()

            dt += self.clock.tick(self.FPS)


    def exit(self, code=0) -> int:

        self.exiting = True

        sw, sh = self.window.get_rect().size
        font = cache_font(("impact", int(sw * 0.02)))
        
        def yes_(object_):
            print("Entered Yes, Exited!")
            if code == 1:
                pygame.quit()
                quit()
            else:
                object_.sounds.stop("theme")
                object_.exiting = False
                return 0


        def no_(object_):
            print("Canceled!")
            object_.exiting = False

        def back_(object_):
            print("Canceled!")
            object_.exiting = False

        button_data = [
            ("Back", back_, [self]),
            ("YES", yes_, [self]),
            ("NO", no_, [self])
        ]

        layout = [
            (1 - 0.02 - 0.1, 0.02 + 0.06, 0.1, 0.06),
            (0.5 - 0.2 - 0.1, 0.5 - 0.04, 0.2, 0.08),
            (0.5 + 0.1, 0.5 - 0.04, 0.2, 0.08)
        ]

        menu = RPGMenu(self.window, font, button_data, layout)

        menu.buttons[1].color = (100, 10, 5)
        menu.buttons[2].color = (5, 100, 5)
        
        while self.exiting:
            # CAPTURE EVENTS
            self.mouse_pos = pygame.mouse.get_pos()
            self.events = pygame.event.get()

            for event in self.events:
                if event.type == pygame.QUIT:
                    self.exiting = False
                    break
                    
                if event.type == pygame.VIDEORESIZE or event.type == pygame.WINDOWDISPLAYCHANGED:
                    try:
                        print(event)
                        self.fix_orientation()
                        continue
                    except Exception as e:
                        print(e)

                if event.type == pygame.KEYUP:
                    self.keys = pygame.key.get_pressed()

                if event.type == pygame.KEYDOWN:
                    self.keys = pygame.key.get_pressed()

                    # HANDLE MENU BUTTONS EVENTS
                    menu.handle_key(event.key)

                    # EXIT KEYS
                    if self.keys[pygame.K_ESCAPE]:
                        self.exiting = False
                        return
                
                if event.type == pygame.JOYAXISMOTION:
                    # HANDLE MENU JOY_BUTTONS EVENTS
                    menu.handle_joy(event, "axis")
                    
                if event.type == pygame.JOYBUTTONDOWN:
                    
                    # HANDLE MENU JOY_BUTTONS EVENTS
                    menu.handle_joy(event)

                if event.type == pygame.MOUSEBUTTONDOWN:        
                    # HANDLE BUTTON EVENTS
                    menu.handle_mouse(event)


            self.window.fill((200, 0, 200))

            # Bg
            self.window.blit(self.menu_bg, (0, 0))

            text_surface = Settings.display_font.render(
                f'Are you sure you want to EXIT' if code == 1 else 'Are you sure you want to GO BACK STARTUP MENU',
                True, Settings.BLACK)
            rect = text_surface.get_rect()
            rect2 = pygame.Rect(0, 200, rect.width, rect.height)

            rect2.centerx = Settings.WIDTH / 2

            Settings.window.blit(text_surface, (rect2.x, rect2.y))
            
            # MENU BUTTONS
            menu.update(self.mouse_pos)
            menu.draw()
            
            self.get_fps()

            pygame.display.flip()

            self.clock.tick(self.FPS)

    def menu(self):

        self.menu_btn_text = 'BACK'
        var = True

        font = pygame.font.SysFont("serif", 36)

        def start():
            print("Start Game!")
            message_text = "Starting Game..."  # Replace with actual scene transition
            game_started = True

        def mode(object_):
            print("Select preferred mode!")
            object_.modes()

        def game_info(object_):
            print("Select preferred game_info!")
            object_.game_info()

        def author_info(object_):
            print("Select preferred author_info!")
            object_.author_info()

        def store(object_):
            print("Select preferred store!")
            return object_.store()

        def game_settings(object_):
            print("Select preferred game_settings!")
            object_.game_settings()

        def quit_(object_):
            print("Quit Game!")
            object_.running = False
            object_.MENU = False

        def back_(object_):
            print("Quit Menu!")
            object_.MENU = False

        button_data = [
            ("Back", back_, [self]), ("game_settings", game_settings, [self]),
            ("store", store, [self]), ("game_info", game_info, [self]),
            ("author_info", author_info, [self]), ("Quit", quit_, [self])
        ]
        layout = [
            (1 - 0.02 - 0.1, 0.02 + 0.06, 0.1, 0.06),
            (0.5, 0.15, 0.3, 0.06),
            (0.3, 0.25, 0.3, 0.06),
            (0.5, 0.35, 0.3, 0.06),
            (0.3, 0.45, 0.3, 0.06),
            (0.5, 0.55, 0.3, 0.06)
        ]

        view_rect = self.player.viewport.clip(self.window_rect)

        menu = RPGMenu(self.window, font, button_data, layout)

        while self.MENU:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.menu_btn_text = 'MENU'
                    self.MENU = False
                    break
                
                if event.type == pygame.JOYAXISMOTION:
                    # HANDLE MENU JOY_BUTTONS EVENTS
                    menu.handle_joy(event, "axis")
                    
                if event.type == pygame.JOYBUTTONDOWN:
                    
                    # HANDLE MENU JOY_BUTTONS EVENTS
                    menu.handle_joy(event)
                    
                if event.type == pygame.VIDEORESIZE or event.type == pygame.WINDOWDISPLAYCHANGED:
                    try:
                        print(event)
                        self.fix_orientation()
                        continue
                    except Exception as e:
                        print(e)

                if event.type == pygame.KEYDOWN:
                    menu.handle_key(event.key)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    menu.handle_mouse(event)

        
            # self.update_menu_btns_pos()

            self.window.fill((200, 0, 200))

            # Bg
            self.window.blit(self.menu_bg, (0, 0))

            self.get_fps()

            menu.update(mouse_pos)
            menu.draw()

            pygame.display.flip()

            self.clock.tick(self.FPS)

    def game_over(self):

        typewriter = TypeText(
            "You awake in the dark.\nA voice whispers:\n'Five floors... then I let you go.'",
            pos=(50, 400),
            font=Settings.font,
            color=(255, 255, 255),
            speed=20  # 20 characters per second
        )
        # self.sounds.play_bg('theme',  -1)

        run = True

        while run:
            self.fix_orientation()

            for event in pygame.event.get():

                if event.type == pygame.MOUSEBUTTONUP:
                    if not self.SPECTATING_BTN.indicate:
                        self.SPECTATING_BTN.clicked = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.SPECTATING_BTN.is_clicked(event.pos, []):
                        self.spectate()

                if event.type == pygame.QUIT:
                    run = False
                    break
                if event.type == pygame.MOUSEBUTTONDOWN and not typewriter.done:
                    typewriter.skip()  # Skip to full text

            self.window.fill((105, 55, 55))

            # Bg
            self.window.blit(self.menu_bg, (0, 0))
            typewriter.update()
            typewriter.draw(self.window, True)
            self.SPECTATING_BTN.draw(self.window)

            self.get_fps()

            pygame.display.flip()

            self.clock.tick(self.FPS)

        pygame.quit()
        quit()

    def spectate(self):

        displaying = True
        self.SPECTATING = True
        self.spectating_btn_text = 'BACK'
        lastx = self.offset_x
        lasty = self.offset_y
        clicked = False
        font = pygame.font.SysFont("serif", 30)

        def menu(_object):
            print("Started Menu!")
            _object.MENU = True
            _object.pause_start = pygame.time.get_ticks()
            _object.menu()
            _object.pause_total += pygame.time.get_ticks() - _object.pause_start
            print("Menu Ended!")

        def exit_spectate(_object):
            _object.SPECTATING = False
            print("Exiting Spectate Window!")

        def view(_object):
            _object.VIEW = not _object.VIEW
            print(f"Object Info is {'ON' if _object.VIEW else 'OFF'}")

        button_data = [
            ("MENU", menu, [self]), 
            ("BACK", exit_spectate, [self]), 
            ("VIEW", view, [self])
        ]

        layout = [
            (1 - 0.08 - 0.02, 0.03, 0.08, 0.06),  
            (0.5 - 0.2 - 0.03, 0.03, 0.2, 0.06),
            (0.5 + 0.03, 0.03, 0.2, 0.06)
        ]

        menu = RPGMenu(self.window, font, button_data, layout)
        
        while self.SPECTATING:
            # CAPTURE EVENTS
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        clicked = True
                    
                    # HANDLE BUTTON EVENTS
                    menu.handle_mouse(event)
                
                elif event.type == pygame.KEYDOWN:
                    self.keys = pygame.key.get_pressed()

                    # HANDLE MENU BUTTONS EVENTS
                    menu.handle_key(event.key)

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        clicked = False
                
                elif event.type == pygame.MOUSEMOTION:
                    if clicked:
                        self.offset_x -= event.rel[0]
                        self.offset_y -= event.rel[1]

                elif event.type == pygame.QUIT:
                    self.SPECTATING = False
                    break

                elif event.type == pygame.VIDEORESIZE or event.type == pygame.WINDOWDISPLAYCHANGED:
                    try:
                        print(event)
                        self.fix_orientation()
                        continue
                    except Exception as e:
                        print(e)
                
                
            self.handle_keypress(self.player)
            
            self.update_game_logic()

            self.window.fill((20, 0, 20))

            # PARALLAX BACKGROUND
            self.bg_particles = parallax_bg(
                self.window, 
                Settings.WIDTH, Settings.HEIGHT, 
                self.bg_particles, self.master_clock,
                threshold=20, height=0,
                parallax_color=Settings.PARALLAX, bg_color=Settings.BG_COLOR
            )

            self.draw_main()    
            
            # MENU BUTTONS
            menu.update(mouse_pos)
            menu.draw()

            # GAME FPS
            self.get_fps()
            
            self.exec(self.clean)
            
            pygame.display.flip()

            # HANDLE DELTA TIME
            raw_dt = self.clock.tick(self.FPS) / 1000.0
            self.game_speed = min(self.max_game_speed, self.game_speed + 0.1)
            self.dt = round(min(0.1, raw_dt * self.game_speed), 3)

            self.master_clock += int(raw_dt * 80)