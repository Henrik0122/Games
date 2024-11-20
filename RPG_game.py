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

        self.tileset = Tileset("gfx/rpg_sprites.png", 16, 4)
        # Create our tilemap
        self.tilemap = Tilemap(MAP, self.tileset)   


    def update(self) -> None:

        if self.previous_time is None: # First run through the loop needs a previous_time value to compute delta time
            self.previous_time = time.time()
        # Delta time
        now = time.time()
        dt = now - self.previous_time
        self.previous_time = now

    def render(self) -> None:
        # Clear screen
        self.screen.fill("black")

        for y in self.tilemap.map:
            for x in y:
                self.screen.blit(x.sprite, (x.x, x.y))

        # Update display
        pygame.display.update()

    def poll_events(self) -> None:
        for event in pygame.event.get():

            if event.type == pygame.QUIT: # If the user closes the window
                self.manager.quit_game()         

class Game:
    def __init__(self) -> None:
        # Initialize global game variables
        pygame.init() 
        self.screen = pygame.display.set_mode((1280, 720))
        self.running = True
        self.sprites = self.load_sprites()

        # Scene system
        self.scene_manager = SceneManager()

        scenes = {"main": MainScene(self.scene_manager, self.screen, self.sprites)}
        self.scene_manager.initialize(scenes, "main")


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

        return sprites

g = Game()
g.run()