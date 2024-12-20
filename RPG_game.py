import pygame, random, time
from pygame_util import SceneManager, Scene

class Tile:
    def __init__(self, 
                 x, 
                 y, 
                 sprite: pygame.Surface, 
                 sprite_id: int) -> None:
        self.x = x
        self.y = y
        self.sprite = sprite
        self.sprite_id = sprite_id

    def update(self) -> None:
        pass

    def render(self) -> None:
        pass

class Tileset:
    def __init__(self,
                 filename: str,
                 original_tilesize: int,
                 scale_factor: int = 1,
                 sprites = None) -> None:
        if sprites is None:
            self.tilesheet = pygame.image.load(filename).convert_alpha()
        else:
            self.tilesheet = sprites

        self.tileset = {} # dict of tile ids to tile images 
        self.tilesize = original_tilesize
        self.scale_factor = scale_factor
        self.scaled_size = self.tilesize * self.scale_factor

        tile_id = 0
        for y in range(int(self.tilesheet.get_height()/self.tilesize)):
            for x in range(int(self.tilesheet.get_width()/self.tilesize)):
                tile_rect = pygame.Rect(x*self.tilesize, 
                                        y*self.tilesize, 
                                        self.tilesize, 
                                        self.tilesize)
                tile_image = self.tilesheet.subsurface(tile_rect)

                tile_image = pygame.transform.scale(tile_image,
                                                    (tile_image.get_width() * self.scale_factor,
                                                    tile_image.get_height() * self.scale_factor))
                
                self.tileset[tile_id] = tile_image

                tile_id += 1

    def get_tileset(self) -> dict:
        return self.tileset
    
    def get_tile_sprite(self, id: int) -> pygame.Surface:
        return self.tileset[id]

class Tilemap:
    def __init__(self,
                 map: list[list],
                 tileset: Tileset) -> None:
        self.tileset = tileset
        self.map_spec = map
        self.map = [[]]
        self.tilesize = self.tileset.scaled_size

        # Create map tiles from spec
        x_coord = 0
        y_coord = 0
        for y in self.map_spec:
            row = []
            for x in y:
                sprite = self.tileset.get_tile_sprite(x)
                tile = Tile(x_coord, y_coord, sprite, x)
                row.append(tile)
                x_coord += self.tilesize
            y_coord += self.tilesize
            x_coord = 0
            self.map.append(row)

class Camera:
    def __init__(self, screen: pygame.surface, subject) -> None:
        self.screen = screen
        self.screen_w = screen.get_width()
        self.screen_h = screen.get_height()

        self.subject = subject
        self.camera_adjustment_x = 0
        self.camera_adjustment_y = 0

        # Initial camera adjustment
        self.camera_adjustment_x = (self.screen_w/2) - self.subject.x
        self.camera_adjustment_y = (self.screen_h/2) - self.subject.y

    def get_camera_adjustment(self) -> tuple:
        return (self.camera_adjustment_x, self.camera_adjustment_y)

    def update(self, dt) -> None:
        self.camera_adjustment_x = (self.screen_w/2) - self.subject.x
        self.camera_adjustment_y = (self.screen_h/2) - self.subject.y

class Button:
    def __init__(self,
                 x,
                 y,
                 text: str) -> None:
        self.x = x
        self.y = y

        self.font = pygame.font.SysFont("Calibri", 36)
        self.color = "white"
        self.text = text

        self.text_surface = self.font.render(self.text, True, self.color)
        self.rect = self.text_surface.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.hovered = False

        self.event = lambda: print("Default Button")

    def update(self, dt):
        if self.hovered is True:
            self.color = "blue"
        else:
            self.color = "white"
        self.text_surface = self.font.render(self.text, True, self.color)

    def set_hover(self, hovered: bool):
        self.hovered = hovered

    def register_event(self, func):
        self.event = func

    def render(self, screen: pygame.surface):
        screen.blit(self.text_surface, (self.x, self.y,))

class Player:
    def __init__(self, spritesheets: dict, x, y) -> None:
        self.x = x
        self.y = y
        self.velocity = 250
        self.direction = "down"
        self.moving = False

        self.animations = AnimationManager(spritesheets, 16, 4)

        # Walking animations
        self.animations.register_animation("walking_right", [3, 7, 11, 15], "walking_animations")
        self.animations.register_animation("walking_left", [2, 6, 10, 14], "walking_animations")
        self.animations.register_animation("walking_up", [1, 5, 9, 13], "walking_animations")
        self.animations.register_animation("walking_down", [0, 4, 8, 12], "walking_animations")

        # Stationary sprites
        self.animations.register_animation("stationary_down", [0, 0, 0], "walking_animations")
        self.animations.register_animation("stationary_up", [1, 1, 1], "walking_animations")
        self.animations.register_animation("stationary_left", [2, 2, 2], "walking_animations")
        self.animations.register_animation("stationary_right", [3, 3, 3], "walking_animations")

        # Attacks
        self.animations.register_animation("attack_down", [0, 0, 0], "attack_animation")
        self.animations.register_animation("attack_up", [1, 1, 1], "attack_animation")
        self.animations.register_animation("attack_left", [2, 2, 2], "attack_animation")
        self.animations.register_animation("attack_right", [3, 3, 3], "attack_animation")

    def move(self, dt) -> None:
        if self.direction == "up":
            self.y -= self.velocity * dt
        elif self.direction == "down":
            self.y += self.velocity * dt
        elif self.direction == "left":
            self.x -= self.velocity * dt
        elif self.direction == "right":
            self.x += self.velocity * dt

    def attack(self) -> None:
        self.animations.activate_animation("attack_" + self.direction, 0.1, False)

    def set_direction(self, new_direction: str) -> None:
        self.direction = new_direction

    def start_moving(self, animation: str) -> None:
        self.moving = True
        self.animations.activate_animation(animation, 0.15, True)

    def stop_moving(self) -> None:
        self.moving = False
        self.animations.activate_animation("stationary_" + self.direction, 0.1, True)

    def update(self, dt) -> None:
        if self.moving:
            self.move(dt)
        
        self.animations.update(dt)
    
    def render(self, screen: pygame.surface, camera_adjust: tuple) -> None:
        screen.blit(self.animations.get_current_sprite(), (self.x + camera_adjust[0], self.y + camera_adjust[1]))

class Enemy:
    def __init__(self, spritesheets: dict, x, y) -> None:
        self.spritesheets = spritesheets
        self.x = x
        self.y = y

        self.animations = AnimationManager(spritesheets, 50, 4)
        self.animations.register_animation("idle", [0, 1, 2, 3, 4], "enemy_idle")
        self.animations.activate_animation("idle", 0.1, True)
    
    def update(self, dt):
        self.animations.update(dt)

    def render(self, screen: pygame.surface, camera_adjust: tuple):
        screen.blit(self.animations.get_current_sprite(), (self.x + camera_adjust[0], self.y + camera_adjust[1]))


class MenuScene(Scene):
    def __init__(self, 
                 manager: SceneManager, 
                 screen: pygame.Surface, 
                 sprites: dict) -> None:
        super().__init__(manager, screen, sprites)

        self.previous_time = None

        # Create buttons
        self.quit_button = Button(500, 400, "Quit Game")
        self.start_button = Button(500, 300, "Start Game")

        # Create button events
        def quit_button():
            self.manager.quit = True

        def start_button():
            self.manager.set_scene("main")

        self.quit_button.register_event(quit_button)
        self.start_button.register_event(start_button)

        self.buttons = [self.quit_button, self.start_button]

    def update(self) -> None:
        if self.previous_time is None:
            self.previous_time = time.time()

        # Delta time
        now = time.time()
        dt = now - self.previous_time
        self.previous_time = now

        mouse_x, mouse_y = pygame.mouse.get_pos()

        for b in self.buttons:
            if b.hovered == False and b.rect.collidepoint(mouse_x, mouse_y):
                b.hovered = True
            if b.hovered == True and not b.rect.collidepoint(mouse_x, mouse_y):
                b.hovered = False

        self.quit_button.update(dt)
        self.start_button.update(dt)
    
    def render(self) -> None:
        self.screen.fill("black")

        self.quit_button.render(self.screen)
        self.start_button.render(self.screen)

        pygame.display.update()

    def poll_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.manager.quit_game()
        # Mouse detection
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for b in self.buttons:
                    if b.hovered:
                        b.event()

class Projectile:
    def __init__(self, spritesheets: dict, x, y) -> None:
        self.spritesheets = spritesheets
        self.x = x
        self.y = y
        self.velocity = 500
        self.direction = "right"

        self.animation = AnimationManager(spritesheets, 16, 2)
        self.animation.register_animation("projectile", [0, 1, 2, 3, 4], "projectile")
        self.animation.activate_animation("projectile", 0.1, True)

    def move(self, dt) -> None:
        if self.direction == "up":
            self.y -= self.velocity * dt
        elif self.direction == "down":
            self.y += self.velocity * dt
        elif self.direction == "left":
            self.x -= self.velocity * dt
        elif self.direction == "right":
            self.x += self.velocity * dt

    def set_direction(self, new_direction: str) -> None:
        self.direction = new_direction

    def update(self, dt):
        self.animation.update(dt)
        self.move(dt)

    def render(self, screen: pygame.surface, camera_adjust: tuple):
        screen.blit(self.animation.get_current_sprite(), (self.x + camera_adjust[0], self.y + camera_adjust[1]))

class Animation:
    def __init__(self,
                 name: str,
                 tileset: Tileset,
                 keyframes: list[int]) -> None:
        self.name = name
        self.tileset = tileset
        self.keyframes = keyframes

        self.current_sprite_id = 0
        self.loop_animation = False
        self.animation_frequency = 0
        self.current_keyframe = 0
        self.keyframe_time = 0

    def get_current_sprite(self) -> pygame.surface:
        return self.tileset.get_tile_sprite(self.current_sprite_id)

    def activate_animation(self, frequency: float, loop: bool):
        self.animation_frequency = frequency
        self.loop_animation = loop
    
    def deactivate_animation(self):
        self.animation_frequency = 0
        self.loop_animation = False

    def update(self, dt) -> None:
        self.keyframe_time += dt

        if self.keyframe_time >= self.animation_frequency:
            if len(self.keyframes) - 1 <= self.current_keyframe:

                if self.loop_animation is True:
                    self.current_keyframe = 0
                else:
                    self.deactivate_animation()
            else:
                self.current_keyframe += 1
                self.current_sprite_id = self.keyframes[self.current_keyframe]

            self.keyframe_time = 0

class AnimationManager:
    def __init__(self, 
                 spritesheets: dict,
                 tilesize: int,
                 scale: int) -> None:
        
        self.tilesets = {}

        for s in spritesheets:
            tileset = Tileset("none", tilesize, scale, spritesheets[s])
            self.tilesets[s] = tileset

        self.animations = {}

        self.current_tileset = None

        self.active_animation = Animation("dummy", self.tilesets[list(self.tilesets.keys())[0]], [0])

    def register_animation(self, name: str, sprite_ids: list[int], tileset: str):
        self.animations[name] = Animation(name, self.tilesets[tileset], sprite_ids)

    def get_current_sprite(self) -> pygame.surface:
        if self.active_animation is not None:
            return self.active_animation.get_current_sprite()
        else:
            return pygame.surface((0, 0))

    def update(self, dt):
        if self.active_animation is not None:
            self.active_animation.update(dt)

    def activate_animation(self, animation: str, frequency: float, loop: bool):
        self.active_animation = self.animations[animation]
        self.active_animation.animation_frequency = frequency
        self.active_animation.loop_animation = loop
    
    def deactivate_animation(self):
        self.active_animation = None

class MainScene(Scene):
    def __init__(self, manager: SceneManager, screen: pygame.Surface, sprites: dict) -> None:
        super().__init__(manager, screen, sprites)

        self.previous_time = None	

        MAP     =      [[101,91,91,91,91,91,91,91,91,91,91,91,91,91,91,91,91,91,91,91,91,91,91,91,102], 
                        [81,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 79], 
                        [81,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,79], 
                        [81,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,71, 0, 0, 0, 0, 0, 0, 0, 0, 0,79], 
                        [81, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,79],
                        [81, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,79],
                        [81, 0, 0, 0, 0, 0, 0, 0, 0,71, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,79],
                        [81, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,79],
                        [81, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,79],
                        [81, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,71, 0, 0, 0, 0, 0, 0, 0, 0, 0,79],
                        [81, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,79],
                        [112,69,69,69,69,69,69,69,69,69,69,69,69,69,69,69,69,69,69,69,69,69,69,69,113]]

        self.tileset = Tileset(r"Games\gfx\rpg_sprites.png", 16, 4)
        # Create our tilemap
        self.tilemap = Tilemap(MAP, self.tileset)

        enemy_anims = {"enemy_idle": self.sprites["enemy_idle"]}
        self.enemy = Enemy(enemy_anims, 500, 500)

        player_anims = {"walking_animations": self.sprites["player_walk"],
                        "attack_animation": self.sprites["player_attack"]}
        self.player = Player(player_anims, 100, 100)  

        self.camera = Camera(self.screen, self.player)

        # User input system
        self.keybinds = {pygame.K_w: "up",
                         pygame.K_s: "down",
                         pygame.K_a: "left",
                         pygame.K_d: "right"}
        
        self.keystack = []
        self.current_key = None

        self.projectiles = []

    def update(self) -> None:

        if self.previous_time is None: # First run through the loop needs a previous_time value to compute delta time
            self.previous_time = time.time()
        # Delta time
        now = time.time()
        dt = now - self.previous_time
        self.previous_time = now

        self.enemy.update(dt)
        self.player.update(dt)

        for p in self.projectiles:
            p.update(dt)

        self.camera.update(dt)

    def render(self) -> None:
        # Clear screen
        self.screen.fill((30, 124, 184))

        for y in self.tilemap.map:
            for x in y:
                self.screen.blit(x.sprite, (x.x + self.camera.get_camera_adjustment()[0],
                                            x.y + self.camera.get_camera_adjustment()[1]))

        self.enemy.render(self.screen, self.camera.get_camera_adjustment())
        self.player.render(self.screen, self.camera.get_camera_adjustment())

        for p in self.projectiles:
            p.render(self.screen, self.camera.get_camera_adjustment())

        # Update display
        pygame.display.update()

    def poll_events(self) -> None:
        for event in pygame.event.get():

            if event.type == pygame.QUIT: # If the user closes the window
                self.manager.quit_game()         

            # Attack controls
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.player.attack()
                p = Projectile({"projectile": self.sprites["projectile"]}, self.player.x, self.player.y)
                p.set_direction(self.player.direction)
                self.projectiles.append(p)


            if event.type == pygame.KEYDOWN and event.key in self.keybinds:
                self.keystack.append(event.key)

            if event.type == pygame.KEYUP and event.key in self.keybinds:
                self.keystack.remove(event.key)

            if len(self.keystack) > 0:
                if self.current_key != self.keystack[-1]:
                    self.current_key = self.keystack[-1]

                    self.player.set_direction(self.keybinds[self.current_key])
                    self.player.start_moving("walking_" + self.keybinds[event.key])

            if len(self.keystack) == 0:
                self.current_key = None
                self.player.stop_moving()

class Game:
    def __init__(self) -> None:
        # Initialize global game variables
        pygame.init() 
        self.screen = pygame.display.set_mode((1280, 720))
        self.running = True
        self.sprites = self.load_sprites()

        # Scene system
        self.scene_manager = SceneManager()

        scenes = {"main": MainScene(self.scene_manager, self.screen, self.sprites),
                  "menu": MenuScene(self.scene_manager, self.screen, self.sprites)}
        self.scene_manager.initialize(scenes, "menu")


    # MAIN GAME LOOP #
    def run(self) -> None:
        self.previous_time = time.time()
        while self.running:

            self.scene_manager.current_scene.poll_events()
            self.scene_manager.current_scene.update()
            self.scene_manager.current_scene.render()

            if self.scene_manager.quit == True:
                self.running = False    

        pygame.quit()

    # Load sprite textures into pygame as surfaces. 
    # Returns a dictionary of names to surfaces.
    def load_sprites(self) -> dict: 
        sprites = {}

        sprites["enemy_idle"] = pygame.image.load(r"Games\gfx\enemy_idle.png").convert_alpha()
        sprites["player_walk"] = pygame.image.load(r"Games\gfx\player_animations.png").convert_alpha()
        sprites["player_attack"] = pygame.image.load(r"Games\gfx\attack.png").convert_alpha()
        sprites["projectile"] = pygame.image.load(r"Games\gfx\projectile.png").convert_alpha()

        return sprites

g = Game()
g.run()