import pygame

import math, copy

import os, sys

from collections import deque

from pygame.locals import *

from pygame.math import Vector2 as vector

# Game images found at this site
# https://opengameart.org/content/zelda-like-tilesets-and-sprites
# https://opengameart.org/content/dungeon-tileset
# https://opengameart.org/content/rotating-arrow-projectile
# https://opengameart.org/content/light-weapons-pixel-art
# https://opengameart.org/content/whirlwind

# Title Screen Image found at
# https://dlpng.com/png/1729391

# Globals

displayWidth = 1024

displayHeight = 768

tiles = 32

BLACK = (0, 0, 0)

WHITE = (255, 255, 255)

GREY = (105, 105, 105)

BROWN = (139, 69, 19)

RED = (255, 0, 0)

MAROON = (139, 0, 0)

highscores = [0, 0, 0, 0, 0]

folder = os.getcwd()

def getPlayerImageOrientation(orientation):

    walkImage = os.path.join(folder, f'images/walk{orientation}/0.png')

    image = pygame.image.load(walkImage)

    image.set_colorkey(WHITE)

    return image.convert_alpha()

def getObstacleImage(obstacleType):

    images = os.path.join(folder, 'images/obstacles')

    image = pygame.image.load(os.path.join(images, f'{obstacleType}.png'))

    image.set_colorkey(WHITE)

    return image.convert_alpha()

def getBackgroundImage(backgroundType):

    images = os.path.join(folder, 'images/background')

    return pygame.image.load(os.path.join(images, f'{backgroundType}.png')).convert_alpha()

def getEnemyImage(enemyType):

    images = os.path.join(folder, 'images/enemy')

    image = pygame.image.load(os.path.join(images, f'{enemyType}.png'))

    image.set_colorkey(WHITE)

    return image.convert_alpha()

def getSwingOrientation(orientation):

    swingImage = os.path.join(folder, f'images/sword{orientation}/1.png')

    image = pygame.image.load(swingImage)

    image.set_colorkey(WHITE)

    return image.convert_alpha()

def getWeaponImage(type):

    weapons = os.path.join(folder, 'images/weapon')

    if type == 'Magic':

        image = pygame.image.load(os.path.join(weapons, 'magic/0.png'))

        image.set_colorkey(WHITE)

    elif type == 'Arrow':

        image = pygame.image.load(os.path.join(weapons, 'arrow/0.png'))

        image.set_colorkey(BLACK)

    elif type == 'Spear':

        image = pygame.image.load(os.path.join(weapons, 'spear.png'))

        image.set_colorkey(WHITE)

    elif type == 'Spikes':

        image = pygame.image.load(os.path.join(weapons, 'spikes.png'))

        image.set_colorkey(WHITE)

    return image.convert_alpha()


# The basic framework of this code was heavily adapted from tutorial http://kidscancode.org/lessons/
# The BFS algorithm was also from http://kidscancode.org/lessons/
class Game:

    def __init__(self):

        pygame.init()

        # Fullscreen display

        # screen = pygame.display.set_mode([0, 0], pygame.FULLSCREEN)

        self.display = pygame.display.set_mode([displayWidth, displayHeight])

        self.titleImage = pygame.image.load(os.path.join(folder, 'images/background.png')).convert()

        self.menu = True

        self.helpScreen = False

        self.levelUp = False

        self.started = False

        self.gameOver = False

        self.win = False

        self.clock = pygame.time.Clock()

        self.currentRoom = 1

        self.score = 0

        self.deaths = 0

        self.playerHealth = 0

        self.playerDamage = 0

    ######################
    # GAME INITIALIZATION
    ######################

    def quitGame(self):

        pygame.quit()

        sys.exit()

    def initializeGame(self):

        self.lastWeaponSpawn = pygame.time.get_ticks()

        self.cooldown = 1000

        self.openInventory = False

        self.highlight = None

        self.currentWeapon = 'Spear'

        self.allSprites = pygame.sprite.Group()

        self.friendlies = pygame.sprite.Group()

        self.enemies = pygame.sprite.Group()

        self.mobs = pygame.sprite.Group()

        self.boss = pygame.sprite.Group()

        self.obstacles = pygame.sprite.Group()

        self.interactable = pygame.sprite.Group()

        self.blocker = pygame.sprite.Group()

        self.weapons = pygame.sprite.Group()

        self.loadSprites()

        self.changeRoom()

    def loadSprites(self):

        self.wallImage = getObstacleImage('wallTile')

        self.holeImage = getObstacleImage('holeTile')

        self.obstacleImage = getObstacleImage('obstacleTile')

        self.doorImage = getObstacleImage('doorTile')

        self.grassImage = getBackgroundImage('grassTile')

        self.floorImage = getBackgroundImage('caveTile')

        self.switchImage = getObstacleImage('switch')

    def changeRoom(self):

        folder = os.getcwd()

        rooms = os.path.join(folder, 'rooms')

        for fileName in os.scandir(rooms):

            if fileName.path.endswith(f"{self.currentRoom}.txt"):

                self.room = []

                roomName = os.path.join(rooms, fileName)

                with open(roomName, 'rt') as f:

                    for line in f:

                        self.room.append(line)

        self.drawRoom()

    def drawRoom(self):

        self.running = False

        self.walls = []

        self.background = pygame.Surface((1024, 768))

        for x in range(0, 1024, 32):

            for y in range(0, 1024, 32):

                self.background.blit(self.floorImage, (x, y))

        for row, tiles in enumerate(self.room):

            for col, tile in enumerate(tiles):
                
                if tile == '0':

                    self.player = Player(self, col, row)

                elif tile == '1':

                    self.walls.append(vector(col, row))

                    Obstacle(self, col, row, self.wallImage)

                elif tile == 'O':

                    self.walls.append(vector(col, row))

                    Obstacle(self, col, row, self.obstacleImage)

                elif tile == '2':

                    BasicEnemy(self, col, row)

                elif tile == '3':

                    self.walls.append(vector(col, row))

                    Hole(self, col, row, self.holeImage)

                elif tile == '4':

                    RangedEnemy(self, col, row)

                elif tile == '5':

                    self.walls.append(vector(col, row))

                    Blocker(self, col, row, self.obstacleImage)

                elif tile == '/':

                    Door(self, col, row, self.switchImage, 'removeBlocker')

                elif tile == '*':

                    Door(self, col, row, self.doorImage, 'nextRoom')

                elif tile == 'B':

                    Boss(self, col, row)

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

            self.clock.tick(30)

    ####################
    # EVENT FUNCTIONS
    ####################

    def events(self):
    
        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                self.quitGame()

            elif event.type == KEYDOWN:

                if event.key == K_ESCAPE:

                    if self.started:

                        self.menu = not self.menu

                    if self.helpScreen:

                        self.menu = True

                        self.helpScreen = False

                elif event.key == K_e:

                    if not (self.menu or self.helpScreen):

                        self.openInventory = not self.openInventory

                elif event.key == K_SPACE:

                    if self.player.spikeCount > 0:

                        self.player.spikeCount -= 1

                        Spikes(self, self.player)

                ######################
                # SHORTCUT KEYS
                ######################
                
                elif event.key == K_m:

                    if self.currentRoom < 10:

                        self.currentRoom += 1

                        self.changeRoom()

                elif event.key == K_EQUALS:

                    self.score += 1000

                elif event.key == K_g:

                    self.player.god = not self.player.god

            elif event.type == MOUSEBUTTONDOWN:

                self.handleMouse(event.button)

        self.mousePos = pygame.mouse.get_pos()

        pressedKeys = pygame.key.get_pressed()

        self.player.move(pressedKeys)

        # Add self.adjustmentPath

        self.path = self.mergeDictionaries(self.breadthFirstSearch(self.player.pos // tiles), self.adjustmentPath)

    def handleMouse(self, button):

        time = pygame.time.get_ticks()

        if button == 1:

            if self.gameOver or self.win:

                if self.highlight == 'Retry':

                    self.gameOver = False

                    self.running = False

                elif self.highlight == 'Restart':

                    self.gameOver = False

                    self.win = False

                    self.deaths = 0

                    self.score = 0

                    self.currentRoom = 1

                    self.changeRoom()

                elif self.highlight == 'Quit':

                    self.quitGame()
            
            elif self.menu:

                if self.highlight == 'Start' or (
                    self.highlight == 'Resume'
                ):

                    self.menu = False

                    self.started = True

                elif self.highlight == 'Help':

                    self.helpScreen = True

                    self.menu = False

                elif self.highlight == 'Restart':

                    self.menu = False

                    self.currentRoom = 1

                    self.changeRoom()

                elif self.highlight == 'Quit':

                    self.quitGame()
                    
            elif self.openInventory:

                if self.highlight == 'Spear':

                    self.currentWeapon = 'Spear'

                elif self.highlight == 'Bow':

                    self.currentWeapon = 'Bow'

                elif self.highlight == 'Magic':

                    self.currentWeapon = 'Magic'

            elif self.levelUp:

                if self.highlight == 'Health':

                    self.playerHealth += 100

                    self.player.health += self.playerHealth

                elif self.highlight == 'Damage':

                    self.playerDamage += 50

                    self.player.damage += self.playerDamage

                elif self.highlight == 'Projectile':

                    self.player.arrowCount += 10

                    self.player.mana += 100

                    self.player.spikeCount += 5

                self.levelUp = False

            self.player.swing = True

            Sword(self, self.player)

        elif button == 3:

            if time - self.lastWeaponSpawn >= self.cooldown:

                self.lastWeaponSpawn = time

                if self.currentWeapon == 'Spear':

                    Spear(self, self.player)

                elif self.currentWeapon == 'Bow':

                    if self.player.arrowCount > 0:

                        self.player.arrowCount -= 1

                        Arrow(self, self.player)

                elif self.currentWeapon == 'Magic':

                    if self.player.mana > 0:

                        self.player.mana -= 10

                        self.magic = Magic(self, self.player)

    ####################
    # UPDATE FUNCTIONS
    ####################

    def update(self):

        self.quitButton = pygame.Rect(displayWidth - 100, displayHeight - 75, 150, 100)

        self.retryButton = pygame.Rect(displayWidth // 2 - 150, displayHeight // 2 - 100, 300, 100)

        self.restartButton = pygame.Rect(displayWidth // 2 - 150, displayHeight // 2 + 50, 300, 100)

        self.startButton = pygame.Rect(displayWidth // 2 - 150, displayHeight // 2 - 50, 300, 100)

        self.resumeButton = pygame.Rect(displayWidth // 2 - 150, displayHeight // 2 - 100, 300, 100)

        self.healthBox = pygame.Rect(displayWidth // 2 - 300, 210, 600, 100)

        self.damageBox = pygame.Rect(displayWidth // 2 - 300, 410, 600, 100)

        self.replenishBox = pygame.Rect(displayWidth // 2 - 300, 610, 600, 100)

        if self.gameOver or self.win:

            if self.retryButton.collidepoint(self.mousePos):

                self.highlight = 'Retry'

            elif self.restartButton.collidepoint(self.mousePos):

                self.highlight = 'Restart'

            elif self.quitButton.collidepoint(self.mousePos):

                self.highlight = 'Quit'

            else:

                self.highlight = None
        
        elif self.menu:

            if self.started:
                
                self.helpButton = pygame.Rect(displayWidth // 2 - 150, displayHeight // 2 + 200, 300, 100)

            else:

                self.helpButton = pygame.Rect(displayWidth // 2 - 150, displayHeight // 2 + 150, 300, 100)

            if self.startButton.collidepoint(self.mousePos):

                self.highlight = 'Start'

            elif self.resumeButton.collidepoint(self.mousePos):

                self.highlight = 'Resume'

            elif self.restartButton.collidepoint(self.mousePos):

                self.highlight = 'Restart'

            elif self.helpButton.collidepoint(self.mousePos):

                self.highlight = 'Help'
            
            elif self.quitButton.collidepoint(self.mousePos):

                self.highlight = 'Quit'

            else:

                self.highlight = None

        elif self.openInventory:

            self.spearBox = pygame.Rect(0, 0, 300, 100)

            self.arrowBox = pygame.Rect(0, 100, 300, 100)

            self.magicBox = pygame.Rect(0, 200, 300, 100)

            if self.spearBox.collidepoint(self.mousePos):

                self.highlight = 'Spear'

            elif self.arrowBox.collidepoint(self.mousePos):

                self.highlight = 'Bow'

            elif self.magicBox.collidepoint(self.mousePos):

                self.highlight = 'Magic'

            else:

                self.highlight = None

        elif self.levelUp:

            if self.healthBox.collidepoint(self.mousePos):

                self.highlight = 'Health'

            elif self.damageBox.collidepoint(self.mousePos):

                self.highlight = 'Damage'

            elif self.replenishBox.collidepoint(self.mousePos):

                self.highlight = 'Projectile'

            else:

                self.highlight = None

        elif not self.helpScreen:

            self.allSprites.update()

            # Attack hits

            hits = pygame.sprite.groupcollide(self.mobs, self.weapons, False, False)

            for enemy, weapon in hits.items():

                enemy.health -= weapon[0].damage + self.playerDamage

                enemy.knockback = weapon[0].knockback

            hits = pygame.sprite.spritecollide(self.player, self.enemies, False)

            for hit in hits:

                self.player.health -= hit.damage

    ##################
    # DRAW FUNCTIONS
    ##################

    def draw(self):

        if self.gameOver:

            self.display.fill(BLACK)

            self.drawGameOver()

        elif self.win:

            self.display.blit(self.titleImage, (0, 0))

            self.drawGameWin()
        
        elif self.menu:

            self.display.blit(self.titleImage, (0, 0))

            self.drawMenu()

        elif self.helpScreen:

            self.display.blit(self.titleImage, (0, 0))

            self.drawHelp()

        elif self.openInventory:

            self.display.fill(BLACK)

            self.drawInventory()

        elif self.levelUp:

            self.display.fill(BLACK)

            self.drawLevelUp()

        else:

            self.display.blit(self.background, (0, 0))

            self.drawGrid()

            self.allSprites.draw(self.display)

        pygame.display.flip()

    def drawGrid(self):

        for x in range(0, displayWidth, tiles):

            pygame.draw.line(self.display, (100, 100, 100), (x, 0), (x, displayHeight))

        for y in range(0, displayHeight, tiles):

            pygame.draw.line(self.display, (100, 100, 100), (0, y), (displayWidth, y))

    def drawInventory(self):

        playerInventoryBox = pygame.Rect(700, 0, 324, 400)

        healthText = pygame.font.Font(None, 40)

        health = healthText.render(f'Health: {self.player.health}', True, WHITE)

        manaText = pygame.font.Font(None, 40)

        mana = manaText.render(f'Mana: {self.player.mana}', True, WHITE)

        arrowText = pygame.font.Font(None, 40)

        arrows = arrowText.render(f'Arrows: {self.player.arrowCount}', True, WHITE)

        spikeText = pygame.font.Font(None, 40)

        spikes = spikeText.render(f'Spikes: {self.player.spikeCount}', True, WHITE)        

        pygame.draw.rect(self.display, WHITE, playerInventoryBox, 2)

        deathFont = pygame.font.Font(None, 40)

        deathText = deathFont.render(f'Deaths: {self.deaths}', True, WHITE)

        scoreFont = pygame.font.Font(None, 40)

        scoreText = scoreFont.render(f'Score: {self.score}', True, WHITE)

        levelFont = pygame.font.Font(None, 40)

        levelText = levelFont.render(f'Level: {self.currentRoom}', True, WHITE)

        weaponFont = pygame.font.Font(None, 40)

        weaponText = weaponFont.render(f'Current Weapon: {self.currentWeapon}', True, WHITE)

        self.display.blit(deathText, (displayWidth - 150, displayHeight - 50))

        self.display.blit(scoreText, (10, displayHeight - 50))

        self.display.blit(levelText, (450, 50))
        
        self.display.blit(weaponText, (350, 150))

        self.display.blit(health, (800, 50))

        self.display.blit(mana, (800, 100))

        self.display.blit(arrows, (800, 150))

        self.display.blit(spikes, (800, 200))

        spearSurface = pygame.Surface((295, 95))

        arrowSurface = pygame.Surface((295, 95))

        magicSurface = pygame.Surface((295, 95))

        spearSurface.fill(BLACK)

        arrowSurface.fill(BLACK)

        magicSurface.fill(BLACK)

        if self.highlight == 'Spear':

            spearSurface.fill(GREY)

        elif self.highlight == 'Bow':

            arrowSurface.fill(GREY)

        elif self.highlight == 'Magic':

            magicSurface.fill(GREY)

        spearText = pygame.font.Font(None, 40)

        spear = spearText.render('Spear', True, WHITE)

        pygame.draw.rect(self.display, WHITE, self.spearBox)

        self.display.blit(spearSurface, (0, 0))

        self.display.blit(spear, (100, 35))

        arrowText = pygame.font.Font(None, 40)

        arrow = arrowText.render('Bow and Arrow', True, WHITE)

        pygame.draw.rect(self.display, WHITE, self.arrowBox)

        self.display.blit(arrowSurface, (0, 100))

        self.display.blit(arrow, (40, 135))

        magicText = pygame.font.Font(None, 40)

        magic = magicText.render('Magic', True, WHITE)

        pygame.draw.rect(self.display, WHITE, self.magicBox)

        self.display.blit(magicSurface, (0, 200))

        self.display.blit(magic, (100, 235))

    def drawMenu(self):

        titleFont = pygame.font.Font(None, 200)

        titleText = titleFont.render('Generic RPG', True, (128, 0, 0))

        titleSurface = pygame.Surface((875, 150))

        quitFont = pygame.font.Font(None, 50)

        quitText = quitFont.render('Quit', True, BLACK)

        quitSurface = pygame.Surface((145, 95))

        helpFont = pygame.font.Font(None, 60)

        helpText = helpFont.render('Instructions', True, BLACK)

        helpSurface = pygame.Surface((295, 95))

        startSurface = pygame.Surface((295, 95))

        resumeSurface = pygame.Surface((295, 95))

        restartSurface = pygame.Surface((295, 95))

        titleSurface.fill(BROWN)

        startSurface.fill(BROWN)

        resumeSurface.fill(BROWN)

        restartSurface.fill(BROWN)

        helpSurface.fill(BROWN)

        quitSurface.fill(BROWN)

        if self.highlight == 'Start':

            startSurface.fill(GREY)

        elif self.highlight == 'Resume':

            resumeSurface.fill(GREY)

        elif self.highlight == 'Restart':

            restartSurface.fill(GREY)

        elif self.highlight == 'Help':

            helpSurface.fill(GREY)

        elif self.highlight == 'Quit':

            quitSurface.fill(GREY)

        if self.started:

            resumeFont = pygame.font.Font(None, 100)

            resumeText = resumeFont.render('Resume', True, BLACK)

            restartFont = pygame.font.Font(None, 100)

            restartText = restartFont.render('Restart', True, BLACK)

            pygame.draw.rect(self.display, BLACK, self.resumeButton, 5)

            pygame.draw.rect(self.display, BLACK, self.restartButton, 5)

            self.display.blit(resumeSurface, (displayWidth // 2 - 147, displayHeight // 2 - 97))

            self.display.blit(resumeText, (displayWidth // 2 - 133, displayHeight // 2 - 85))

            self.display.blit(restartSurface, (displayWidth // 2 - 147, displayHeight // 2 + 52))

            self.display.blit(restartText, (displayWidth // 2 - 127, displayHeight // 2 + 65))

            self.display.blit(helpSurface, (displayWidth // 2 - 147, displayHeight // 2 + 202))

            self.display.blit(helpText, (displayWidth // 2 - 127, displayHeight // 2 + 240))

        else:

            startFont = pygame.font.Font(None, 100)

            startText = startFont.render('Start', True, BLACK)

            pygame.draw.rect(self.display, BLACK, self.startButton, 5)

            self.display.blit(startSurface, (displayWidth // 2 - 147, displayHeight // 2 - 47))

            self.display.blit(startText, (displayWidth // 2 - 85, displayHeight // 2 - 30))

            self.display.blit(helpSurface, (displayWidth // 2 - 147, displayHeight // 2 + 152))

            self.display.blit(helpText, (displayWidth // 2 - 125, displayHeight // 2 + 190))

        pygame.draw.rect(self.display, BLACK, self.helpButton, 5)

        self.display.blit(titleSurface, (displayWidth // 2 - 435, displayHeight // 2 - 315))

        self.display.blit(titleText, (displayWidth // 2 - 435, displayHeight // 2 - 300))

        self.display.blit(quitSurface, (displayWidth - 97, displayHeight - 73))

        self.display.blit(quitText, (displayWidth - 85, displayHeight - 50))

        pygame.draw.rect(self.display, BLACK, self.quitButton, 5)

    def drawHelp(self):

        help1Font = pygame.font.Font(None, 40)

        help1Text = help1Font.render('Objective: Get to the next room through the door by any means possible!', True, MAROON)

        help2Font = pygame.font.Font(None, 40)

        help2Text = help2Font.render('Controls:', True, MAROON)

        help3Font = pygame.font.Font(None, 40)

        help3Text = help3Font.render('WASD to move up, left, down, and right', True, MAROON)

        help4Font = pygame.font.Font(None, 40)

        help4Text = help4Font.render('Left Click: Use Sword (No cooldown)', True, MAROON)

        help5Font = pygame.font.Font(None, 40)

        help5Text = help5Font.render('Right Click: Use special weapon (3 second cooldown)', True, MAROON)

        help6Font = pygame.font.Font(None, 40)

        help6Text = help6Font.render('Space Bar: Drop spikes', True, MAROON)

        help7Font = pygame.font.Font(None, 40)

        help7Text = help7Font.render('E: Bring up inventory and switch special weapons you can ', True, MAROON)

        help8Font = pygame.font.Font(None, 40)

        help8Text = help8Font.render('select using your mouse', True, MAROON)

        help9Font = pygame.font.Font(None, 40)

        help9Text = help9Font.render('Use your sword on doors and switches to activate them!', True, RED)

        help10Font = pygame.font.Font(None, 40)

        help10Text = help9Font.render('Avoid getting hit by holes, enemies, and projectiles', True, RED)
        
        help11Font = pygame.font.Font(None, 40)
        
        help11Text = help10Font.render('Use Escape now to go back to the main menu', True, RED)

        help12Font = pygame.font.Font(None, 40)

        help12Text = help11Font.render('You can also use escape to go to the main menu during the game', True, RED)

        self.display.blit(help1Text, (10, 25))

        self.display.blit(help2Text, (10, 100))

        self.display.blit(help3Text, (10, 150))

        self.display.blit(help4Text, (10, 200))

        self.display.blit(help5Text, (10, 250))

        self.display.blit(help6Text, (10, 300))

        self.display.blit(help7Text, (10, 350))

        self.display.blit(help8Text, (10, 400))

        self.display.blit(help9Text, (10, 500))

        self.display.blit(help10Text, (10, 550))

        self.display.blit(help11Text, (10, 600))

        self.display.blit(help12Text, (10, 650))

        holeFont = pygame.font.Font(None, 30)

        holeText = holeFont.render('Hole Example: ', True, RED)

        self.display.blit(holeText, (750, 560))

        self.display.blit(self.holeImage, (900 ,550))

    def drawGameOver(self):
        
        titleFont = pygame.font.Font(None, 200)

        titleText = titleFont.render('You Died', True, (128, 0, 0))

        titleSurface = pygame.Surface((875, 150))

        quitFont = pygame.font.Font(None, 50)

        quitText = quitFont.render('Quit', True, BLACK)

        quitSurface = pygame.Surface((145, 95))

        retrySurface = pygame.Surface((295, 95))

        restartSurface = pygame.Surface((295, 95))

        titleSurface.fill(BROWN)

        retrySurface.fill(BROWN)

        restartSurface.fill(BROWN)

        quitSurface.fill(BROWN)

        if self.highlight == 'Retry':

            retrySurface.fill(GREY)

        elif self.highlight == 'Restart':

            restartSurface.fill(GREY)

        elif self.highlight == 'Quit':

            quitSurface.fill(GREY)

        retryFont = pygame.font.Font(None, 100)

        retryText = retryFont.render('Retry?', True, BLACK)

        restartFont = pygame.font.Font(None, 100)

        restartText = restartFont.render('Restart', True, BLACK)

        pygame.draw.rect(self.display, BLACK, self.retryButton, 5)

        pygame.draw.rect(self.display, BLACK, self.restartButton, 5)

        self.display.blit(retrySurface, (displayWidth // 2 - 147, displayHeight // 2 - 97))

        self.display.blit(retryText, (displayWidth // 2 - 115, displayHeight // 2 - 85))

        self.display.blit(restartSurface, (displayWidth // 2 - 147, displayHeight // 2 + 52))

        self.display.blit(restartText, (displayWidth // 2 - 127, displayHeight // 2 + 65))

        self.display.blit(titleSurface, (displayWidth // 2 - 435, displayHeight // 2 - 315))

        self.display.blit(titleText, (displayWidth // 2 - 325, displayHeight // 2 - 300))

        self.display.blit(quitSurface, (displayWidth - 97, displayHeight - 73))

        self.display.blit(quitText, (displayWidth - 85, displayHeight - 50))

        pygame.draw.rect(self.display, BLACK, self.quitButton, 5)

    def drawGameWin(self):

        titleFont = pygame.font.Font(None, 100)

        titleText = titleFont.render('You completed the game!', True, (0, 255, 0))

        titleSurface = pygame.Surface((875, 150))

        quitFont = pygame.font.Font(None, 50)

        quitText = quitFont.render('Quit', True, BLACK)

        quitSurface = pygame.Surface((145, 95))

        restartSurface = pygame.Surface((295, 95))

        scoreTitleFont = pygame.font.Font(None, 50)

        scoreTitleText = scoreTitleFont.render('Highscores:', True, BLACK)

        score1Font = pygame.font.Font(None, 50)

        score1Text = score1Font.render(f'1: {highscores[0]}', True, BLACK)

        score2Font = pygame.font.Font(None, 50)

        score2Text = score1Font.render(f'2: {highscores[1]}', True, BLACK)

        score3Font = pygame.font.Font(None, 50)

        score3Text = score1Font.render(f'3: {highscores[2]}', True, BLACK)

        score4Font = pygame.font.Font(None, 50)

        score4Text = score1Font.render(f'4: {highscores[3]}', True, BLACK)

        score5Font = pygame.font.Font(None, 50)

        score5Text = score1Font.render(f'5: {highscores[4]}', True, BLACK)

        scoreRect = pygame.Rect(displayWidth // 2 - 150, displayHeight // 2 + 160, 300, 500)

        titleSurface.fill(BROWN)

        restartSurface.fill(BROWN)

        quitSurface.fill(BROWN)

        if self.highlight == 'Restart':

            restartSurface.fill(GREY)

        elif self.highlight == 'Quit':

            quitSurface.fill(GREY)

        restartFont = pygame.font.Font(None, 100)

        restartText = restartFont.render('Restart', True, BLACK)

        pygame.draw.rect(self.display, BLACK, self.restartButton, 5)

        pygame.draw.rect(self.display, BROWN, scoreRect)

        self.display.blit(scoreTitleText, (displayWidth // 2 - 127, displayHeight // 2 + 170))

        self.display.blit(score1Text, (displayWidth // 2 - 127, displayHeight // 2 + 205))

        self.display.blit(score2Text, (displayWidth // 2 - 127, displayHeight // 2 + 240))

        self.display.blit(score3Text, (displayWidth // 2 - 127, displayHeight // 2 + 275))

        self.display.blit(score4Text, (displayWidth // 2 - 127, displayHeight // 2 + 308))

        self.display.blit(score5Text, (displayWidth // 2 - 127, displayHeight // 2 + 343))

        self.display.blit(restartSurface, (displayWidth // 2 - 147, displayHeight // 2 + 52))

        self.display.blit(restartText, (displayWidth // 2 - 127, displayHeight // 2 + 65))

        self.display.blit(titleSurface, (displayWidth // 2 - 435, displayHeight // 2 - 315))

        self.display.blit(titleText, (displayWidth // 2 - 420, displayHeight // 2 - 290))

        self.display.blit(quitSurface, (displayWidth - 97, displayHeight - 73))

        self.display.blit(quitText, (displayWidth - 85, displayHeight - 50))

        pygame.draw.rect(self.display, BLACK, self.quitButton, 5)

    def drawLevelUp(self):

        levelUpFont = pygame.font.Font(None, 80)

        levelUpText = levelUpFont.render('You Leveled Up!', True, WHITE)

        self.display.blit(levelUpText, (displayWidth // 2 - 220, 75))

        healthSurface = pygame.Surface((595, 95))

        damageSurface = pygame.Surface((595, 95))

        replenishSurface = pygame.Surface((595, 95))

        healthSurface.fill(BLACK)

        damageSurface.fill(BLACK)

        replenishSurface.fill(BLACK)

        if self.highlight == 'Health':

            healthSurface.fill(GREY)

        elif self.highlight == 'Damage':

            damageSurface.fill(GREY)

        elif self.highlight == 'Projectile':

            replenishSurface.fill(GREY)

        healthFont = pygame.font.Font(None, 40)

        healthText = healthFont.render('Health', True, WHITE)

        pygame.draw.rect(self.display, WHITE, self.healthBox)

        self.display.blit(healthSurface, (displayWidth // 2 - 298, 213))

        self.display.blit(healthText, (displayWidth // 2 - 50, 250))

        damageFont = pygame.font.Font(None, 40)

        damageText = damageFont.render('Damage', True, WHITE)

        pygame.draw.rect(self.display, WHITE, self.damageBox)

        self.display.blit(damageSurface, (displayWidth // 2 - 297, 413))

        self.display.blit(damageText, (displayWidth // 2 - 50, 450))

        replenishFont = pygame.font.Font(None, 40)

        replenishText = replenishFont.render('Replenish Projectiles', True, WHITE)

        pygame.draw.rect(self.display, WHITE, self.replenishBox)

        self.display.blit(replenishSurface, (displayWidth // 2 - 297, 613))

        self.display.blit(replenishText, (displayWidth // 2 - 150, 650))       

    ########################
    # PATHFINDING ALGORITHM
    ########################

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

    ###########################
    # Helper functions
    ###########################

    def vectorToInteger(self, vector):

        return (int(vector.x), int(vector.y))

    def mergeDictionaries(self, dict1, dict2):

        newDict = copy.deepcopy(dict1)

        for key, value in dict1.items():
            
            newDict[key] = value + dict2[key]

        return newDict

###############
# Player
###############

class Player(pygame.sprite.Sprite):

    def __init__(self, game, x, y):

        self.groups = game.allSprites, game.friendlies

        pygame.sprite.Sprite.__init__(self, self.groups)

        self.game = game

        self.god = False

        self.orientation = 'Down'

        self.image = getPlayerImageOrientation(self.orientation)

        self.rect = self.image.get_rect()

        self.rotation = 0

        self.vel = vector(0, 0)

        self.pos = vector(x, y) * tiles

        self.swing = False

        self.health = 100

        self.damage = 0

        self.arrowCount = 10

        self.mana = 100

        self.spikeCount = 5

        self.stats = {'health': 100, 'arrowCount': 10, 'mana': 100, 'spikeCount': 5}

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

    @staticmethod
    def obstacleCollide(sprite, moveDirection):

        collision = pygame.sprite.spritecollide(sprite, sprite.game.obstacles, False)

        if moveDirection == 'dx':

            if collision:

                if sprite.vel.x > 0:
                
                    sprite.pos.x = collision[0].rect.left - sprite.rect.width

                elif sprite.vel.x < 0:

                    sprite.pos.x = collision[0].rect.right

                sprite.vel.x = 0

                sprite.rect.x = int(sprite.pos.x)

        elif moveDirection == 'dy':

            if collision:

                if sprite.vel.y > 0:
                
                    sprite.pos.y = collision[0].rect.top - sprite.rect.height

                elif sprite.vel.y < 0:

                    sprite.pos.y = collision[0].rect.bottom

                sprite.vel.y = 0

                sprite.rect.y = int(sprite.pos.y)

    def swing(self):

        self.swing = True

    def update(self):

        if self.health <= 0 and not self.god:

            self.kill()

            self.game.deaths += 1

            self.game.score -= 500

            self.game.gameOver = True

        frameTime = self.game.clock.get_time() / 1000

        if self.swing:

            self.image = getSwingOrientation(self.orientation)

        else:

            self.image = getPlayerImageOrientation(self.orientation)

        self.pos += self.vel * frameTime

        self.rect.x = int(self.pos.x)

        self.obstacleCollide(self, 'dx')

        self.rect.y = int(self.pos.y)

        self.obstacleCollide(self, 'dy')

###################
# Enemies
###################

class BasicEnemy(pygame.sprite.Sprite):

    def __init__(self, game, x, y):

        self.groups = game.allSprites, game.enemies, game.mobs

        pygame.sprite.Sprite.__init__(self, self.groups)

        self.game = game
        
        self.image = getEnemyImage('basic')

        self.rect = self.image.get_rect()

        self.vel = vector(0, 0)

        self.pos = vector(x, y) * tiles

        self.rect.center = self.pos

        self.health = 500

        self.damage = 25

        self.knockback = 0

    def update(self):

        self.attackDir = vector.normalize(self.game.player.pos - self.pos)

        if self.health <= 0:

            self.game.score += 500

            self.kill()

        try:        

            self.acceleration = self.game.path[game.vectorToInteger(self.pos // tiles)]

        except:

            self.acceleration = vector(0, 0)

        self.vel += self.acceleration

        if self.vel != vector(0, 0):

            self.vel = vector.normalize(self.vel)

        if self.knockback > 0:

            self.pos += -self.attackDir * self.knockback

            self.knockback = 0

        else:

            self.pos += self.vel * 3

        self.rect.center = self.pos

class RangedEnemy(pygame.sprite.Sprite):

    def __init__(self, game, x, y):

        self.groups = game.allSprites, game.enemies, game.mobs

        pygame.sprite.Sprite.__init__(self, self.groups)

        self.game = game

        self.image = getEnemyImage('ranged')

        self.rect = self.image.get_rect()

        self.vel = vector(0, 0)

        self.pos = vector(x, y) * tiles

        self.rect.center = self.pos

        self.health = 250

        self.knockback = 0

        self.damage = 20

        self.lastAttack = pygame.time.get_ticks()

        self.fireRate = 3000

    def attack(self):

        self.lastAttack = pygame.time.get_ticks()

        EnemyProjectile(self.game, self, self.attackDir)

    def lineOfSight(self):

        sightLine = pygame.draw.line(self.game.display, BLACK, self.pos, self.game.player.pos)

        for wall in self.game.obstacles:

            if sightLine.colliderect(wall.rect):

                return False

        return True

    def update(self):

        self.attackDir = vector.normalize(self.game.player.pos - self.pos)

        if self.health <= 0:

            self.game.score += 250

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

        if self.knockback > 0:

            self.pos += -self.attackDir * self.knockback

            self.knockback = 0

        else:

            self.pos += self.vel * 3

        self.rect.center = self.pos

class Boss(RangedEnemy):

    def __init__(self, game, x, y):

        self.groups = game.allSprites, game.enemies, game.boss, game.mobs

        pygame.sprite.Sprite.__init__(self, self.groups)

        self.game = game
        
        self.image = getEnemyImage('boss')

        self.rect = self.image.get_rect()

        self.pos = vector(x, y) * tiles

        self.rect.center = self.pos

        self.lastAttack = pygame.time.get_ticks()

        self.acceleration = vector(0, 0)

        self.vel = vector(0, 0)

        self.health = 1000

        self.damage = 25

    def move(self):

        try:

            self.acceleration = self.game.path[game.vectorToInteger(self.pos // tiles)]

        except:

            self.acceleraton = vector(0, 0)

            self.vel = vector(0, 0)

    def update(self):

        self.attackDir = vector.normalize(self.game.player.pos - self.pos)

        currentTime = pygame.time.get_ticks()

        if self.health <= 0:

            self.kill()

            self.game.score += 1000

            highscores.append(self.game.score)

            highscores.sort(reverse = True)

            self.game.score = 0

            self.game.win = True

        if (self.health > 800) and (
            currentTime - self.lastAttack >= 500):

            self.lastAttack = currentTime

            self.move()

            self.acceleration *= -1

            self.attack()

        elif (200 < self.health < 800):

            self.move()

            if currentTime - self.lastAttack >= 5000:

                self.pos += self.vel * 25

                self.rect.center = self.pos

                hits = pygame.sprite.spritecollide(self, self.game.obstacles, False)

                if hits:

                    self.lastAttack = currentTime

                    self.rect.x = int(self.pos.x)

                    self.game.player.obstacleCollide(self, 'dx')

                    self.rect.y = int(self.pos.y)

                    self.game.player.obstacleCollide(self, 'dy')

            else:

                self.vel += self.acceleration

                if self.vel != vector(0, 0):

                    self.vel = vector.normalize(self.vel)

                    self.pos += self.vel * 7

                self.rect.center = self.pos

        elif self.health < 200:

            self.move()

            self.vel += self.acceleration

            if self.vel != vector(0, 0):

                self.vel = vector.normalize(self.vel)

            self.pos += self.vel * 5

            self.rect.center = self.pos

            if currentTime - self.lastAttack >= 250:

                self.attack()

class EnemyProjectile(pygame.sprite.Sprite):

    def __init__(self, game, enemy, direction):

        self.groups = game.allSprites, game.enemies

        pygame.sprite.Sprite.__init__(self, self.groups)

        self.game = game

        self.rangedEnemy = enemy

        self.direction = direction

        self.originalImage = getWeaponImage('Arrow')

        self.image = pygame.transform.rotate(self.originalImage, 180)

        self.rect = self.image.get_rect()

        self.pos = copy.copy(self.rangedEnemy.pos)

        self.rect.center = self.pos
        
        self.damage = 50

        self.knockback = 0

    def update(self):

        if pygame.sprite.spritecollideany(self, self.game.obstacles):

            self.kill()

        if pygame.sprite.spritecollide(self, self.game.friendlies, False):

            self.kill()

        if pygame.sprite.spritecollide(self, self.game.weapons, True):

            self.game.score += 10

            self.kill()

        self.pos += self.direction * 10

        self.rect.center = self.pos

###################
# Obstacles
###################

class Floor(pygame.sprite.Sprite):

    def __init__(self, game, x, y, image):

        self.groups = game.allSprites

        pygame.sprite.Sprite.__init__(self, self.groups)

        self.image = image

        self.rect = self.image.get_rect()

        self.pos = vector(x, y) * tiles

        self.rect.topleft = self.pos

class Door(pygame.sprite.Sprite):

    def __init__(self, game, x, y, image, purpose = 'open'):

        self.groups = game.allSprites, game.obstacles, game.interactable

        pygame.sprite.Sprite.__init__(self, self.groups)

        self.game = game

        self.originalImage = image

        self.image = self.originalImage

        self.rect = self.image.get_rect()

        self.pos = vector(x, y) * tiles
        
        self.rect.topleft = self.pos

        self.purpose = purpose

        self.open = False

    def update(self):

        if self.open:

            if self.purpose == 'open':

                self.remove(self.game.obstacles)

            elif self.purpose == 'removeBlocker':

                self.game.blocker.empty()

            elif self.purpose == 'nextRoom':

                self.game.currentRoom += 1

                self.game.changeRoom()

                self.game.score += 500

                self.game.levelUp = True

        else:

            self.add(self.game.obstacles)

            self.image = self.originalImage

            self.health = 0

class Obstacle(pygame.sprite.Sprite):

    def __init__(self, game, x, y, image):

        self.groups = game.allSprites, game.obstacles

        pygame.sprite.Sprite.__init__(self, self.groups)

        self.game = game

        self.image = image

        self.rect = self.image.get_rect()

        self.pos = vector(x, y) * tiles

        self.rect.topleft = self.pos

class Hole(Obstacle):

    def __init__(self, game, x, y, image):

        self.groups = game.allSprites, game.enemies

        pygame.sprite.Sprite.__init__(self, self.groups)

        self.game = game

        self.image = image 

        self.rect = self.image.get_rect()

        self.pos = vector(x, y) * tiles

        self.rect.topleft = self.pos

        self.damage = 100

class Blocker(Obstacle):

    def __init__(self, game, x, y, image):

        self.groups = game.allSprites, game.obstacles, game.blocker

        pygame.sprite.Sprite.__init__(self, self.groups)

        self.game = game
        
        self.image = image

        self.rect = self.image.get_rect()

        self.pos = vector(x, y) * tiles

        self.rect.topleft = self.pos

        self.switch = False

    def update(self):

        if self not in self.game.blocker and (
            self.pos in self.game.walls
        ):

            self.kill()

            self.game.walls.remove(self.pos)

        elif self in self.game.blocker and (
            self.pos not in self.game.walls
        ):

            self.add(self.game.allSprites)

            self.add(self.game.obstacles)

            self.game.walls.append(self.pos)

################
# Weapons
################

# Replace with sword eventually
class Spear(pygame.sprite.Sprite):

    def __init__(self, game, player):

        self.groups = game.allSprites, game.weapons

        pygame.sprite.Sprite.__init__(self, self.groups)

        self.game = game

        self.player = player

        self.direction = player.orientation

        self.originalImage = getWeaponImage('Spear')

        self.image = self.originalImage

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

            self.image = pygame.transform.rotate(self.originalImage, 240)

        elif self.direction == 'Up':

            offset = vector(-10, -30)

            self.image = pygame.transform.rotate(self.originalImage, 60)

        elif self.direction == 'Right':

            offset = vector(20, -10)

            self.image = pygame.transform.rotate(self.originalImage, 330)

        elif self.direction == 'Left':

            offset = vector(-50, 0)

            self.image = pygame.transform.rotate(self.originalImage, 150)

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

        self.originalImage = getWeaponImage('Arrow')

        self.image = self.originalImage

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

        self.knockack = 2

    def update(self):

        if pygame.sprite.spritecollideany(self, self.game.obstacles):

            self.kill()

        if pygame.sprite.spritecollideany(self, self.game.mobs):

            self.kill()

        self.pos += self.vel

        self.rect.center = self.pos

class Magic(pygame.sprite.Sprite):

    def __init__(self, game, player):

        self.groups = game.allSprites, game.weapons

        pygame.sprite.Sprite.__init__(self, self.groups)

        self.game = game

        self.player = player

        self.image = getWeaponImage('Magic')

        self.rect = self.image.get_rect()

        self.vel = vector(0, 0)

        self.pos = copy.copy(self.player.pos)

        self.rect.center = self.pos

        self.spawnTime = pygame.time.get_ticks()
        
        self.damage = 15

        self.knockback = 0

    def update(self):

        self.currentTime = pygame.time.get_ticks()

        if self.currentTime - self.spawnTime > 1000:

            self.player.mana -= 10

            self.spawnTime = self.currentTime

        if pygame.sprite.spritecollideany(self, self.game.obstacles) or (
            self.player.mana <= 0):

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

        self.originalImage = getWeaponImage('Spikes')

        self.image = self.originalImage

        self.rect = self.image.get_rect()

        self.pos = self.player.pos

        self.rect.center = self.pos

        self.spawnTime = pygame.time.get_ticks()
        
        self.damage = 10

        self.knockback = 0.1

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

        self.originalImage = pygame.Surface((tiles * 0.5, tiles), pygame.SRCALPHA, 32).convert_alpha()

        self.image = self.originalImage

        self.rect = self.image.get_rect()

        self.pos = self.player.pos

        self.rect.topleft = self.pos

        self.spawnTime = pygame.time.get_ticks()

        self.damage = 30

        self.knockback = 5

    def update(self):

        hits = pygame.sprite.spritecollide(self, self.game.interactable, False)

        for hit in hits:

            hit.open = not hit.open

        frameTime = self.game.clock.get_time() // 10

        if (pygame.time.get_ticks() - self.spawnTime) > 150:

            self.player.swing = False

            self.kill()

        if self.direction == 'Down':

            offset = vector(-7, 30)

            self.image = pygame.transform.rotate(self.originalImage, 270)

        elif self.direction == 'Up':

            offset = vector(-7, -10)

            self.image = pygame.transform.rotate(self.originalImage, 90)

        elif self.direction == 'Right':

            offset = vector(15, -5)

            self.image = pygame.transform.rotate(self.originalImage, 0)

        elif self.direction == 'Left':

            offset = vector(-15, 0)

            self.image = pygame.transform.rotate(self.originalImage, 180)

        self.rect.topleft = self.player.pos + offset

# Run the game

game = Game()

while True:

    game.initializeGame()

    game.newGame()