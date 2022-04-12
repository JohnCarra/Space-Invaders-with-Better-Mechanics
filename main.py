#!/usr/bin/env python3

import pygame
import pygame.freetype
from pygame.sprite import Sprite
from pygame.rect import Rect
from enum import Enum
from pygame.sprite import RenderUpdates
import random
import math

pygame.init()

WHITE = (255, 255, 255)

# Window size
width = 800
height = 800

screen = pygame.display.set_mode((width, height))

# Set frames per second
clock = pygame.time.Clock()
fps = 60

# For spawning enemies
rows = 4
cols = 9
cols_2 = 50

# For stopping the spawning of lasers at end of level
stop = 0

# Firerate of enemies
enemy_cooldown = 1000 #milliseconds?
last_enemy_shot = pygame.time.get_ticks()

# Freeze screen before beginning level starts
countdown = 3
last_count = pygame.time.get_ticks()

# How long power up lasts
power_up_time = 0
power_cooldown = pygame.time.get_ticks()

# Timer for displaying next level
next = 10
next_count = pygame.time.get_ticks()

# Timer for when end of level for barrage
end_timer = pygame.time.get_ticks()


# Background image and level one image
background = pygame.image.load('Sprites/background.png')
background = pygame.transform.scale(background, (width, height))

# Level two image
background_two = pygame.image.load('Sprites/background_two.png')
background_two = pygame.transform.scale(background_two, (width, height))

# Caption and Icon
# Set the title to space invadors on the window
pygame.display.set_caption("Space Invaders")
icon = pygame.image.load('Sprites/ufo.png')
pygame.display.set_icon(icon)







# Returns surface with text written on
def create_surface_with_text(text, font_size, text_rgb):
    font = pygame.freetype.SysFont("Courier", font_size, bold=True)
    surface, _ = font.render(text=text, fgcolor=text_rgb)
    return surface.convert_alpha()


# Puts text onto screen
def draw_text(x, y, text, font_size, text_rgb):
    img = font.render(text, True, text_rgb)
    text_rect = img.get_rect(center = (x / 2, y))
    screen.blit(img, text_rect)


# Buttons that can't be clicked
class UIPlain(Sprite):
    """ An user interface element that can be added to a surface """

    def __init__(self, center_position, text, font_size, text_rgb):

        self.mouse_over = False

        default_image = create_surface_with_text(
            text=text, font_size=font_size, text_rgb=text_rgb
        )

        highlighted_image = create_surface_with_text(
            text=text, font_size=font_size * 1.2, text_rgb=text_rgb
        )

        self.images = [default_image, highlighted_image]

        self.rects = [
            default_image.get_rect(center=center_position),
            highlighted_image.get_rect(center=center_position),
        ]

        super().__init__()

    @property
    def image(self):
        return self.images[1] if self.mouse_over else self.images[0]

    @property
    def rect(self):
        return self.rects[1] if self.mouse_over else self.rects[0]

    def draw(self, surface):
        """ Draws element onto a surface """
        surface.blit(self.image, self.rect)


# Buttons that can be clicked
class UIElement(Sprite):
    """ An user interface element that can be added to a surface """

    def __init__(self, center_position, text, font_size, text_rgb, action=None):
        """
        Args:
            center_position - tuple (x, y)
            text - string of text to write
            font_size - int
            text_rgb (text colour) - tuple (r, g, b)
            action - the gamestate change associated with this button
        """
        self.mouse_over = False

        default_image = create_surface_with_text(
            text=text, font_size=font_size, text_rgb=text_rgb
        )

        highlighted_image = create_surface_with_text(
            text=text, font_size=font_size * 1.2, text_rgb=text_rgb
        )

        self.images = [default_image, highlighted_image]

        self.rects = [
            default_image.get_rect(center=center_position),
            highlighted_image.get_rect(center=center_position),
        ]

        self.action = action

        super().__init__()

    @property
    def image(self):
        return self.images[1] if self.mouse_over else self.images[0]

    @property
    def rect(self):
        return self.rects[1] if self.mouse_over else self.rects[0]

    def update(self, mouse_pos, mouse_up):
        """ Updates the mouse_over variable and returns the button's
            action value when clicked.
        """
        if self.rect.collidepoint(mouse_pos):
            self.mouse_over = True
            if mouse_up:
                return self.action
        else:
            self.mouse_over = False

    def draw(self, surface):
        """ Draws element onto a surface """
        surface.blit(self.image, self.rect)


# Game state machine, helps transition to different screens
def main():
    game_state = GameState.TITLE

    while True:
        if game_state == GameState.TITLE:
            game_state = title_screen(screen)

        if game_state == GameState.NEWGAME:
            game_state = game_start()

        if game_state == GameState.DEAD:
            game_state = game_over()

        if game_state == GameState.SECOND:
            game_state = second_level()

        if game_state == GameState.QUIT:
            pygame.quit()
            return


# Draws buttons on screen and checks if a button has been clicked
def game_loop(screen, buttons):
    """ Handles game loop until an action is return by a button in the
        buttons sprite renderer.
    """
    while True:

        screen.blit(background, (0,0))

        mouse_up = False
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_up = True

        for button in buttons:
            ui_action = button.update(pygame.mouse.get_pos(), mouse_up)
            if ui_action is not None:
                return ui_action

        buttons.draw(screen)
        pygame.display.flip()


# Title screen
def title_screen(screen):

    start_btn = UIElement(
        center_position=(400, 400),
        font_size=30,
        text_rgb=WHITE,
        text="Start",
        action=GameState.NEWGAME,
    )
    quit_btn = UIElement(
        center_position=(400, 500),
        font_size=30,
        text_rgb=WHITE,
        text="Quit",
        action=GameState.QUIT,
    )

    buttons = RenderUpdates(start_btn, quit_btn)

    return game_loop(screen, buttons)


# Display score
font = pygame.font.Font('freesansbold.ttf', 25)

def show_score():
    score = font.render("Score : " + str(playerShip.score), True, WHITE)
    screen.blit(score, (1, 775))
    health = font.render("Health : " + str(playerShip.health), True, WHITE)
    screen.blit(health, (681, 775))


# Game over screen
def game_over():

    game_over =  UIPlain(
        center_position = (400, 200),
        font_size = 70,
        text_rgb = WHITE,
        text = "GAME OVER",
    )

    final_score = UIPlain(
        center_position = (400, 300),
        font_size = 30,
        text_rgb = WHITE,
        text = "Final Score : " + str(playerShip.score),
    )

    retry_btn = UIElement(
        center_position=(400, 400),
        font_size=30,
        text_rgb=WHITE,
        text="Retry?",
        action=GameState.NEWGAME,
    )

    menu_btn = UIElement(
        center_position=(400, 650),
        font_size=30,
        text_rgb=WHITE,
        text="Main Menu",
        action=GameState.TITLE,
    )

    quit_btn = UIElement(
        center_position=(400, 700),
        font_size=30,
        text_rgb=WHITE,
        text="Quit",
        action=GameState.QUIT,
    )

    playerShip.reset(width / 2, height - 100, 8, 5, 0, 500, "player.png")
    player_sprite.add(playerShip)
    all_lasers.empty()
    all_enemies.empty()
    all_enemies_lasers.empty()
    obstacle.empty()
    rock.empty()
    create_enemies()

    fast = Power(random.randint(10, width - 20), random.randint(-100, -50))
    power_up.add(fast)

    for i in range(1, 20):
        meteorite = Obstacle(random.randint(10, width - 20), random.randint(-5000, -50))
        obstacle.add(meteorite)

    global countdown
    countdown = 4

    buttons = RenderUpdates(retry_btn, menu_btn, quit_btn, game_over, final_score)

    return game_loop(screen, buttons)


# Next Level
def second_level():
    playerShip.reset(width / 2, height - 100, 8, playerShip.health, playerShip.score, 500, "Sprites/car.png")
    running = True
    while running:

        screen.blit(background_two, (0,0))

        clock.tick(fps)

        global countdown
        global last_count
        global power_up_time
        global next_count
        global next
        game_state = None

        time_now = pygame.time.get_ticks()

        # Pressing escape while in a game closes window
        for event in pygame.event.get():   # for loop to check for a event trigger from pygames
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:     #Pressing escape key will quit the game
                    running = False

        if countdown == 0:
            #if time_now - last_enemy_shot > enemy_cooldown and len(all_enemies_lasers) < 5 and len(all_enemies) > 0:
            #    attacking_enemy = random.choice(all_enemies.sprites())
            #    enemy_laser = Enemy_Laser(attacking_enemy.rect.centerx, attacking_enemy.rect.bottom)
            #    all_enemies_lasers.add(enemy_laser)


            game_state = playerShip.update()
            #all_lasers.update()
            #all_enemies.update()
            #all_enemies_lasers.update()
            #power_up.update()
            #obstacle.update()

            # How long the power up lasts
            #if power_up_time == 0:
            #    playerShip.cooldown = 500
            #if power_up_time > 0:
            #    down = pygame.time.get_ticks()
            #    if down - next > 800:
            #        playerShip.cooldown = 0
            #        power_up_time -= 1
            #        next = down

            #if len(all_enemies) == 0:
            #    draw_text(width, 450, "Complete!", font, WHITE)
            #    freeze = pygame.time.get_ticks()
            #    if next > 0:
            #        if freeze - next_count > 1000:
            #            next -= 1
            #            next_count = freeze
            #    if next == 0:
            #        return GameState.SECOND

        if countdown > 0:
            draw_text(width, 450, "READY!", font, WHITE)
            draw_text(width, 490, str(countdown), font, WHITE)
            count_timer = pygame.time.get_ticks()
            if count_timer - last_count > 1500:
                countdown -= 1
                last_count = count_timer

        player_sprite.draw(screen)
        #all_lasers.draw(screen)
        #all_enemies.draw(screen)
        #all_enemies_lasers.draw(screen)
        #power_up.draw(screen)
        #obstacle.draw(screen)

        show_score()
        pygame.display.update()  # update our screen

        for event in pygame.event.get():   # for loop to check for a event trigger from pygames
            if event.type == pygame.QUIT:  # once the quit event presents itself by clicking the exit button it changes the value of running
                running = False            # running will equal false which will terminate our program

        if game_state == GameState.DEAD:
            return GameState.DEAD

    return GameState.QUIT



# Player class
class Ship(pygame.sprite.Sprite):
    """ Stores information about a ship """
    def __init__(self, x, y, speed, health, score, cooldown, picture):

        super().__init__()

        self.reset(x, y, speed, health, score, cooldown, picture)


    def update(self):

        #cooldown = 500 # milliseconds
        game_state = None

        # Registers multiple keys
        keys = pygame.key.get_pressed()

        # Player movement
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if (keys[pygame.K_RIGHT] and self.rect.right < width):
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if (keys[pygame.K_DOWN] and self.rect.bottom < height):
            self.rect.y += self.speed

        time_now = pygame.time.get_ticks()

        # Player shoot
        if keys[pygame.K_SPACE] and time_now - self.last_shot > playerShip.cooldown:
            laser = Laser(self.rect.centerx, self.rect.top)
            all_lasers.add(laser)
            self.last_shot = pygame.time.get_ticks()

        # Pixel perfect collision
        self.mask = pygame.mask.from_surface(self.image)

        # Death
        if self.health <= 0:
            self.kill()
            return GameState.DEAD

    def reset(self, x, y, speed, health, score, cooldown, picture):
        self.speed = speed
        self.health = health
        self.score = score
        self.cooldown = cooldown

        #Draw the ship
        self.image = pygame.image.load(picture).convert_alpha()
        self.image = pygame.transform.scale(self.image, (32, 32))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.last_shot = pygame.time.get_ticks()


# Laser class
class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y):

        super().__init__()

        self.image = pygame.image.load("Sprites/laser.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y -= 8
        if self.rect.bottom < 0:
            self.kill()
        if pygame.sprite.spritecollide(self, all_enemies, True):
            playerShip.score += 100
            self.kill()
        if pygame.sprite.spritecollide(self, obstacle, False):
            self.kill()


# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):

        super().__init__()

        self.speed = speed

        #Draw the enemy
        self.image = pygame.image.load("Sprites/enemy.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (32, 32))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.x += self.speed
        if self.rect.right > width:
            self.rect.y += 55
            self.speed = -self.speed
        elif self.rect.left < 0:
            self.rect.y += 55
            self.speed = abs(self.speed)

        if pygame.sprite.spritecollide(self, player_sprite, False, pygame.sprite.collide_mask):
            self.kill()
            playerShip.health -= 1


# Enemy laser class
class Enemy_Laser(pygame.sprite.Sprite):
    def __init__(self, x, y):

        super().__init__()

        self.image = pygame.image.load("Sprites/laser.png").convert_alpha()
        self.image = pygame.transform.rotate(self.image, 180)
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y += 5
        if self.rect.top > height:
            self.kill()
        if pygame.sprite.spritecollide(self, player_sprite, False, pygame.sprite.collide_mask):
            self.kill()
            playerShip.health -= 1
        if pygame.sprite.spritecollide(self, rock, False):
            self.kill()


# Power up class
class Power(pygame.sprite.Sprite):
    def __init__(self, x, y):

        super().__init__()

        self.image = pygame.image.load("Sprites/crate.png").convert_alpha()

        self.image = pygame.transform.scale(self.image, (32, 32))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):

        global power_up_time

        self.rect.y += 5
        if self.rect.top > height:
            self.kill()
        if pygame.sprite.spritecollide(self, player_sprite, False):
            self.kill()
            power_up_time = 5


# Obstacle class
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y):

        super().__init__()

        self.image = pygame.image.load("Sprites/meteorite.png").convert_alpha()

        self.image = pygame.transform.scale(self.image, (32, 32))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):

        self.rect.y += 5
        if self.rect.top > height:
            self.kill()
        if pygame.sprite.spritecollide(self, player_sprite, False):
            playerShip.health -= 1
            self.kill()


# Obstacle class
class Rock(pygame.sprite.Sprite):
    def __init__(self, x, y):

        super().__init__()

        self.image = pygame.image.load("Sprites/meteorite.png").convert_alpha()

        self.image = pygame.transform.scale(self.image, (64, 64))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):

        self.rect.x -= 1.5
        if self.rect.right < 0:
            self.kill()


# Initializing lists
player_sprite = pygame.sprite.Group()
all_lasers = pygame.sprite.Group()
all_enemies = pygame.sprite.Group()
all_enemies_lasers = pygame.sprite.Group()
power_up = pygame.sprite.Group()
obstacle = pygame.sprite.Group()
rock = pygame.sprite.Group()


# Creating enemies
def create_enemies():
    for row in range(rows):
        for item in range(cols):
            #Enemy(buffer to the left + pixels apart, buffer at the top + pixels apart)
            enemy = Enemy((80 + item * 80), (50 + row * 100), 4)
            all_enemies.add(enemy)

create_enemies()

# Creating player
playerShip = Ship(width / 2, height - 100, 8, 5, 0, 500, "Sprites/player.png")
player_sprite.add(playerShip)

# Creating powerup
fast = Power(random.randint(10, width - 20), random.randint(-100, -50))
power_up.add(fast)

# Creating obstacles
for i in range(1, 20):
    meteorite = Obstacle(random.randint(10, width - 20), random.randint(-5000, -50))
    obstacle.add(meteorite)


# Game logic
def game_start():

    running = True
    while running:

        screen.blit(background, (0,0))

        clock.tick(fps)

        global countdown
        global last_count
        global power_up_time
        global next_count
        global next
        global end_timer
        global stop
        global power_cooldown
        game_state = None

        time_now = pygame.time.get_ticks()

        # Pressing escape while in a game closes window
        for event in pygame.event.get():   # for loop to check for a event trigger from pygames
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:     #Pressing escape key will quit the game
                    running = False

        # Everything begins to move
        if countdown == 0:
            if time_now - last_enemy_shot > enemy_cooldown and len(all_enemies_lasers) < 5 and len(all_enemies) > 0:
                attacking_enemy = random.choice(all_enemies.sprites())
                enemy_laser = Enemy_Laser(attacking_enemy.rect.centerx, attacking_enemy.rect.bottom)
                all_enemies_lasers.add(enemy_laser)


            game_state = playerShip.update()
            all_lasers.update()
            all_enemies.update()
            all_enemies_lasers.update()
            power_up.update()
            obstacle.update()
            rock.update()

            # How long the power up lasts
            if power_up_time == 0:
                playerShip.cooldown = 500
            if power_up_time > 0:
                if time_now - power_cooldown > 700:
                    playerShip.cooldown = 0
                    power_up_time -= 1
                    power_cooldown = time_now

            # Following rock in lasers
            if len(all_enemies) == 0 and len(rock) == 0 and stop == 0:
                block = Rock(width + 40, 500)
                rock.add(block)
            elif len(rock) == 1 and block.rect.left > 200 and stop == 0:
                obstacle.empty()
                if time_now - end_timer > 200:
                    for row in range(1):
                        for item in range(40):
                            #Enemy(buffer to the left + pixels apart, buffer at the top + pixels apart)
                            laser = Enemy_Laser((10 + item * 20), (2 + row * 50))
                            all_enemies_lasers.add(laser)
                            end_timer = time_now
                if block.rect.left < 203:
                    stop += 1

            # Displaying complete after finishing level as well as moving to next level
            if stop == 1:
                if next > 0:
                    if time_now - next_count > 1000:
                        next -= 1
                        next_count = time_now
                if next in range(1, 5):
                    draw_text(width, 450, "Complete!", font, WHITE)
                    playerShip.speed = 0
                    playerShip.rect.top -= 5
                if next == 0:
                    countdown = 4
                    return GameState.SECOND

        # Countdown timer for start of game
        if countdown > 0:
            draw_text(width, 450, "READY!", font, WHITE)
            draw_text(width, 490, str(countdown), font, WHITE)
            if time_now - last_count > 1500:
                countdown -= 1
                last_count = time_now

        player_sprite.draw(screen)
        all_lasers.draw(screen)
        all_enemies.draw(screen)
        all_enemies_lasers.draw(screen)
        power_up.draw(screen)
        obstacle.draw(screen)
        rock.draw(screen)

        show_score()    # Displays health and score
        pygame.display.update()  # update our screen

        for event in pygame.event.get():   # for loop to check for a event trigger from pygames
            if event.type == pygame.QUIT:  # once the quit event presents itself by clicking the exit button it changes the value of running
                running = False            # running will equal false which will terminate our program

        if game_state == GameState.DEAD:
            return GameState.DEAD


    return GameState.QUIT

# Game state machine class
class GameState(Enum):
    QUIT = -1
    TITLE = 0
    NEWGAME = 1
    SECOND = 2
    DEAD = 3


if __name__ == "__main__":
    main()
