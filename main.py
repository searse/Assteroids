# this allows us to use code from
# the open-source pygame library
# throughout this file
import pygame

from constants import *
from player import Player

def main():

    # Print game start to console
    print("Starting Asteroids!")
    print("Screen width: 1280")
    print("Screen height: 720")

    # init pygame
    pygame.init()

    # declare screen as instance of pygame.display with set_mode() method to define screen dimensions
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # declare clock as instance of pygame.time.Clock()
    clock = pygame.time.Clock()

    # declare dt
    dt = 0

    # declare Player as instance of Player(CircleShape)
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    # Game Loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        screen.fill("black")
        player.draw(screen)
        pygame.display.flip()
        dt = clock.tick(60) / 1000


# Main function protection
if __name__ == "__main__":
    main()
