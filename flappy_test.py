import pygame
import random
import time
import os


class Entity:
    def __init__(self, x: float, y: float, velocity: float, sprite: pygame.Surface) -> None:
        self.x = x
        self.y = y
        self.velocity = velocity
        self.sprite = sprite

    def update(self, dt) -> None:
        pass

    def render(self, screen: pygame.Surface) -> None:
        screen.blit(self.sprite, (self.x, self.y))


class Player(Entity):
    def __init__(self, x: float, y: float, velocity: float, sprite: pygame.Surface, gravity_constant: float) -> None:
        super().__init__(x, y, velocity, sprite)
        self.gravity_constant = gravity_constant

    def update(self, dt) -> None:
        self.y += self.velocity * dt
        self.velocity += self.gravity_constant * dt


class Obstacle(Entity):
    class ObstacleBlock(Entity):
        def update(self, dt) -> None:
            self.x += self.velocity * dt

    def __init__(self, x: float, y: float, velocity: float, screen_height: int, gap_height: int, gap_loc: int,
                 sprite: pygame.Surface) -> None:
        super().__init__(x, y, velocity, sprite)
        self.screen_height = screen_height
        self.gap_height = gap_height
        self.gap_loc = gap_loc
        self.BLOCK_SIZE = 48
        self.num_blocks = round(self.screen_height / self.BLOCK_SIZE)
        self.gap_range = (self.gap_loc, self.gap_loc + self.gap_height)
        self.blocks = self.create_blocks()

    def create_blocks(self) -> list:
        blocks = []
        for i in range(self.num_blocks):
            block_y = i * self.BLOCK_SIZE
            if not (self.gap_range[0] * self.BLOCK_SIZE <= block_y < self.gap_range[1] * self.BLOCK_SIZE):
                blocks.append(Obstacle.ObstacleBlock(
                    self.x, block_y, self.velocity, self.sprite))
        return blocks

    def update(self, dt) -> None:
        self.x += self.velocity * dt
        for block in self.blocks:
            block.update(dt)

    def render(self, screen: pygame.Surface) -> None:
        for block in self.blocks:
            block.render(screen)


class Environment:
    def __init__(self, player: Player, screen: pygame.Surface, sprites: dict, freq: float, obstacle_velocity: float,
                 obstacle_gap: int) -> None:
        self.obstacle_velocity = obstacle_velocity
        self.obstacle_gap = obstacle_gap
        self.freq = freq
        self.screen = screen
        self.player = player
        self.sprites = sprites
        self.obstacles = []
        self.obstacle_spawn_point = screen.get_width()
        self.new_obstacle_timer = 0

    def add_obstacle(self, obstacle: Obstacle) -> None:
        self.obstacles.append(obstacle)

    def remove_obstacle(self) -> None:
        self.obstacles = [obs for obs in self.obstacles if obs.x > -200]

    def update_obstacles(self, dt) -> None:
        for obstacle in self.obstacles:
            obstacle.update(dt)
        self.remove_obstacle()

        if self.new_obstacle_timer > self.freq:
            gap_loc = random.randint(2, 10)
            new_obstacle = Obstacle(
                self.obstacle_spawn_point,
                0,
                self.obstacle_velocity,
                self.screen.get_height(),
                self.obstacle_gap,
                gap_loc,
                self.sprites["obstacle"]
            )
            self.add_obstacle(new_obstacle)
            self.new_obstacle_timer = 0

        self.new_obstacle_timer += dt

    def update(self, dt) -> None:
        self.update_obstacles(dt)

    def render(self, screen: pygame.Surface) -> None:
        for obstacle in self.obstacles:
            obstacle.render(screen)


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.running = True
        self.screen = pygame.display.set_mode((1280, 720))
        self.sprites = self.load_sprites()
        self.previous_time = time.time()

        self.GRAVITY_CONSTANT = 1700
        self.PLAYER_VEL = 200
        self.JUMP_CONSTANT = -450
        self.OBS_FREQ = 2.0
        self.OBS_VEL = -200
        self.OBS_GAP = 2

        self.player = Player(self.screen.get_width() / 2, self.screen.get_height() / 2, self.PLAYER_VEL,
                             self.sprites["player"], self.GRAVITY_CONSTANT)
        self.env = Environment(
            self.player, self.screen, self.sprites, self.OBS_FREQ, self.OBS_VEL, self.OBS_GAP)

    def poll_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.player.velocity = self.JUMP_CONSTANT

    def update(self) -> None:
        now = time.time()
        dt = now - self.previous_time
        self.previous_time = now
        self.player.update(dt)
        self.env.update(dt)

    def render(self) -> None:
        self.screen.fill((0, 0, 0))
        self.player.render(self.screen)
        self.env.render(self.screen)
        pygame.display.update()

    def load_sprites(self) -> dict:
        sprites = {}
        sprites["player"] = pygame.image.load(
            os.path.join("gfx", "ball.png")).convert_alpha()
        sprites["obstacle"] = pygame.image.load(
            os.path.join("gfx", "block.png")).convert_alpha()
        return sprites

    def run(self) -> None:
        while self.running:
            self.poll_events()
            self.update()
            self.render()
        pygame.quit()


if __name__ == "__main__":
    Game().run()
