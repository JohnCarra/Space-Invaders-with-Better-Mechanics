#!/usr/bin/env python3

import pygame
from pygame import mixer
import random
import math

# Initialize the pygames library
pygame.init()

# create our first screen
screen = pygame.display.set_mode((800, 600))

# Background
background = pygame.image.load('Sprites/background.png')

# Sound
mixer.music.load("Sounds/background.wav")
mixer.music.play(-1)

#Caption and Icon
# Set the title to space invadors on the window
pygame.display.set_caption("Space Invaders")
icon = pygame.image.load('ufo.png')  # Set icon variable equal to our png
pygame.display.set_icon(icon)  # set the icon to the value of our icon variable

# Player
# set player variable equal to player.png image
playerImg = pygame.image.load('Sprites/player.png')
playerX = 370  # X-Axis
playerY = 480  # Y-AXis
playerX_change = 0

# Enemy
# set enemy variable equal to player.png image
enemyImg = []
enemyX = []
enemyY = []
enemyX_change = []
enemyY_change = []
num_of_enemies = 6

for i in range(num_of_enemies):
    enemyImg.append(pygame.image.load('Sprites/enemy.png'))
    enemyX.append(random.randint(0, 735))  # X-Axis
    enemyY.append(random.randint(30, 150))  # Y-AXis
    enemyX_change.append(0.1)
    enemyY_change.append(40)

# Laser
# ready state means laser is not rendered
# fire means the laser is in motion
laserImg = pygame.image.load('Sprites/laser.png')
laserX = 0  # X-Axis
laserY = 480  # Y-AXis
laserX_change = 0
laserY_change = 2
laser_state = "ready"

# Score

score_value = 0
font = pygame.font.Font('freesansbold.ttf', 32)

textX = 10
testY = 10

# Game Over
over_font = pygame.font.Font('freesansbold.ttf', 64)


def show_score(x, y):
    score = font.render("Score : " + str(score_value), True, (255, 255, 255))
    screen.blit(score, (x, y))


def game_over_text():
    over_text = over_font.render("GAME OVER", True, (255, 255, 255))
    screen.blit(over_text, (200, 250))


def player(x, y):
    # drawing our player image using blit method 3 parameters with the image and x/y coordinates
    screen.blit(playerImg, (x, y))


def enemy(x, y, i):
    # drawing our enemy image using blit method 3 parameters with the image and x/y coordinates
    screen.blit(enemyImg[i], (x, y))


def fire_laser(x, y):
    global laser_state
    laser_state = "fire"  # change state to fire
    # draw laser on screen, numbers offset laser location to place it at the center of player
    screen.blit(laserImg, (x + 16, y + 10))


# laser collison function using distance formula
def isCollision(enemyX, enemyY, laserX, laserY):
    distance = math.sqrt((math.pow(enemyX - laserX, 2)) +
                         (math.pow(enemyY - laserY, 2)))
    if distance < 27:
        return True
    else:
        return False


# Game Loop
running = True  # variable to check if our game is running defaults to true
while running:  # while loop for game running
    # creating a tuple with RGB values for background
    screen.fill((0, 0, 0))
    # Background Image
    screen.blit(background, (0, 0))  # draw back ground
    for event in pygame.event.get():   # for loop to check for a event trigger from pygames
        if event.type == pygame.QUIT:  # once the quit event presents itself by clicking the exit button it changes the value of running
            running = False            # running will equal false which will terminate our program
    # if keystroke is pressed check whether its right or left
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:  # movement
                playerX_change = -0.9
            if event.key == pygame.K_RIGHT:  # movement
                playerX_change = +0.9
            if event.key == pygame.K_SPACE:  # space bar to shoot laser
                if laser_state == "ready":  # prevents spamming spacebar bug
                    laserX = playerX
                    fire_laser(laserX, laserY)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                playerX_change = 0

    # Player Movement
    playerX += playerX_change  # set our playerX variable equal to our playerX change value

    if playerX <= 0:
        playerX = 0
    elif playerX >= 736:
        playerX = 736

    # Enemy Movement
    for i in range(num_of_enemies):
        # Game Over
        if enemyY[i] > 440:
            for j in range(num_of_enemies):
                enemyY[j] = 2000
            game_over_text()
            break
        enemyX[i] += enemyX_change[i]
        if enemyX[i] <= 0:
            enemyX_change[i] = 0.4
            enemyY[i] += enemyY_change[i]
        elif enemyX[i] >= 736:
            enemyX_change[i] = -0.4
            enemyY[i] += enemyY_change[i]
    # Collision
    # Resets enemy position after collision is detected
        collision = isCollision(enemyX[i], enemyY[i], laserX,
                                laserY)  # stores value of T/F
        if collision:
            laserY = 480  # starting position of player
            laser_state = "ready"  # ready to fire again
            score_value += 1  # increase score by 1
            enemyX[i] = random.randint(0, 735)  # X-Axis
            enemyY[i] = random.randint(30, 150)  # Y-AXis
        enemy(enemyX[i], enemyY[i], i)

    # Laser Movement
    if laserY <= 0:  # resets our laser to be able to shoot again
        laserY = 480
        laser_state = "ready"
    if laser_state is "fire":
        fire_laser(laserX, laserY)
        laserY -= laserY_change

    player(playerX, playerY)  # call player method
    show_score(textX, testY)
    pygame.display.update()  # update our screen
