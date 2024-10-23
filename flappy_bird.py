import pygame
import random
import time



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

class Game:
    def __init__(self) -> None:
        pygame.init()
        self.running = True
        self.screen = pygame.display.set_mode((1280, 720))
        self.sprites = self.load_sprites()

        self.previous_time = None

        #GAME Constants
        self.GRAVITY_CONSTANT = 1700
        self.PLAYER_VEL = 200

        self.player = Player(self.screen.get_width()/2,
                             self.screen.get_height()/2,
                             self.PLAYER_VEL,
                             self.sprites["player"],
                             self.GRAVITY_CONSTANT
                             )


    def poll_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self) -> None:
        if self.previous_time is None:
            self.previous_time = time.time()
        
        # Delta time
        now = time.time()
        dt = now - self.previous_time
        self.previous_time = now

        self.player.update(dt)


    def render(self) -> None:
        self.screen.fill("black")

        self.player.render(self.screen)

        pygame.display.update()

    def run(self) -> None:
        while self.running:
            self.poll_events()
            self.update()
            self.render()
        pygame.quit()

    def load_sprites(self) -> dict:
        sprites = {}

        sprites["player"] = pygame.image.load("Games\gfx\ball.png").convert_alpha()

        return sprites



g = Game()
g.run()
