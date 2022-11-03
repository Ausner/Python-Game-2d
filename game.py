import pygame
from pygame.locals import *
from pygame import gfxdraw
from random import randint
from levels.levels import Levels
from pygame import mixer

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 1500
screen_height = 900


screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Game')

#define font
font_score = pygame.font.SysFont('Bauhaus 93', 30)
font = pygame.font.SysFont('Bahaus 93', 70)
font_big = pygame.font.SysFont('Bahaus 93', 80)

# define game variables
title_size = 43
game_over = 0
main_menu = True
level = 1
max_levels = 2
score = 0

#define colours
white = (255, 255, 255)
black = (0, 0, 0)
blue = (0, 0, 255)

# load images
sun_img = pygame.image.load('img/sun.png')
menu_img = pygame.image.load('img/menu_img.png').convert_alpha()
bg_img = pygame.image.load('img/sky.png').convert_alpha()
restart_img = pygame.image.load('img/restart.jpg')
start_img = pygame.image.load('img/start.png')
exit_img = pygame.image.load('img/exit.png')
play_again_img = pygame.image.load('img/play_again.png')
home_img = pygame.image.load('img/home.png')

#load sound
pygame.mixer.music.load('sounds/levels_music.mp3')
pygame.mixer.music.play(-1, 0.0, 5000)
coin_fx =pygame.mixer.Sound('sounds/coin.mp3')
coin_fx.set_volume(0.5)
jump_fx =pygame.mixer.Sound('sounds/jump.mp3')
jump_fx.set_volume(0.5)
die_fx =pygame.mixer.Sound('sounds/hit.mp3')
die_fx.set_volume(0.5)


#draw_score and some messages 
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x + 10, y))


# reset level
def reset_level(level):
    player.reset(100, screen_height - 130)
    enemies.empty()
    lava_group.empty()
    door_group.empty()
    # get the level and create the world
    world_data = Levels.game_levels[level]
    world = World(world_data)
    return world


class World():
    def __init__(self, data):
        self.tile_list = []

        # load images
        block_img = pygame.image.load('img/block.png')
        grass_img = pygame.image.load('img/grass.png')
        grass3_img = pygame.image.load('img/grass.png')

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if data[row_count][col_count] == 1:
                    img = pygame.transform.scale(
                        block_img, (title_size, title_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * title_size
                    img_rect.y = row_count * title_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if data[row_count][col_count] == 2:
                    img = pygame.transform.scale(
                        grass_img, (title_size, title_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * title_size
                    img_rect.y = row_count * title_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if data[row_count][col_count] == 3:
                    enemy = Enemy(col_count * title_size,
                                  row_count * title_size - 25)
                    enemies.add(enemy)
                if data[row_count][col_count] == 6:
                    lava = Lava(col_count * title_size, row_count *
                                title_size + (title_size // 2))
                    lava_group.add(lava)
                if data[row_count][col_count] == 7:
                    coin = Coin(col_count * title_size + (title_size // 2), row_count *
                                title_size + (title_size // 2))
                    coin_group.add(coin)
                if data[row_count][col_count] == 8:
                    door = Door(col_count * title_size, row_count *
                                title_size - (title_size // 2))
                    door_group.add(door)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            # pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)


class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False
        # mouse position
        pos = pygame.mouse.get_pos()

        # check mouserover and clicks
        if self.rect.collidepoint(pos):
            # left click
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # draw button
        screen.blit(self.image, self.rect)
        return action


class Player():
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, game_over):
        dx = 0
        dy = 0
        walk_cooldown = 2

        if game_over == 0:
            # get keypresess
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
                jump_fx.play()
                self.vel_y = -17
                self.jumped = True

            if key[pygame.K_SPACE] == False:
                self.jumped = False

            if key[pygame.K_LEFT]:
                dx -= 5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += 5
                self.counter += 1
                self.direction = 1
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_rigth[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # handle animation:
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_rigth):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_rigth[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # add gravity
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            # check for collision
            self.in_air = True
            for tile in world.tile_list:
                # check for collision in x directio
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0

                # check for collision in y direction
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # check if below the ground... jumping
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    # check if above the ground... falling
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False

            # check for collision with enemies
            if pygame.sprite.spritecollide(self, enemies, False):
                game_over = -1
                die_fx.play()

            # check for collision with lava
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1
                die_fx.play()

            # check for collision with door
            if pygame.sprite.spritecollide(self, door_group, False):
                game_over = 1



            # update the player coordinates
            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1:
            self.image = self.dead_img
            if self.rect.y > 200:
                self.rect.y -= 5

        # draw player onto screen
        screen.blit(self.image, self.rect)
        # pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        return game_over

    def reset(self, x, y):
        self.images_rigth = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 12):
            img_rigth = pygame.image.load(f'img/player{num}.png')
            img_rigth = pygame.transform.scale(img_rigth, (50, 80)) #70, 100
            img_left = pygame.transform.flip(img_rigth, True, False)
            self.images_rigth.append(img_rigth)
            self.images_left.append(img_left)
        self.dead_img = pygame.image.load('img/ghost.png')
        self.image = self.images_rigth[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/enemy1.png')
        self.image = pygame.transform.scale(self.image, (60, 80)) #70, 100

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 115:
            self.move_direction *= -1
            self.move_counter *= -1


class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        image = pygame.image.load('img/lava.png')
        self.image = pygame.transform.scale(
            image, (title_size, title_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        image = pygame.image.load('img/brain.png')
        self.image = pygame.transform.scale(
            image, (title_size, title_size))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y) #middle of the coin

class Door(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        image = pygame.image.load('img/door.png')
        self.image = pygame.transform.scale(
            image, (title_size, title_size * 1.5))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


player = Player(100, screen_height - 130)
enemies = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
door_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()

#dummy coin for score
score_coin = Coin(title_size //2, title_size //2)
coin_group.add(score_coin)

# get the level and create the world
world_data = Levels.game_levels[level]
world = World(world_data)

# buttons
restar_button = Button(screen_width // 2 - 300,
                       screen_height // 2 - 300, restart_img)
start_button = Button(screen_width // 2 - 360,
                      screen_height // 2 + 130, start_img)
exit_button = Button(screen_width // 2 + 160,
                     screen_height // 2 + 130, exit_img)
play_again_button = Button(screen_width // 2 -10 ,
                       screen_height // 2 + 50, play_again_img)

home_button = Button(screen_width // 2 -90 ,
                       screen_height // 2 + 50, home_img)



# def main():

# game_over = 0
# main_menu = True
run = True
 # get the level and create the world
#  world_data = Levels.game_levels[level]
#   world = World(world_data)

while run == True:
    clock.tick(fps)

    screen.blit(menu_img, (0, 0))

    # show main menu
    if main_menu:
        if exit_button.draw():
            run = False
        if start_button.draw():
            main_menu = False

    else:
        screen.blit(bg_img, (0, 0))
        screen.blit(sun_img, (100, 100))

        world.draw()

        if game_over == 0:
            enemies.update()
            #update score
            if pygame.sprite.spritecollide(player, coin_group, True):
                coin_fx.play()
                score += 1
            draw_text('X '+str(score), font_score, black, title_size -10, 10)

        enemies.draw(screen)

        lava_group.draw(screen)
        door_group.draw(screen)
        coin_group.draw(screen)
        game_over = player.update(game_over)

        # if died
        if game_over == -1:
            if restar_button.draw():
                world_data = []
                world = reset_level(level)
                game_over = 0
                score = 0

        # if win
        if game_over == 1:
        # reset the game and go to next level
            level += 1
            if level <= max_levels:
                # reset level
                world_data = []
                world = reset_level(level)
                game_over = 0
            else:
                draw_text('You Win!!!', font, blue, (screen_width // 2) - 140, screen_height // 2)
                if play_again_button.draw():
                    level = 1
                    # reset level
                    world_data = []
                    world = reset_level(level)
                    main_menu = True
                    game_over = 0
                    score = 0
                if home_button.draw():
                    level = 1
                    # go to main menu
                    world_data = []
                    main_menu = True
                    game_over = 0
                    score = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()
pygame.quit()

# main()
# intro()