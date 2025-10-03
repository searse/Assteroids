# pygame library
import pygame 

# imports
from constants import *
from circleshape import CircleShape
from shot import Shot

class Player(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.timer = 0

    def triangle(self):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def draw(self, screen):
        # pygame.draw.circle(screen, "red", self.position, self.radius, 2)
        pygame.draw.polygon(screen, "white", self.triangle(), 2)

    def rotate(self, dt):
        self.rotation += PLAYER_TURN_SPEED * dt

    def update(self, dt):
        self.timer -= dt
        keys = pygame.key.get_pressed() # listen for keys "getting pressed"
        speed = BOOST_SPEED if keys[pygame.K_LSHIFT] else PLAYER_SPEED
        mouse = pygame.mouse.get_pressed() # listen for mouse buttons "getting pressed"
        if keys[pygame.K_a]:
            self.rotate(-dt) # rotate left
        if keys[pygame.K_d]:
            self.rotate(dt) # rotate right
        if keys[pygame.K_w]:
            self.move(dt, speed)
        if keys[pygame.K_s]:
            self.move(-dt, speed)
        if keys[pygame.K_SPACE]: # shoot if space bar pressed
            self.shoot()
        if mouse[0]: # shoot if left mouse button is pressed
            self.shoot()
        if mouse[2]: # shoot if right mouse button is pressed
            self.shoot()
    
    def move(self, dt, speed):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        self.position += forward * speed * dt

    def shoot(self):
        if self.timer > 0: # shoot rate limit
            return
        shot = Shot(self.position.x, self.position.y)
        shot.velocity = pygame.Vector2(0, 1).rotate(self.rotation) * PLAYER_SHOOT_SPEED
        self.timer = PLAYER_SHOOT_COOLDOWN