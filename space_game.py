import pygame
import random
import time

class collectible:
    def __init__(self, x: float, y: float, sprite: pygame.surface) -> None:
        self.x = x
        self.y = y
        self.sprite = sprite
        self.rect = self.sprite.get_rect()

    def update(self) -> None:
        pass

    def render(self, screen: pygame.surface) -> None:
        screen.blit(self.sprite, (self.x, self.y))

    def randomize_postion(self) -> None:
        self.x = random.randint(50, 1250)
        self.y = random.randint(50, 670)
        self.rect.x = self.x
        self.rect.y = self.y

class player:
    def __init__(self, x: float, y: float, sprite: pygame.surface) -> None:
        self.x = x
        self.y = y
        self.sprite = sprite
        self.velocity = 200
        self.angle = 0
        self.direction = "up"
        self.moving = False
        self.rect = self.sprite.get_rect()

    def update(self, dt) -> None:
        if self.moving:
            self.move(dt)
        
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def render(self, screen: pygame.surface) -> None:
        screen.blit(self.sprite, (self.x, self.y))

    def set_angle(self, new_angle: int) -> None:
        rotation = new_angle - self.angle
        self.sprite = pygame.transform.rotate(self.sprite, rotation)
        self.angle = new_angle

    def move(self, dt) -> None:
        if self.direction == "up":
            self.y -= self.velocity * dt
        elif self.direction == "down":
            self.y += self.velocity * dt
        elif self.direction == "left":
            self.x -= self.velocity * dt
        elif self.direction == "right":
            self.x += self.velocity *dt

        self.x = min((1280, self.x))
        self.x = max((0, self.x))

        self.y = min((720, self.y))
        self.y = max((0, self.y))


class Text:
    def __init__(self, x, y, text: str) -> None:
        self.x = x
        self.y = y
        self.text = text
        self.font = pygame.font.SysFont("Calibri", 36)
        
    def updat(self) -> None:
        pass

    def render(self, screen: pygame.surface) -> None:
        self.rendered = self.font.render(self.text, True, "white")
        screen.blit(self.rendered, (self.x, self.y))

class Game:
    def __init__(self) -> None:
        pygame.init()
        self.running = True
        self.screen = pygame.display.set_mode((1280, 720))
        self.sprites = self.load_sprites()

        self.score = 0

        self.player = player(200, 200, self.sprites["spaceship"])
        self.collectible = collectible(500, 500, self.sprites["collectible"])
        self.collectible.randomize_postion()
        self.text = Text(600, 50, str(self.score))

        self.keybinds = {pygame.K_w: (0, "up"),
                         pygame.K_d: (270, "right"),
                         pygame.K_s: (180, "down"),
                         pygame.K_a: (90, "left")}
        
        pygame.mixer.music.load("sfx\music.ogg")
        pygame.mixer.music.set_volume(0.25)
        pygame.mixer.music.play()

        self.collect_sound = pygame.mixer.Sound("sfx\collect.wav")
        self.collect_sound.set_volume(0.5)

    def poll_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN and event.key in self.keybinds:
                self.player.set_angle(self.keybinds[event.key][0])
                self.player.direction = self.keybinds[event.key][1]
                self.player.moving = True
            
            if event.type == pygame.KEYUP and event.key in self.keybinds:
                if self.keybinds[event.key][1] == self.player.direction:
                    self.player.moving = False


    def update(self) -> None:
        #compute delta time
        now = time.time()
        dt = now - self.previous_time
        self.previous_time = now

        self.player.update(dt)
        self.collectible.update()

        if self.player.rect.colliderect(self.collectible.rect):
            self.collectible.randomize_postion()
            self.player.velocity += 100
            self.collect_sound.play()
            self.score += 1

            
        self.text.updat()
        self.text.text =str(self.score)


    def render(self) -> None:
        self.screen.fill("black")
        
        self.screen.blit(self.sprites["background"], (0, 0))
        self.player.render(self.screen)
        self.collectible.render(self.screen)
        self.text.render(self.screen)
        
        pygame.display.update()

    def run(self) -> None:
        self.previous_time = time.time()
        while self.running:
            self.poll_events()
            self.update()
            self.render()
        pygame.quit()

    def load_sprites(self) -> dict:
        sprites = {}


        sprites["spaceship"] = pygame.image.load("gfx\ship.png").convert_alpha()
        sprites["background"] = pygame.image.load("gfx\simple_game_bg.png").convert_alpha()
        sprites["collectible"] = pygame.image.load("gfx\collectible.png").convert_alpha()
        #Downscale
        sprites["spaceship"] = pygame.transform.scale(sprites["spaceship"], (48, 48))

        return sprites
g = Game()
g.run()