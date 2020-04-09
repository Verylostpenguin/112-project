import pygame, random, math, sys, os, pathlib

from pygame.locals import *

from collections import deque

# Temp globals

vector = pygame.math.Vector2

displayWidth = 1024

displayHeight = 768

tiles = 32

gridWidth = displayWidth // tiles

gridHeight = displayHeight // tiles

def getImageOrientation(orientation):

    # Scale to 200%

    imagesFolder = os.path.join(pathlib.Path(__file__).parent.absolute(), 'images')

    orientedImages = os.path.join(imagesFolder, orientation)

    return pygame.image.load(os.path.join(orientedImages, '4.png')).convert_alpha()

# The basic framework of this code was heavily adapted from tutorial http://kidscancode.org/lessons/
class Game:

    def __init__(self):

        pygame.init()

        # Fullscreen display

        # screen = pygame.display.set_mode([0, 0], pygame.FULLSCREEN)

        self.display = pygame.display.set_mode([displayWidth, displayHeight])

        self.clock = pygame.time.Clock()

        self.loadMap()

    def loadMap(self):

        folder = os.path.dirname(__file__)

        self.room = []

        with open(os.path.join(folder, 'room1.txt'), 'rt') as f:

            for line in f:

                self.room.append(line)

    def initializeGame(self):

        self.allSprites = pygame.sprite.Group()

        self.enemies = pygame.sprite.Group()

        self.obstacles = pygame.sprite.Group()

        self.weapons = pygame.sprite.Group()

        for row, tiles in enumerate(self.room):

            for col, tile in enumerate(tiles):

                if tile == '0':

                    self.player = Player(self, col, row)

                elif tile == '1':

                    Obstacle(self, col, row)

                elif tile == '2':

                    Enemy(self, col, row)

    def newGame(self):

        self.running = True

        while self.running:

            # Control
            self.events()

            # Model
            self.update()

            # View
            self.draw()

            self.clock.tick(60)

    def quitGame(self):

        pygame.quit()

        sys.exit()

    def events(self):
    
        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                self.quitGame()

            elif event.type == KEYDOWN:

                if event.key == K_ESCAPE:

                    self.quitGame()

            elif event.type == MOUSEBUTTONDOWN:

                Spear(self, self.player)

        pressedKeys = pygame.key.get_pressed()

        self.player.move(pressedKeys)


    def update(self):

        self.allSprites.update()

        # Attack hits

        hits = pygame.sprite.groupcollide(self.enemies, self.weapons, False, True)

        for hit in hits:

            hit.kill()

    def drawGrid(self):

        for x in range(0, displayWidth, tiles):

            pygame.draw.line(self.display, (100, 100, 100), (x, 0), (x, displayHeight))

        for y in range(0, displayHeight, tiles):

            pygame.draw.line(self.display, (100, 100, 100), (0, y), (displayWidth, y))

    def draw(self):

        self.display.fill((255, 255, 255))

        self.drawGrid()

        self.allSprites.draw(self.display)

        pygame.display.flip()

##########
# Classes
##########

class Player(pygame.sprite.Sprite):

    def __init__(self, game, x, y):

        self.groups = game.allSprites

        pygame.sprite.Sprite.__init__(self, self.groups)

        self.game = game

        self.orientation = 'facingDown'

        self.image = getImageOrientation(self.orientation)

        self.rect = self.image.get_rect()

        self.rotation = 0

        self.vel = vector(0, 0)

        self.pos = vector(x, y) * tiles

    def move(self, pressedKeys):

        self.vel = vector(0, 0)

        if pressedKeys[K_w]:

            self.orientation = 'facingUp'

            self.vel.y = -250

        if pressedKeys[K_s]:

            self.orientation = 'facingDown'

            self.vel.y = 250

        if pressedKeys[K_a]:

            self.orientation = 'facingLeft'

            self.vel.x = -250

        if pressedKeys[K_d]:

            self.orientation = 'facingRight'

            self.vel.x = 250

        if self.vel.x != 0 and self.vel.y != 0:

            self.vel *= math.sqrt(2) / 2

    def obstacleCollide(self, moveDirection):

        collision = pygame.sprite.spritecollide(self, self.game.obstacles, False)

        if moveDirection == 'dx':

            if collision:

                if self.vel.x > 0:
                
                    self.pos.x = collision[0].rect.left - self.rect.width

                elif self.vel.x < 0:

                    self.pos.x = collision[0].rect.right

                self.vel.x = 0

                self.rect.x = int(self.pos.x)

        elif moveDirection == 'dy':

            if collision:

                if self.vel.y > 0:
                
                    self.pos.y = collision[0].rect.top - self.rect.height

                elif self.vel.y < 0:

                    self.pos.y = collision[0].rect.bottom

                self.vel.y = 0

                self.rect.y = int(self.pos.y)

    def update(self):

        frameTime = self.game.clock.get_time() / 1000

        self.image = getImageOrientation(self.orientation)

        self.pos += self.vel * frameTime

        self.rect.x = int(self.pos.x)

        self.obstacleCollide('dx')

        self.rect.y = int(self.pos.y)

        self.obstacleCollide('dy')

class Enemy(pygame.sprite.Sprite):

    def __init__(self, game, x, y):

        self.groups = game.allSprites, game.enemies

        pygame.sprite.Sprite.__init__(self, self.groups)

        self.game = game
        
        self.image = getImageOrientation('facingUp')

        self.rect = self.image.get_rect()

        self.pos = vector(x, y) * tiles

        self.vel = vector(0, -10)

        self.rect.center = self.pos

    def update(self):

        frameTime = self.game.clock.get_time() / 1000

        self.pos += self.vel * frameTime

        self.rect.y = int(self.pos.y)

        collision = pygame.sprite.spritecollide(self, self.game.obstacles, False)

        if collision:

            self.image = getImageOrientation('facingDown')

            if self.vel.y > 0:

                self.pos.y = collision[0].rect.top - self.rect.height

            else:

                self.pos.y = collision[0].rect.bottom

            self.vel *= -1

class Obstacle(pygame.sprite.Sprite):

    def __init__(self, game, x, y):

        self.groups = game.allSprites, game.obstacles

        pygame.sprite.Sprite.__init__(self, self.groups)

        self.game = game

        folder = os.path.dirname(__file__)
        images = os.path.join(folder, 'images')
        caveImages = os.path.join(images, 'Cave')

        self.image = pygame.image.load(os.path.join(caveImages, '0.png')).convert_alpha()

        self.rect = self.image.get_rect()

        self.pos = vector(x, y) * tiles

        self.rect.topleft = self.pos

# Replace with sword eventually
class Spear(pygame.sprite.Sprite):

    def __init__(self, game, player):

        self.groups = game.allSprites, game.weapons

        pygame.sprite.Sprite.__init__(self, self.groups)

        self.game = game

        self.player = player

        self.direction = player.orientation

        folder = os.path.dirname(__file__)
        images = os.path.join(folder, 'images')
        self.originalImage = os.path.join(images, 'spear.png')

        self.image = pygame.image.load(self.originalImage).convert_alpha()

        self.rect = self.image.get_rect()

        self.pos = self.player.pos

        self.rect.topleft = self.pos

        self.spawnTime = pygame.time.get_ticks()

    def update(self):

        # Spear img is wierd, have to rotate 60 degrees to get it oriented with character, (draw own spear?)

        if self.direction == 'facingDown':

            offset = vector(0, 30)

            self.image = pygame.transform.rotate(pygame.image.load(self.originalImage).convert_alpha(), 240)

        elif self.direction == 'facingUp':

            offset = vector(-10, -30)

            self.image = pygame.transform.rotate(pygame.image.load(self.originalImage).convert_alpha(), 60)

        elif self.direction == 'facingRight':

            offset = vector(20, -10)

            self.image = pygame.transform.rotate(pygame.image.load(self.originalImage).convert_alpha(), 330)

        elif self.direction == 'facingLeft':

            offset = vector(-50, 0)

            self.image = pygame.transform.rotate(pygame.image.load(self.originalImage).convert_alpha(), 150)

        self.rect.topleft = self.player.pos + offset

        if (pygame.time.get_ticks() - self.spawnTime > 100):

            # attacks go through walls, maybe kill on obstacle collide?

            self.kill()


# Run the game

game = Game()

while True:

    game.initializeGame()

    game.newGame()
