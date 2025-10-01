# pygame library
import pygame

# imports
from constants import *
from player import Player

def main():

    # Print game start to console
    print("Starting Asteroids!")
    print("Screen width: 1280")
    print("Screen height: 720")

    # init pygame
    pygame.init()

    # declare clock as instance of pygame.time.Clock()
    clock = pygame.time.Clock()

    # declare dt
    dt = 0

    # declare screen as instance of pygame.display with set_mode() method to define screen dimensions
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # declare Player as instance of Player(CircleShape)
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    # Game Loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: #listen for quit in pygame window
                return
        dt = clock.tick(60) / 1000 #limit the FPS to 60
        player.update(dt) # update the player rotation status
        screen.fill("black") # fill the screen
        player.draw(screen) # draw the player on the screen
        pygame.display.flip() #recycle the screen

# Main function protection
if __name__ == "__main__":
    main()
