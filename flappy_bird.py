import pygame
import random
import time

import pygame.surface


class Entity:
    def __init__(self, x: float, y: float, velocity: float, sprite: pygame.surface) -> None:
        self.x = x
        self.y = y
        self.velocity = velocity
        self.sprite = sprite

    def update(self, dt) -> None:
        pass

    def render(self, screen: pygame.surface) -> None:
        pass


class Player(Entity):
    def __init__(self, x: float, y: float, velocity: float, sprite: pygame.surface, gravity_constant: float) -> None:
        super().__init__(x, y, velocity, sprite)
        self.gravity_constant = gravity_constant


    def update(self, dt) -> None:
        self.y += self.velocity * dt
        self.velocity += self.gravity_constant * dt

    def render(self, screen: pygame.surface) -> None:
        screen.blit(self.sprite, (self.x, self.y))

class Obstacle(Entity):

    class ObtacleBlocks(Entity):
        def __init__(self, x: float, y: float, velocity: float, sprite: pygame.surface) -> None:
            super().__init__(x, y, velocity, sprite)

        def update(self, dt) -> None:
            self.x += self.velocity * dt
        
        def render(self, screen: pygame.surface) -> None:
            screen.blit(self.sprite, (self.x, self.y))
        
    def __init__(self, x: float,
                y: float,
                velocity: float,
                screen_height: int,
                gap_height: int,
                gap_loc: int,
                sprite: pygame.surface) -> None:
        super().__init__(x, y, velocity, sprite)

        self.screen_height = screen_height
        self.gap_height = gap_height
        self.gap_loc = gap_loc
        self.BLOCK_SIZE = 48

        #calculate the number of blocks required to fill the screen
        self.num_blocks = round(self.screen_height/self.BLOCK_SIZE)

        #calculate gap
        self.gap_range = (self.gap_loc, self.gap_loc + self.gap_height)

        self.blocks = self.create_blocks()

    def create_blocks(self) -> list[ObtacleBlocks]:
        o = []
        current_block = 0
        for i in range(self.num_blocks):
            if i < self.gap_range[0] or i > self.gap_range[1]:
                o.append(Obstacle.ObtacleBlocks(self.x,
                                                current_block,
                                                self.velocity,
                                                self.sprite))
                current_block += self.BLOCK_SIZE
        return o
    
    def update(self, dt) -> None:
        self.x += self.velocity * dt
        for b in self.blocks:
            b.update(dt)
    
    def render(self, screen: pygame.surface) -> None:
        for b in self.blocks:
            b.render(screen)


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.running = True
        self.screen = pygame.display.set_mode((1280, 720))
        self.sprites = self.load_sprites()

        self.previous_time = None

        # GAME Constants
        self.GRAVITY_CONSTANT = 1700
        self.PLAYER_VEL = 200
        self.JUMP_CONSTANT = -450

        self.player = Player(self.screen.get_width()/2,
                             self.screen.get_height()/2,
                             self.PLAYER_VEL,
                             self.sprites["player"],
                             self.GRAVITY_CONSTANT
                             )

        self.test_obstacle = Obstacle(1280,
                                      0,
                                      -200,
                                      self.screen.get_height(),
                                      2,
                                      5,
                                      self.sprites["obstacle"])
    def poll_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.velocity = self.JUMP_CONSTANT

    def update(self) -> None:
        if self.previous_time is None:
            self.previous_time = time.time()

        # Delta time
        now = time.time()
        dt = now - self.previous_time
        self.previous_time = now

        self.player.update(dt)
        self.test_obstacle.update(dt)

    def render(self) -> None:
        self.screen.fill("black")

        self.player.render(self.screen)
        self.test_obstacle.render(self.screen)

        pygame.display.update()

    def run(self) -> None:
        while self.running:
            self.poll_events()
            self.update()
            self.render()
        pygame.quit()

    def load_sprites(self) -> dict:
        sprites = {}

        sprites["player"] = pygame.image.load(r"Games\gfx\ball.png").convert_alpha()
        sprites["obstacle"] = pygame.image.load(r"Games\gfx\block.png").convert_alpha()

        return sprites


g = Game()
g.run()
