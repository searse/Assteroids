# sys library
import sys

# pygame library
import pygame

# imports
from constants import *
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot

def main():
    # Print game start to console
    print("Starting Asteroids!")
    print("Screen width: 1280")
    print("Screen height: 720")

    # init pygame
    pygame.init()

    # declare screen as instance of pygame.display with set_mode() method to define screen dimensions
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    clock = pygame.time.Clock() # declare clock as instance of pygame.time.Clock()
    updatable = pygame.sprite.Group() # declare updatable objects group
    drawable = pygame.sprite.Group() # declare drawable objects group
    asteroids = pygame.sprite.Group() # declare asteroid objects group
    shots = pygame.sprite.Group() # declare shots objects group

    Player.containers = (updatable, drawable) # add class variable "containers" to Player to store groups
    Asteroid.containers = (asteroids, updatable, drawable) # add class variable "containers" to Asteroid to store groups
    AsteroidField.containers = (updatable) # add class variable "containers" to AsteroidField to store groups
    Shot.containers = (shots, updatable, drawable) # add class variable "containers" to Shots to store groups

    asteroid_field = AsteroidField() # declare variable to store the Asteroid Field as instance of AsteroidField()

    # declare Player as instance of Player(CircleShape)
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    # declare dt
    dt = 0

    # Game Loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: #listen for quit in pygame window
                return
        updatable.update(dt) # update the player rotation status
        for asteroid in asteroids:
            if asteroid.collides(player):
                print("Game over!")
                sys.exit()
            for shot in shots:
                if asteroid.collides(shot):
                    asteroid.split()
                    shot.kill()
        dt = clock.tick(60) / 1000 #limit the FPS to 60
        screen.fill("black") # fill the screen
        for object in drawable:
            object.draw(screen) # draw the objects on the screen
        pygame.display.flip() #recycle the screen

# Main function namespace protection
if __name__ == "__main__":
    main()
