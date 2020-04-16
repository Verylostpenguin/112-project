import pygame, random, math, sys, os, pathlib

from collections import deque, Counter

from pygame.locals import *

# Images found at this site
# https://opengameart.org/content/zelda-like-tilesets-and-sprites

# Temp globals

vector = pygame.math.Vector2

displayWidth = 1024

displayHeight = 768

tiles = 32

gridWidth = displayWidth // tiles

gridHeight = displayHeight // tiles

def getImageOrientation(orientation):

    # Scale to 200%

    return pygame.image.load(f'c:/Users/willh/Desktop/112-project/images/walk{orientation}/0.png').convert()

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

        print(folder)

        self.room = []

        with open('c:/Users/willh/Desktop/112-project/rooms/room1.txt', 'rt') as f:

            for line in f:

                self.room.append(line)

    def loadSprites(self):

        pass

    def initializeGame(self):

        self.allSprites = pygame.sprite.Group()

        self.enemies = pygame.sprite.Group()

        self.mobs = pygame.sprite.Group()

        self.boss = pygame.sprite.Group()

        self.obstacles = pygame.sprite.Group()

        self.weapons = pygame.sprite.Group()

        self.walls = []

        for row, tiles in enumerate(self.room):

            for col, tile in enumerate(tiles):

                if tile == '0':

                    self.player = Player(self, col, row)

                elif tile == '1':

                    self.walls.append(vector(col, row))

                    Obstacle(self, col, row)

                elif tile == '2':

                    Enemy(self, col, row)

                elif tile == '3':

                    self.walls.append(vector(col, row))

                    Hole(self, col, row)

                elif tile == '4':

                    self.boss = Boss(self, col, row)

        self.adjustmentPath = Counter()

        for row, tiles in enumerate(self.room):

            for col, tile in enumerate(tiles):

                self.adjustmentPath[(col, row)] = self.findObstacles(col, row)

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

                if event.button == 1:

                    Sword(self, self.player)

                elif event.button == 3:

                    Spear(self, self.player)

        pressedKeys = pygame.key.get_pressed()

        self.player.move(pressedKeys)

        # Add self.adjustmentPath

        self.path = self.breadthFirstSearch(self.player.pos // tiles)

    def update(self):

        self.allSprites.update()

        # Attack hits

        pygame.sprite.groupcollide(self.mobs, self.weapons, True, False)

        hits = pygame.sprite.spritecollide(self.player, self.enemies, False)

        for hit in hits:

            self.running = False

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

    def findObstacles(self, x, y):

        connections = [vector(1, 0), vector(-1, 0), vector(0, 1), vector(0, -1), vector(1, 1), vector(-1, -1), vector(1, -1), vector(-1, 1)]

        adjustment = vector(0, 0)

        for connection in connections:

            newTile = vector(x, y) + connection

            if newTile in self.walls:

                adjustment -= connection * 0.1

        return adjustment

    def findNeighbors(self, tile):

        connections = [vector(1, 0), vector(-1, 0), vector(0, 1), vector(0, -1), vector(1, 1), vector(-1, -1), vector(1, -1), vector(-1, 1)]

        neighbors = []

        for connection in connections:

            newTile = tile + connection

            if (newTile not in self.walls) and (
                0 < newTile.x < 32 and 0 < newTile.y < 24
            ):

                neighbors.append(tile + connection)

        return neighbors

    def vectorToInteger(self, vector):

        return (int(vector.x), int(vector.y))

    def breadthFirstSearch(self, start):

        frontier = deque()

        frontier.append(start)

        path = dict()

        path[self.vectorToInteger(start)] = vector(0, 0)

        while len(frontier) > 0:

            currentTile = frontier.popleft()

            for neighbor in self.findNeighbors(currentTile):

                if self.vectorToInteger(neighbor) not in path:

                    frontier.append(neighbor)

                    path[self.vectorToInteger(neighbor)] = currentTile - neighbor

        return path

##########
# Classes
##########

class Player(pygame.sprite.Sprite):

    def __init__(self, game, x, y):

        self.groups = game.allSprites

        pygame.sprite.Sprite.__init__(self, self.groups)

        self.game = game

        self.orientation = 'Down'

        self.image = getImageOrientation(self.orientation)

        self.rect = self.image.get_rect()

        self.rotation = 0

        self.vel = vector(0, 0)

        self.pos = vector(x, y) * tiles

        self.health = 100

    def move(self, pressedKeys):

        self.vel = vector(0, 0)

        if pressedKeys[K_w]:

            self.orientation = 'Up'

            self.vel.y = -250

        if pressedKeys[K_s]:

            self.orientation = 'Down'

            self.vel.y = 250

        if pressedKeys[K_a]:

            self.orientation = 'Left'

            self.vel.x = -250

        if pressedKeys[K_d]:

            self.orientation = 'Right'

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

        self.groups = game.allSprites, game.enemies, game.mobs

        pygame.sprite.Sprite.__init__(self, self.groups)

        self.game = game
        
        self.image = getImageOrientation('Up')

        self.rect = self.image.get_rect()

        self.pos = vector(x, y) * tiles

        self.rect.center = self.pos

        self.health = 50

    def update(self):

        frameTime = self.game.clock.get_time() / 1000

        try:        

            self.vel = self.game.path[game.vectorToInteger(self.pos // tiles)]

        except:

            self.vel = vector(0, 0)

        self.pos += self.vel * 2

        self.rect.center = self.pos

class Boss(pygame.sprite.Sprite):

    def __init__(self, x, y):

        self.groups = game.allSprites, game.enemies, game.Boss

        pygame.sprite.Sprite.__init__(self, self.groups)

        self.game = game
        
        self.image = getImageOrientation('Down')

        self.rect = self.image.get_rect()

        self.pos = vector(x, y) * tiles

        self.rect.center = self.pos


    def update(self):

        pass

class Obstacle(pygame.sprite.Sprite):

    def __init__(self, game, x, y):

        self.groups = game.allSprites, game.obstacles

        pygame.sprite.Sprite.__init__(self, self.groups)

        self.game = game

        self.image = pygame.image.load('c:/Users/willh/Desktop/112-project/images/Cave/0.png').convert()

        self.rect = self.image.get_rect()

        self.pos = vector(x, y) * tiles

        self.rect.topleft = self.pos

class Hole(Obstacle):

    def __init__(self, game, x, y):

        self.groups = game.allSprites, game.enemies

        pygame.sprite.Sprite.__init__(self, self.groups)

        self.game = game

        self.image = pygame.image.load('c:/Users/willh/Desktop/112-project/images/Cave/1.png').convert()

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

        self.originalImage = 'c:/Users/willh/Desktop/112-project/images/spear.png'

        self.image = pygame.image.load(self.originalImage).convert()

        self.rect = self.image.get_rect()

        self.pos = self.player.pos

        self.rect.topleft = self.pos

        self.spawnTime = pygame.time.get_ticks()

        self.damage = 50

    def update(self):

        # Spear img is wierd, have to rotate 60 degrees to get it oriented with character, (draw own spear?)

        if self.direction == 'Down':

            offset = vector(0, 30)

            self.image = pygame.transform.rotate(pygame.image.load(self.originalImage).convert(), 240)

        elif self.direction == 'Up':

            offset = vector(-10, -30)

            self.image = pygame.transform.rotate(pygame.image.load(self.originalImage).convert(), 60)

        elif self.direction == 'Right':

            offset = vector(20, -10)

            self.image = pygame.transform.rotate(pygame.image.load(self.originalImage).convert(), 330)

        elif self.direction == 'Left':

            offset = vector(-50, 0)

            self.image = pygame.transform.rotate(pygame.image.load(self.originalImage).convert(), 150)

        self.rect.topleft = self.player.pos + offset

        if (pygame.time.get_ticks() - self.spawnTime > 100):

            # attacks go through walls, maybe kill on obstacle collide?

            self.kill()

class Sword(pygame.sprite.Sprite):

    def __init__(self, game, player):

        self.groups = game.allSprites, game.weapons

        pygame.sprite.Sprite.__init__(self, self.groups)

        self.game = game
        
        self.player = player

        self.direction = player.orientation

        self.image = pygame.Surface((tiles * 0.1, tiles), pygame.SRCALPHA)

        self.image.fill((0, 255, 0))

        self.rect = self.image.get_rect()

        self.pos = self.player.pos

        self.rect.topleft = self.pos

        self.vel = vector(0, 0)

        self.spawnTime = pygame.time.get_ticks()

        self.damage = 30

    def update(self):

        frameTime = self.game.clock.get_time() // 10

        if (pygame.time.get_ticks() - self.spawnTime) > 100:

            self.kill()

        elif (pygame.time.get_ticks() - self.spawnTime) < 50:

            newHeight = tiles + frameTime

            self.image = pygame.transform.scale(self.image, (10, newHeight))

            if self.direction == 'Down':

                offset = vector(0, 30)

                self.image = pygame.transform.scale(pygame.transform.rotate(self.image, 180), (10, newHeight))

            elif self.direction == 'Up':

                offset = vector(-10, -30)

            elif self.direction == 'Right':

                offset = vector(0, 0)

                self.image = pygame.transform.scale(pygame.transform.rotate(self.image, 90), (10, newHeight))

            elif self.direction == 'Left':

                offset = vector(-50, 0)

                self.image = pygame.transform.scale(pygame.transform.rotate(self.image, -90), (10, newHeight))

            self.rect.topleft = self.player.pos + offset

        elif 50 < (pygame.time.get_ticks() - self.spawnTime) < 100:

            self.image = pygame.transform.scale(self.image, (10, tiles - frameTime))

            if self.direction == 'Down':

                offset = vector(0, 30)

                self.image = pygame.transform.rotate(self.image, 180)

            elif self.direction == 'Up':

                offset = vector(-10, -30)

            elif self.direction == 'Right':

                offset = vector(30, 15)

                self.image = pygame.transform.rotate(self.image, 90)

            elif self.direction == 'Left':

                offset = vector(-50, 0)

                self.image = pygame.transform.rotate(self.image, -90)

            self.rect.topleft = self.player.pos + offset

        

# Run the game

game = Game()

while True:

    game.initializeGame()

    game.newGame()
