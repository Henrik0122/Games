import pygame
import random
import time


class Entity:
    def __init__(self, x: float, y: float, velocity: float, sprite: pygame.Surface) -> None:
        self.x = x
        self.y = y
        self.velocity = velocity
        self.sprite = sprite

    def update(self, dt) -> None:
        pass

    def render(self, screen: pygame.Surface) -> None:
        pass


class Player(Entity):
    def __init__(self,
                 x: float,
                 y: float,
                 velocity: float,
                 sprite: pygame.Surface,
                 gravity_constant: float) -> None:
        super().__init__(x, y, velocity, sprite)
        self.gravity_constant = gravity_constant

    def update(self, dt) -> None:
        self.y += self.velocity * dt
        self.velocity += self.gravity_constant * dt

    def render(self, screen: pygame.Surface) -> None:
        screen.blit(self.sprite, (self.x, self.y))


class Obstacle(Entity):

    class ObstacleBlock(Entity):
        def __init__(self,
                     x: float,
                     y: float,
                     velocity: float,
                     sprite: pygame.Surface) -> None:

            super().__init__(x, y, velocity, sprite)

        def update(self, dt) -> None:
            self.x += self.velocity * dt

        def render(self, screen: pygame.Surface) -> None:
            screen.blit(self.sprite, (self.x, self.y))

    def __init__(self,
                 x: float,
                 y: float,
                 velocity: float,
                 screen_height: int,
                 gap_height: int,  # Number of blocks missing to form gap
                 # Number of blocks from the top of the screen that the gap is located at.
                 gap_loc: int,
                 sprite: pygame.Surface) -> None:
        super().__init__(x, y, velocity, sprite)
        self.screen_height = screen_height
        self.gap_height = gap_height
        self.gap_loc = gap_loc
        self.BLOCK_SIZE = 48  # Obstacle block sprite size

        # Calculate the number of blocks required to fill the screen
        self.num_blocks = round(self.screen_height/self.BLOCK_SIZE)

        # Calculate gap
        self.gap_range = (self.gap_loc, self.gap_loc + self.gap_height)

        self.blocks = self.create_blocks()

    def create_blocks(self) -> list[ObstacleBlock]:
        o = []
        current_block = 0
        for i in range(self.num_blocks):
            if i < self.gap_range[0] or i > self.gap_range[1]:
                o.append(Obstacle.ObstacleBlock(self.x,
                                                current_block,
                                                self.velocity,
                                                self.sprite))
            current_block += self.BLOCK_SIZE
        return o

    def update(self, dt) -> None:
        self.x += self.velocity * dt
        for b in self.blocks:
            b.update(dt)

    def render(self, screen: pygame.Surface) -> None:
        for b in self.blocks:
            b.render(screen)


class Environment:
    def __init__(self,
                 player: Player,
                 screen: pygame.Surface,
                 sprites: dict,
                 freq: int,
                 obstacle_velocity: float,
                 obstacle_gap: int) -> None:

        self.obstacle_velocity = obstacle_velocity
        self.obstacle_gap = obstacle_gap
        self.freq = freq
        self.screen = screen
        self.player = player
        self.sprites = sprites

        self.obstacles = []  # All of the currently active obstacles
        self.obstacle_spawn_point = 1280
        self.new_obstacle_timer = 0

    def add_obstacle(self, obstacle: Obstacle) -> None:
        self.obstacles.append(obstacle)

    def remove_obstacle(self) -> None:
        self.obstacles.pop(0)

    def update_obstacles(self, dt) -> None:
        for o in self.obstacles:
            o.update(dt)
            if o.x < -200:
                self.remove_obstacle()

        if self.new_obstacle_timer > self.freq:  # Time to spawn a new obstacle

            gap = random.randint(2, 10)

            o = Obstacle(self.obstacle_spawn_point,
                         0,
                         self.obstacle_velocity,
                         self.screen.get_height(),
                         self.obstacle_gap,
                         gap,
                         self.sprites["obstacle"])
            self.add_obstacle(o)
            self.new_obstacle_timer = 0

        self.new_obstacle_timer += 1

    def update(self, dt) -> None:
        self.update_obstacles(dt)

    def render(self, screen: pygame.Surface) -> None:
        for o in self.obstacles:
            o.render(screen)


class SceneManager:
    def __init__(self) -> None:
        self.scenes = {}
        self.quit = False

    def initialize(self, scenes: dict, starting_scene: str) -> None:
        self.scenes = scenes
        self.current_scene = self.scenes[starting_scene]

    def set_scene(self, new_scene: str) -> None:
        self.current_scene = self.scenes[new_scene]

    def get_scene(self):
        return self.current_scene

    def quit_game(self) -> None:
        self.quit = True


class Scene:
    def __init__(self,
                 manager: SceneManager,
                 screen: pygame.Surface,
                 sprites: dict) -> None:
        self.manager = manager
        self.screen = screen
        self.sprites = sprites

    def update(self) -> None:
        pass

    def render(self) -> None:
        pass

    def poll_events(self) -> None:
        pass


class MainScene(Scene):
    def __init__(self,
                 manager: SceneManager,
                 screen: pygame.Surface,
                 sprites: dict) -> None:
        super().__init__(manager, screen, sprites)

        self.previous_time = None

        # GAME CONSTANTS
        self.GRAVITY_CONSTANT = 1700
        self.PLAYER_VEL = 200
        self.JUMP_CONSTANT = -450
        self.OBS_FREQ = 800
        self.OBS_VEL = -200
        self.OBS_GAP = 2

        self.player = Player(self.screen.get_width()/2,
                             self.screen.get_height()/2,
                             self.PLAYER_VEL,
                             self.sprites["player"],
                             self.GRAVITY_CONSTANT)

        self.env = Environment(self.player,
                               self.screen,
                               self.sprites,
                               self.OBS_FREQ,
                               self.OBS_VEL,
                               self.OBS_GAP)

    def update(self) -> None:
        if self.previous_time is None:  # First run through the loop
            self.previous_time = time.time()

        # Delta time
        now = time.time()
        dt = now - self.previous_time
        self.previous_time = now

        self.player.update(dt)
        self.env.update(dt)

    def render(self) -> None:
        self.screen.fill("black")

        self.player.render(self.screen)
        self.env.render(self.screen)

        pygame.display.update()

    def poll_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.manager.quit_game()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.velocity = self.JUMP_CONSTANT


class StartScene(Scene):
    pass


class DeathScene(Scene):
    pass


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.running = True
        self.screen = pygame.display.set_mode((1280, 720))
        self.sprites = self.load_sprites()

        self.scene_manager = SceneManager()
        scenes = {"main": MainScene(
            self.scene_manager, self.screen, self.sprites)}
        self.scene_manager.initialize(scenes, "main")

    def run(self) -> None:
        while self.running:

            self.scene_manager.current_scene.poll_events()
            self.scene_manager.current_scene.update()
            self.scene_manager.current_scene.render()

            if self.scene_manager.quit == True:
                self.running = False

        pygame.quit()

    def load_sprites(self) -> dict:
        sprites = {}

        sprites["player"] = pygame.image.load("gfx/ball.png").convert_alpha()
        sprites["obstacle"] = pygame.image.load(
            "gfx/block.png").convert_alpha()

        return sprites


g = Game()
g.run()
