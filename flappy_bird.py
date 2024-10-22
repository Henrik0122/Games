import pygame
import random
import time


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.running = True
        self.screen = pygame.display.set_mode((1280, 720))

    def poll_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self) -> None:
        pass

    def render(self) -> None:
        self.screen.fill("black")

        pygame.display.update()

    def run(self) -> None:
        while self.running:
            self.poll_events()
            self.update()
            self.render()
        pygame.quit()


g = Game()
g.run()
