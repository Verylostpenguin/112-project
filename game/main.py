import pygame, random, math, sys, os, pathlib, copy

from collections import deque

from pygame.locals import *

# Images found at this site
# https://opengameart.org/content/zelda-like-tilesets-and-sprites
# https://opengameart.org/content/rotating-arrow-projectile
# https://opengameart.org/content/light-weapons-pixel-art

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

        self.lastWeaponSpawn = pygame.time.get_ticks()

        self.cooldown = 1000

        self.openInventory = False

        self.currentWeapon = 'Bow'

        self.allSprites = pygame.sprite.Group()

        self.friendlies = pygame.sprite.Group()

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

                    BasicEnemy(self, col, row)

                elif tile == '3':

                    self.walls.append(vector(col, row))

                    Hole(self, col, row)

                elif tile == '4':

                    RangedEnemy(self, col, row)

                elif tile == '5':

                    self.boss = Boss(self, col, row)

        self.adjustmentPath = dict()

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

                elif event.key == K_e:

                    self.openInventory = not self.openInventory

            elif event.type == MOUSEBUTTONDOWN:

                time = pygame.time.get_ticks()

                if event.button == 1:

                    self.player.swing()

                    Sword(self, self.player)

                elif event.button == 3:

                    if time - self.lastWeaponSpawn >= self.cooldown:

                        self.lastWeaponSpawn = time

                        if self.currentWeapon == 'Spear':

                            Spear(self, self.player)

                        elif self.currentWeapon == 'Bow':

                            self.player.bow()

                            if self.player.arrowCount > 0:

                                self.player.arrowCount -= 1

                                Arrow(self, self.player)

                        elif self.currentWeapon == 'Magic':

                            if self.player.mana > 0:

                                self.player.mana -= 10

                                self.magic = Magic(self, self.player)

                elif event.button == 2:

                    if self.player.spikeCount > 0:

                        self.player.spikeCount -= 1

                        Spikes(self, self.player)

        self.mousePos = pygame.mouse.get_pos()

        pressedKeys = pygame.key.get_pressed()

        self.player.move(pressedKeys)

        # Add self.adjustmentPath

        self.path = self.mergeDictionaries(self.breadthFirstSearch(self.player.pos // tiles),self.adjustmentPath)

    def update(self):

        if self.openInventory:

            pass

        else:

            self.allSprites.update()

            # Attack hits

            hits = pygame.sprite.groupcollide(self.mobs, self.weapons, False, False)

            for enemy, weapon in hits.items():

                enemy.health -= weapon[0].damage

            hits = pygame.sprite.spritecollide(self.player, self.enemies, False)

            for hit in hits:

                self.player.health -= hit.damage

    def drawGrid(self):

        for x in range(0, displayWidth, tiles):

            pygame.draw.line(self.display, (100, 100, 100), (x, 0), (x, displayHeight))

        for y in range(0, displayHeight, tiles):

            pygame.draw.line(self.display, (100, 100, 100), (0, y), (displayWidth, y))

    def drawInventory(self):

        pygame.draw.line(self.display, (100, 100, 100), (700, 0), (700, displayHeight))

        playerStatBox = pygame.Rect(700, 0, 324, 400)

        healthText = pygame.font.Font(None, 40)

        health = healthText.render(f'Health: {self.player.health}', True, (0, 0, 0))

        manaText = pygame.font.Font(None, 40)

        mana = manaText.render(f'Mana: {self.player.mana}', True, (0, 0, 0))

        arrowText = pygame.font.Font(None, 40)

        arrows = arrowText.render(f'Arrows: {self.player.arrowCount}', True, (0, 0, 0))

        spikeText = pygame.font.Font(None, 40)

        spikes = spikeText.render(f'Spikes: {self.player.spikeCount}', True, (0, 0, 0))        

        pygame.draw.rect(self.display, (0, 0, 0), playerStatBox, 2)

        self.display.blit(health, (800, 50))

        self.display.blit(mana, (800, 100))

        self.display.blit(arrows, (800, 150))

        self.display.blit(spikes, (800, 200))

    def draw(self):

        self.display.fill((255, 255, 255))

        if self.openInventory:

            self.drawInventory()

        else:

            self.drawGrid()

            self.allSprites.draw(self.display)

        pygame.display.flip()

    def findObstacles(self, x, y):

        connections = [vector(1, 0), vector(-1, 0), vector(0, 1), vector(0, -1), vector(1, 1), vector(-1, -1), vector(1, -1), vector(-1, 1)]

        adjustment = vector(0, 0)

        for connection in connections:

            newTile = vector(x, y) + connection

            if newTile in self.walls:

                adjustment -= connection * 0.25

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

    def mergeDictionaries(self, dict1, dict2):

        newDict = copy.deepcopy(dict1)

        for key, value in dict1.items():

            # if math.abs(value.x) < math.abs(dict2[key].x):
            #
            #     newDict[key].x = 0
            #
            # if math.abs(value.y) < math.abs(dict2[key].y):
            #
            #     newDict[key].y = 0
            
            newDict[key] = value + dict2[key]

        return newDict

    # From kidscancode.org/lessons/

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

        self.groups = game.allSprites, game.friendlies

        pygame.sprite.Sprite.__init__(self, self.groups)

        self.game = game

        self.orientation = 'Down'

        self.image = getImageOrientation(self.orientation)

        self.rect = self.image.get_rect()

        self.rotation = 0

        self.vel = vector(0, 0)

        self.pos = vector(x, y) * tiles

        self.health = 100

        self.arrowCount = 10

        self.mana = 100

        self.spikeCount = 5

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

    def bow(self):

        pass

    def swing(self):

        pass

    def update(self):

        if self.health <= 0:

            self.kill()

            self.game.running = False

        frameTime = self.game.clock.get_time() / 1000

        self.image = getImageOrientation(self.orientation)

        self.pos += self.vel * frameTime

        self.rect.x = int(self.pos.x)

        self.obstacleCollide('dx')

        self.rect.y = int(self.pos.y)

        self.obstacleCollide('dy')

class BasicEnemy(pygame.sprite.Sprite):

    def __init__(self, game, x, y):

        self.groups = game.allSprites, game.enemies, game.mobs

        pygame.sprite.Sprite.__init__(self, self.groups)

        self.game = game
        
        self.image = getImageOrientation('Up')

        self.rect = self.image.get_rect()

        self.vel = vector(0, 0)

        self.pos = vector(x, y) * tiles

        self.rect.center = self.pos

        self.health = 100

        self.damage = 25

    def update(self):

        if self.health <= 0:

            self.kill()

        try:        

            self.acceleration = self.game.path[game.vectorToInteger(self.pos // tiles)]

        except:

            self.acceleration = vector(0, 0)

        self.vel += self.acceleration

        self.vel = vector.normalize(self.vel)

        self.pos += self.vel * 10

        self.rect.center = self.pos

class RangedEnemy(pygame.sprite.Sprite):

    def __init__(self, game, x, y):

        self.groups = game.allSprites, game.enemies, game.mobs

        pygame.sprite.Sprite.__init__(self, self.groups)

        self.game = game

        self.image = getImageOrientation('Down')

        self.rect = self.image.get_rect()

        self.vel = vector(0, 0)

        self.pos = vector(x, y) * tiles

        self.rect.center = self.pos

        self.health = 75

        self.damage = 20

        self.lastAttack = pygame.time.get_ticks()

        self.fireRate = 3000

    def attack(self):

        self.lastAttack = pygame.time.get_ticks()

        self.attackDir = vector.normalize(self.game.player.pos - self.pos)

        EnemyProjectile(self.game, self, self.attackDir)

    def lineOfSight(self):

        sightLine = pygame.draw.line(self.game.display, (0, 0, 0), self.pos, self.game.player.pos)

        for wall in self.game.obstacles:

            if sightLine.colliderect(wall.rect):

                return False

        return True

    def update(self):

        if self.health <= 0:

            self.kill()

        self.playerSeen = self.lineOfSight()

        try:     

            if (pygame.time.get_ticks() - self.lastAttack >= self.fireRate) and (
                self.playerSeen
            ):

                self.attack()

            if not self.playerSeen:

                self.acceleration = self.game.path[game.vectorToInteger(self.pos // tiles)]

            else:

                self.acceleration = vector(0, 0)

                self.vel = vector(0, 0)

        except:

            self.acceleration = vector(0, 0)

        self.vel += self.acceleration

        if self.vel != vector(0, 0):

            self.vel = vector.normalize(self.vel)

        self.pos += self.vel * 10

        self.rect.center = self.pos

class Boss(pygame.sprite.Sprite):

    def __init__(self, game, x, y):

        self.groups = game.allSprites, game.enemies, game.Boss

        pygame.sprite.Sprite.__init__(self, self.groups)

        self.game = game
        
        self.image = getImageOrientation('Down')

        self.rect = self.image.get_rect()

        self.pos = vector(x, y) * tiles

        self.rect.center = self.pos


    def update(self):

        pass

class EnemyProjectile(pygame.sprite.Sprite):

    def __init__(self, game, enemy, direction):

        self.groups = game.allSprites, game.enemies

        pygame.sprite.Sprite.__init__(self, self.groups)

        self.game = game

        self.rangedEnemy = enemy

        self.direction = direction

        self.originalImage = 'c:/Users/willh/Desktop/112-project/images/weapon/0.png'

        self.image = pygame.image.load(self.originalImage).convert()

        self.rect = self.image.get_rect()

        self.pos = copy.copy(self.rangedEnemy.pos)

        self.rect.center = self.pos
        
        self.damage = 50

    def update(self):

        if pygame.sprite.spritecollideany(self, self.game.obstacles):

            self.kill()

        if pygame.sprite.spritecollide(self, self.game.friendlies, False):

            self.kill()

        self.pos += self.direction * 10

        self.rect.center = self.pos

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

        self.damage = 100

# Replace with sword eventually
class Spear(pygame.sprite.Sprite):

    def __init__(self, game, player):

        self.groups = game.allSprites, game.weapons

        pygame.sprite.Sprite.__init__(self, self.groups)

        self.game = game

        self.player = player

        self.direction = player.orientation

        self.originalImage = 'c:/Users/willh/Desktop/112-project/images/weapon/spear.png'

        self.image = pygame.image.load(self.originalImage).convert()

        self.rect = self.image.get_rect()

        self.pos = self.player.pos

        self.rect.topleft = self.pos

        self.spawnTime = pygame.time.get_ticks()

        self.damage = 50

        self.knockback = 10

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

        if (pygame.time.get_ticks() - self.spawnTime > 150):

            self.kill()

class Arrow(pygame.sprite.Sprite):

    def __init__(self, game, player):

        self.groups = game.allSprites, game.weapons

        pygame.sprite.Sprite.__init__(self, self.groups)

        self.game = game

        self.player = player

        self.direction = self.player.orientation

        self.originalImage = 'c:/Users/willh/Desktop/112-project/images/weapon/0.png'

        self.image = pygame.image.load(self.originalImage).convert()

        self.rect = self.image.get_rect()

        if self.direction == 'Down':

            self.vel = vector(0, 10)

        elif self.direction == 'Up':

            self.vel = vector(0, -10)

        elif self.direction == 'Left':

            self.vel = vector(-10, 0)

        elif self.direction == 'Right':

            self.vel = vector(10, 0)

        self.pos = copy.copy(self.player.pos)

        self.rect.center = self.pos
        
        self.damage = 30

    def update(self):

        if pygame.sprite.spritecollideany(self, self.game.obstacles):

            self.kill()

        self.pos += self.vel

        self.rect.center = self.pos

class Magic(pygame.sprite.Sprite):

    def __init__(self, game, player):

        self.groups = game.allSprites, game.weapons

        pygame.sprite.Sprite.__init__(self, self.groups)

        self.game = game

        self.player = player

        self.originalImage = 'c:/Users/willh/Desktop/112-project/images/weapon/spikes.png'

        self.image = pygame.image.load(self.originalImage).convert()

        self.rect = self.image.get_rect()

        self.vel = vector(0, 0)

        self.pos = copy.copy(self.player.pos)

        self.rect.center = self.pos

        self.spawnTime = pygame.time.get_ticks()
        
        self.damage = 15

    def update(self):

        if pygame.sprite.spritecollideany(self, self.game.obstacles) or (
            pygame.time.get_ticks() - self.spawnTime >= 3000
        ):

            self.kill()

        self.mouseDir = vector.normalize(pygame.mouse.get_pos() - self.pos)

        self.vel = self.mouseDir * 10

        self.pos += self.vel

        self.rect.center = self.pos

class Spikes(pygame.sprite.Sprite):

    def __init__(self, game, player):

        self.groups = game.allSprites, game.weapons

        pygame.sprite.Sprite.__init__(self, self.groups)

        self.game = game

        self.player = player

        self.originalImage = 'c:/Users/willh/Desktop/112-project/images/weapon/spikes.png'

        self.image = pygame.image.load(self.originalImage).convert()

        self.rect = self.image.get_rect()

        self.pos = self.player.pos

        self.rect.center = self.pos

        self.spawnTime = pygame.time.get_ticks()
        
        self.damage = 10

    def update(self):

        if pygame.time.get_ticks() - self.spawnTime > 1000:

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

        self.spawnTime = pygame.time.get_ticks()

        self.damage = 30

    def update(self):

        frameTime = self.game.clock.get_time() // 10

        if (pygame.time.get_ticks() - self.spawnTime) > 150:

            self.kill()

        if self.direction == 'Down':

            offset = vector(0, 30)

            self.image = pygame.transform.rotate(self.image, 240)

        elif self.direction == 'Up':

            offset = vector(-10, -30)

            self.image = pygame.transform.rotate(self.image, 60)

        elif self.direction == 'Right':

            offset = vector(20, -10)

            self.image = pygame.transform.rotate(self.image, 330)

        elif self.direction == 'Left':

            offset = vector(-50, 0)

            self.image = pygame.transform.rotate(self.image, 150)

        self.rect.topleft = self.player.pos + offset

# Run the game

game = Game()

while True:

    game.initializeGame()

    game.newGame()
