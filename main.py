import pygame, random

from pygame.locals import *

pygame.init()

#############
# Objects
#############

class Player(pygame.sprite.Sprite):

    def __init__(self):

        super(Player, self).__init__()

        self.surf = pygame.Surface((100, 100))

        self.surf.fill((0, 0, 0))

        self.rect = self.surf.get_rect()

    def update(self, pressedKeys):
        
        dx = 0

        dy = 0

        if pressedKeys[K_w]:

            dy = -5

            self.rect.move_ip(dx, dy)

        elif pressedKeys[K_s]:

            dy = 5

            self.rect.move_ip(dx, dy)

        elif pressedKeys[K_a]:

            dx = -5

            self.rect.move_ip(dx, dy)

        elif pressedKeys[K_d]:

            dx = 5

            self.rect.move_ip(dx, dy)

        if self.obstacleCollide():

            self.rect.move_ip(-dx, -dy)

        # Bound checking
        if self.rect.left < 0:
            
            self.rect.left = 0

        elif self.rect.right > displayWidth:

            self.rect.right = displayWidth

        if self.rect.top <= 0:

            self.rect.top = 0

        elif self.rect.bottom >= displayHeight:

            self.rect.bottom = displayHeight

    def obstacleCollide(self):

        if pygame.sprite.spritecollideany(player, obstacles):

            return True

        return False

class Enemy(pygame.sprite.Sprite):

    def __init__(self):

        super(Enemy, self).__init__()

        self.surf = pygame.Surface((50, 50))

        self.surf.fill((255, 0, 0))

        self.rect = self.surf.get_rect(
            center = (
                displayWidth - 50,
                displayHeight - 50
            )

        )

class Obstacle(pygame.sprite.Sprite):

    def __init__(self):

        super(Obstacle, self).__init__()

        self.surf = pygame.Surface((500, 500))

        self.surf.fill((0, 0, 255))

        self.rect = self.surf.get_rect(
            center = (
                (displayWidth - 250)//2,
                (displayHeight - 250)//2
            )
        )


###########
# Display
###########


# Fullscreen display

# screen = pygame.display.set_mode([0, 0], pygame.FULLSCREEN)

displayWidth, displayHeight = 1500, 1000

screen = pygame.display.set_mode([displayWidth, displayHeight])


##################
# Initialization
##################


clock = pygame.time.Clock()

player = Player()

obstacle1 = Obstacle()

obstacles = pygame.sprite.Group()

obstacles.add(obstacle1)

enemy1 = Enemy()

enemies = pygame.sprite.Group()

enemies.add(enemy1)

allSprites = pygame.sprite.Group()

allSprites.add(player)

allSprites.add(obstacle1)

allSprites.add(enemy1)


############
# Game Loop
############


running = True

while running:

    for event in pygame.event.get():

        # Checks if a key is pressed
        if event.type == KEYDOWN:

            # Closes on escape key press
            if event.key == K_ESCAPE:
                
                running = False

        # Checks for window closure
        if event.type == pygame.QUIT:

            running = False

    # Grabs the currently pressed keys
    pressedKeys = pygame.key.get_pressed()

    # Updates sprite based on input
    player.update(pressedKeys)

    # Make background white
    screen.fill((255, 255, 255))

    for sprite in allSprites:
        
        screen.blit(sprite.surf, sprite.rect)

    if pygame.sprite.spritecollideany(player, enemies):

        player.kill()

        running = False

    # Update the display
    pygame.display.flip()

    # runs the loop at 60fps
    clock.tick(60)

pygame.quit()

