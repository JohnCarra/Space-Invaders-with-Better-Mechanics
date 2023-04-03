import pygame
import pygame.freetype
from pygame.sprite import Sprite
from pygame.rect import Rect
from enum import Enum
from pygame.sprite import RenderUpdates
import random
import os

pygame.init()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 191, 255)

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

# For stopping the spawning of lasers at the end of level one
stop = 0

# For stopping production of enemies after laser and rock part
stop_making = 0

# For moving to the second mechanic after big rock
move_on = 10

# Firerate of enemies
enemy_cooldown = 1000  # milliseconds?
last_enemy_shot = pygame.time.get_ticks()

# Freeze screen before a level begins moving to give player time
countdown = 6
last_count = pygame.time.get_ticks()

# How long the power up lasts
power_up_time = 0
power_cooldown = pygame.time.get_ticks()

# Timer for when to change to next level when previous level is completed
next = 10
next_count = pygame.time.get_ticks()

# Timer for when end of level laser barrage
end_timer = pygame.time.get_ticks()

# Timer for when end of second laser barrage
ender_timer = pygame.time.get_ticks()

# Background image for title
mainscreen = pygame.image.load('Sprites/mainscreen2.png')
mainscreen = pygame.transform.scale(mainscreen, (width, height))

# Background image for level one
background = pygame.image.load('Sprites/background.png')
background = pygame.transform.scale(background, (width, height))

# Level two image
background_two = pygame.image.load('Sprites/background2.png')
background_two = pygame.transform.scale(background_two, (width, height))

# Dead screen image
dead_background = pygame.image.load('Sprites/deadscreen.png')
dead_background = pygame.transform.scale(dead_background, (width, height))

# Shrug image
shrug = pygame.image.load('Sprites/shrug.png')
shrug = pygame.transform.scale(shrug, (100, 50))

# Caption and Icon
# Set the title to space invadors on the window
pygame.display.set_caption("Space Invaders")
icon = pygame.image.load('ufo.png')
pygame.display.set_icon(icon)

# Used to capture the name of player at death screen
user_text = ''

# Highscore text file that is written to, to save highscores
highscore_file = 'highscores.txt'


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


# Player class
class Ship(pygame.sprite.Sprite):
    """ Stores information about a ship """

    def __init__(self, x, y, speed, health, score, cooldown, picture):

        super().__init__()

        self.reset(x, y, speed, health, score, cooldown, picture)

    def update(self):

        # cooldown = 500 # milliseconds
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
            return GameState.NAME

    def reset(self, x, y, speed, health, score, cooldown, picture):
        self.speed = speed
        self.health = health
        self.score = score
        self.cooldown = cooldown

        # Draw the ship
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

        # Draw the enemy
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

        if self.rect.top > height:
            playerShip.health -= 1
            self.kill()

        if pygame.sprite.spritecollide(self, player_sprite, False, pygame.sprite.collide_mask):
            self.kill()
            playerShip.health -= 1


# Enemy that stays stills class
class Enemy_Still(pygame.sprite.Sprite):
    def __init__(self, x, y):

        super().__init__()

        # Draw the enemy
        self.image = pygame.image.load("Sprites/enemy.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (32, 32))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]


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

        self.rect.y += 20
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
    def __init__(self, x, y, speed):

        super().__init__()

        self.speed = speed

        self.image = pygame.image.load("Sprites/meteorite.png").convert_alpha()

        self.image = pygame.transform.scale(self.image, (64, 64))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):

        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()
        if pygame.sprite.spritecollide(self, player_sprite, True):
            playerShip.health -= playerShip.health
            self.kill()


# Returns surface with text written on
def create_surface_with_text(text, font_size, text_rgb):
    font = pygame.freetype.SysFont("Courier", font_size, bold=True)
    surface, _ = font.render(text=text, fgcolor=text_rgb)
    return surface.convert_alpha()


# Puts text onto screen
def draw_text(x, y, text, font_size, text_rgb):
    font = pygame.font.SysFont('freesansbold.ttf', font_size)
    img = font.render(text, True, text_rgb)
    text_rect = img.get_rect(center=(x / 2, y))
    screen.blit(img, text_rect)


# Game state machine, helps transition to different screens
def main():
    game_state = GameState.TITLE

    while True:
        if game_state == GameState.TITLE:
            game_state = title_screen(screen)

        if game_state == GameState.NEWGAME:
            game_state = game_start()

        if game_state == GameState.HIGHSCORE:
            game_state = highscore(highscore_file)

        if game_state == GameState.PAUSE:
            game_state = game_pause()

        if game_state == GameState.DEAD:
            game_state = game_over()

        if game_state == GameState.NAME:
            game_state = getting_name()

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

        screen.blit(mainscreen, (0, 0))

        mouse_up = False
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_up = True
            if event.type == pygame.QUIT:
                return GameState.QUIT

        for button in buttons:
            ui_action = button.update(pygame.mouse.get_pos(), mouse_up)
            if ui_action is not None:
                return ui_action

        buttons.draw(screen)
        pygame.display.flip()


# Title screen
def title_screen(screen):

    title = UIPlain(
        center_position=(400, 50),
        font_size=70,
        text_rgb=BLUE,
        text="Space Invaders",
    )

    title_2 = UIPlain(
        center_position=(400, 120),
        font_size=70,
        text_rgb=BLUE,
        text="with",
    )

    title_3 = UIPlain(
        center_position=(400, 200),
        font_size=70,
        text_rgb=BLUE,
        text="Better Mechanics",
    )

    title_4 = UIPlain(
        center_position=(405, 55),
        font_size=70,
        text_rgb=WHITE,
        text="Space Invaders",
    )

    title_5 = UIPlain(
        center_position=(405, 125),
        font_size=70,
        text_rgb=WHITE,
        text="with",
    )

    title_6 = UIPlain(
        center_position=(405, 205),
        font_size=70,
        text_rgb=WHITE,
        text="Better Mechanics",
    )

    start_btn = UIElement(
        center_position=(400, 500),
        font_size=30,
        text_rgb=WHITE,
        text="Start",
        action=GameState.NEWGAME,
    )

    score_btn = UIElement(
        center_position=(400, 600),
        font_size=30,
        text_rgb=WHITE,
        text="Highscores",
        action=GameState.HIGHSCORE,
    )

    quit_btn = UIElement(
        center_position=(400, 700),
        font_size=30,
        text_rgb=WHITE,
        text="Quit",
        action=GameState.QUIT,
    )

    buttons = RenderUpdates(start_btn, score_btn, quit_btn,
                            title, title_2, title_3, title_4, title_5, title_6)

    return game_loop(screen, buttons)


# Displays your current score and health during the duration of the game
def show_score():
    font = pygame.font.SysFont('freesansbold.ttf', 37)
    score = font.render("Score : " + str(playerShip.score), True, WHITE)
    screen.blit(score, (1, 775))
    health = font.render("Health : " + str(playerShip.health), True, WHITE)
    screen.blit(health, (681, 775))


# Dsplaying all saved highscores on highscore screen
def highscore(file_name):

    scores = get_highscore(file_name)

    title = UIPlain(
        center_position=(400, 200),
        font_size=50,
        text_rgb=WHITE,
        text="Highscores",
    )

    first = UIPlain(
        center_position=(400, 300),
        font_size=30,
        text_rgb=WHITE,
        text='1st: ' + scores.get('high')[0] + ' - ' + scores.get('high')[1],
    )

    second = UIPlain(
        center_position=(400, 350),
        font_size=30,
        text_rgb=WHITE,
        text='2nd: ' + scores.get('mid')[0] + ' - ' + scores.get('mid')[1],
    )

    third = UIPlain(
        center_position=(400, 400),
        font_size=30,
        text_rgb=WHITE,
        text='3rd: ' + scores.get('low')[0] + ' - ' + scores.get('low')[1],
    )

    menu_btn = UIElement(
        center_position=(130, 750),
        font_size=30,
        text_rgb=WHITE,
        text="Main Menu",
        action=GameState.TITLE,
    )

    buttons = RenderUpdates(menu_btn, title, first, second, third)

    return game_loop(screen, buttons)


def get_highscore(file_name):
    text = ''

    if os.path.isfile(file_name):
        with open(file_name, 'r') as text_file:
            text = text_file.read()
    else:
        f = open(file_name, 'w')
        text = 'high:Empty:0,mid:Empty:0,low:Empty:0,lowest:Empty:0'
        f.write(text)
        f.close()

    text_list = text.split(',')

    to_return = {}

    for element in text_list:
        i = element.split(':')
        to_return[i[0]] = [i[1], i[2]]

    return to_return


def write_highscore(file_name, score):
    f = open(file_name, 'w')
    to_write = ''
    for name in ('high', 'mid', 'low', 'lowest'):
        to_write += name
        to_write += ':'
        to_write += str(score.get(name)[0])
        to_write += ':'
        to_write += str(score.get(name)[1])
        to_write += ','

    print(to_write)
    to_write = to_write.rstrip(to_write[-1])
    f.write(to_write)
    f.close()


def set_highscore(file_name, player_name, score):
    scores = get_highscore(file_name)

    old_high = scores.get('high')[0]
    old_mid = scores.get('mid')[0]
    old_low = scores.get('low')[0]
    old_highscore = scores.get('high')[1]
    old_midscore = scores.get('mid')[1]
    old_lowscore = scores.get('low')[1]

    if (int(score) >= int(scores.get('high')[1])):
        print('in1')
        scores['high'][0] = player_name
        scores['high'][1] = score
        scores['mid'][0] = old_high
        scores['mid'][1] = old_highscore
        scores['low'][0] = old_mid
        scores['low'][1] = old_midscore
    elif (int(score) >= int(scores.get('mid')[1])):
        print('in2')
        scores['mid'][0] = player_name
        scores['mid'][1] = score
        scores['low'][0] = old_mid
        scores['low'][1] = old_midscore
    elif (int(score) >= int(scores.get('low')[1])):
        print('in3')
        scores['low'][0] = player_name
        scores['low'][1] = score
        scores['lowest'][0] = old_low
        scores['lowest'][1] = old_lowscore

    write_highscore(file_name, scores)
    print(scores)


# Pausing the game
def game_pause():

    paused = True
    while paused:

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                paused = False
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        screen.fill(BLACK)
        draw_text(width, 400, "PAUSED", 37, WHITE)

        pygame.display.update()
        clock.tick(fps)


# Getting name of player after death
def getting_name():
    global user_text
    global highscore_file
    font = pygame.font.SysFont('freesansbold.ttf', 37)
    input_rect = pygame.Rect(365, 745, 58, 35)

    running = True
    while running:

        screen.blit(dead_background, (0, 0))

        # Getting user input for name
        for event in pygame.event.get():   # for loop to check for a event trigger from pygames
            if event.type == pygame.QUIT:
                return GameState.QUIT
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                else:
                    user_text += event.unicode
                if len(user_text) >= 4:
                    user_text = user_text[:-1]
                if event.key == pygame.K_RETURN:
                    set_highscore(highscore_file, user_text, playerShip.score)
                    return GameState.DEAD

        # Displaying what the user types in
        pygame.draw.rect(screen, WHITE, input_rect, 2)
        text = font.render(user_text, True, WHITE)
        screen.blit(text, (input_rect.x + 5, input_rect.y + 5))

        # Box around the user input moves with the input
        input_rect.w = max(10, text.get_width() + 10)

        pygame.display.update()  # update our screen
        clock.tick(fps)


# Game over screen
def game_over():
    game_over = UIPlain(
        center_position=(400, 200),
        font_size=70,
        text_rgb=WHITE,
        text="GAME OVER",
    )

    final_score = UIPlain(
        center_position=(400, 300),
        font_size=30,
        text_rgb=WHITE,
        text="Final Score : " + str(playerShip.score),
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

    playerShip.reset(width / 2, height - 100, 8, 5,
                     0, 500, "Sprites/player.png")
    player_sprite.add(playerShip)
    all_lasers.empty()
    all_enemies.empty()
    all_enemies_lasers.empty()
    obstacle.empty()
    rock.empty()
    power_up.empty()
    create_enemies()

    fast = Power(random.randint(10, width - 20), random.randint(-100, -50))
    power_up.add(fast)

    for i in range(1, 20):
        meteorite = Obstacle(random.randint(
            10, width - 20), random.randint(-5000, -50))
        obstacle.add(meteorite)

    global stop
    stop = 0

    global stop_making
    stop_making = 0

    global move_on
    move_on = 10

    global countdown
    countdown = 6

    global next
    next = 10

    global user_text
    user_text = ''

    buttons = RenderUpdates(retry_btn, menu_btn,
                            quit_btn, game_over, final_score)

    return game_loop(screen, buttons)


# Next Level
def second_level():
    playerShip.reset(width / 2, height - 100, 8, playerShip.health,
                     playerShip.score, 500, "Sprites/sub.png")
    running = True
    while running:

        screen.blit(background_two, (0, 0))

        draw_text(width, 400, "Buy the DLC for more content.", 37, WHITE)

        clock.tick(fps)

        global countdown
        global last_count

        game_state = None

        time_now = pygame.time.get_ticks()

        # Pressing escape while in a game closes window
        for event in pygame.event.get():   # for loop to check for a event trigger from pygames
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                game_pause()
            if event.type == pygame.QUIT:
                return GameState.QUIT

        if countdown > 0:
            if time_now - last_count > 2000:
                countdown -= 1
                last_count = time_now
            if countdown < 4:
                draw_text(width, 200, "THE GAME WILL NOW CLOSE IN " +
                          str(countdown), 52, WHITE)

        if countdown == 0:
            return GameState.QUIT

        game_state = playerShip.update()

        player_sprite.draw(screen)

        show_score()
        pygame.display.update()  # update our screen

        for event in pygame.event.get():   # for loop to check for a event trigger from pygames
            if event.type == pygame.QUIT:  # once the quit event presents itself by clicking the exit button it changes the value of running
                running = False            # running will equal false which will terminate our program

        if game_state == GameState.DEAD:
            return GameState.DEAD

    return GameState.QUIT


# Creating enemies
def create_enemies():
    for row in range(rows):
        for item in range(cols):
            # Enemy(buffer to the left + pixels apart, buffer at the top + pixels apart)
            enemy = Enemy((80 + item * 80), (50 + row * 100), 4)
            all_enemies.add(enemy)


# Initializing sprite lists
player_sprite = pygame.sprite.Group()
all_lasers = pygame.sprite.Group()
all_enemies = pygame.sprite.Group()
all_enemies_still = pygame.sprite.Group()
all_enemies_lasers = pygame.sprite.Group()
power_up = pygame.sprite.Group()
obstacle = pygame.sprite.Group()
rock = pygame.sprite.Group()

# Creating enemies
create_enemies()

# Creating player
playerShip = Ship(width / 2, height - 100, 8, 5, 0, 500, "Sprites/player.png")
player_sprite.add(playerShip)

# Creating powerup
fast = Power(random.randint(10, width - 20), random.randint(-100, -50))
power_up.add(fast)

# Creating obstacles
for i in range(1, 20):
    meteorite = Obstacle(random.randint(10, width - 20),
                         random.randint(-5000, -50))
    obstacle.add(meteorite)


# Game logic
def game_start():

    running = True
    while running:

        screen.blit(background, (0, 0))

        global countdown
        global last_count
        global power_up_time
        global next_count
        global next
        global move_on
        global end_timer
        global ender_timer
        global stop
        global stop_making
        global power_cooldown
        global enemy_cooldown
        game_state = None

        time_now = pygame.time.get_ticks()

        # Pressing escape while in a game pauses game
        for event in pygame.event.get():   # for loop to check for a event trigger from pygames
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                game_pause()
            if event.type == pygame.QUIT:
                return GameState.QUIT

        # Countdown timer to start level
        if countdown > 0:
            draw_text(width, 450, "READY!", 37, WHITE)
            if time_now - last_count > 1300:
                countdown -= 1
                last_count = time_now
            if countdown < 4:
                draw_text(width, 490, str(countdown), 37, WHITE)

        # Everything begins to move
        if countdown == 0:

            # Choosing which enemy will shoot at a set interval
            if time_now - last_enemy_shot > enemy_cooldown and len(all_enemies_lasers) < 5 and len(all_enemies) > 0:
                attacking_enemy = random.choice(all_enemies.sprites())
                enemy_laser = Enemy_Laser(
                    attacking_enemy.rect.centerx, attacking_enemy.rect.bottom)
                all_enemies_lasers.add(enemy_laser)

            # Updating movement of all sprites
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
                    playerShip.cooldown = 80
                    power_up_time -= 1
                    power_cooldown = time_now

            # Following rock in lasers
            if len(all_enemies) == 0 and len(rock) == 0 and stop == 0:
                block = Rock(width + 40, 500, 1.5)
                rock.add(block)
            elif len(rock) == 1 and block.rect.left > 200 and stop == 0:
                obstacle.empty()
                if time_now - end_timer > 200:
                    for row in range(1):
                        for item in range(40):
                            # Enemy(buffer to the left + pixels apart, buffer at the top + pixels apart)
                            laser = Enemy_Laser(
                                (10 + item * 20), (2 + row * 50))
                            all_enemies_lasers.add(laser)
                            end_timer = time_now
                if block.rect.left < 203:
                    stop += 1

            # Dodging lasers
            if stop == 1:
                if time_now - end_timer > 30:
                    if stop_making == 0:
                        for row in range(1):
                            for item in range(40):
                                # Enemy(buffer to the left + pixels apart, buffer at the top + pixels apart)
                                enemy = Enemy_Still(
                                    (10 + item * 20), (-20 + row * 50))
                                all_enemies_still.add(enemy)
                            stop_making = 1
                    if time_now - last_enemy_shot > enemy_cooldown and len(all_enemies_lasers) < 200:
                        attacking_enemy = random.choice(
                            all_enemies_still.sprites())
                        enemy_laser = Enemy_Laser(
                            attacking_enemy.rect.centerx, attacking_enemy.rect.bottom)
                        all_enemies_lasers.add(enemy_laser)
                        end_timer = time_now
                if move_on > 0:
                    if time_now - ender_timer > 2500:
                        move_on -= 1
                        ender_timer = time_now
                if move_on == 0:
                    all_enemies_still.empty()
                    stop += 1

            # Displaying complete after finishing level as well as moving to next level
            if stop == 2:
                if playerShip.score == 3600:
                    if next > 0:
                        if time_now - next_count > 1000:
                            next -= 1
                            next_count = time_now
                    if next in range(1, 5):
                        draw_text(width, 450, "Complete!", 37, WHITE)
                        playerShip.speed = 0
                        playerShip.rect.top -= 5
                    if next == 0:
                        countdown = 6
                        return GameState.SECOND
                else:
                    if next > 0:
                        if time_now - next_count > 1000:
                            next -= 1
                            next_count = time_now
                    if next in range(1, 5):
                        screen.blit(shrug, (350, 375))
                        draw_text(
                            width, 450, "Sorry, you don't get to pass!", 37, WHITE)
                        playerShip.speed = 0
                        playerShip.rect.top += 5
                    if next == 0:
                        return GameState.NAME

        # Draws all sprites onto screen
        player_sprite.draw(screen)
        all_lasers.draw(screen)
        all_enemies.draw(screen)
        all_enemies_lasers.draw(screen)
        power_up.draw(screen)
        obstacle.draw(screen)
        rock.draw(screen)

        # Displays health and score
        show_score()

        # Update our screen
        pygame.display.update()

        # Locks framerate to specified fps
        clock.tick(fps)

        # If health becomes 0, Ship class returns a game_state which this if statement uses to change screens
        if game_state == GameState.NAME:
            return GameState.NAME


# Game state machine class
class GameState(Enum):
    QUIT = -1
    TITLE = 0
    NEWGAME = 1
    SECOND = 2
    DEAD = 3
    NAME = 4
    PAUSE = 5
    HIGHSCORE = 6


if __name__ == "__main__":
    main()
