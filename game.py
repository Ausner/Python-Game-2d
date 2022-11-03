# from distutils import dir_util
import pygame
from pygame.locals import *
#from pyvidplayer import Video
from pygame import gfxdraw
from random import randint
from levels.levels import Levels

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 1500
screen_height = 900


screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Platformer')


#vid = Video('Tic Tac Toe Video.mp4')
#vid.set_size((screen_width, screen_height))


# def intro():
#     while True:
#         vid.draw(screen, (0, 0))
#         pygame.display.update()
#         for event in pygame.event.get():
#             if event.type == pygame.MOUSEBUTTONDOWN:
#                 vid.close()
#                 main()

#define game variables
title_size = 43
game_over = 0
main_menu = True

#load images
sun_img = pygame.image.load('img/sun.png')
bg_img = pygame.image.load('img/sky.png').convert_alpha()
restart_img = pygame.image.load('img/restart.jpg')
start_img = pygame.image.load('img/start.png')
exit_img = pygame.image.load('img/exit.png')

class World():
    def __init__(self, data):
        self.tile_list = []

        #load images
        block_img = pygame.image.load('img/block.png')
        grass_img = pygame.image.load('img/grass.png')
        grass3_img = pygame.image.load('img/grass.png')

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if data[row_count][col_count] == 1:
                    img = pygame.transform.scale(block_img, (title_size, title_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * title_size
                    img_rect.y = row_count * title_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if data[row_count][col_count] == 2:
                    img = pygame.transform.scale(grass_img, (title_size, title_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * title_size
                    img_rect.y = row_count * title_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if data[row_count][col_count] == 3:
                    enemy = Enemy(col_count * title_size, row_count * title_size - 40) # you can plus the place
                    enemies.add(enemy)
                if data[row_count][col_count] == 6:
                    lava = Lava(col_count * title_size, row_count * title_size + (title_size // 2))
                    lava_group.add(lava)
                col_count += 1
            row_count += 1
    
    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            #pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)


class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False
        #mouse position
        pos = pygame.mouse.get_pos()

        #check mouserover and clicks
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False: #left click
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        #draw button
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
            #get keypresess
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
                self.vel_y = -15
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
            


            #handle animation:
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_rigth):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_rigth[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]   
            
            #add gravity
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            #check for collision
            self.in_air = True
            for tile in world.tile_list:
                #check for collision in x directio
                if tile[1].colliderect(self.rect.x +dx, self.rect.y, self.width, self.height):
                    dx = 0

                #check for collision in y direction
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #check if below the ground... jumping
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    #check if above the ground... falling
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False

            #check for collision with enemies
            if pygame.sprite.spritecollide(self, enemies, False):
                game_over = -1

            #check for collision with lava
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1




            #update the player coordinates
            self.rect.x += dx
            self.rect.y += dy


        elif game_over == -1:
            self.image = self.dead_img
            if self.rect.y >= 200:
                self.rect.y -= 5

        #draw player onto screen
        screen.blit(self.image, self.rect)
        #pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        return game_over
    
    def reset(self, x, y):
        self.images_rigth = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 12):
            img_rigth = pygame.image.load(f'img/player{num}.png')
            img_rigth = pygame.transform.scale(img_rigth, (70, 100))
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
        self.image = pygame.transform.scale(image, (title_size, title_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y




player = Player(100, screen_height - 130)
enemies = pygame.sprite.Group()
lava_group = pygame.sprite.Group()

#get the level and create the world
world_data = Levels.level1
world = World(world_data)

#buttons
restar_button = Button(screen_width // 2 - 300, screen_height // 2 -300, restart_img)
start_button = Button(screen_width // 2  -350, screen_height // 2 - 100, start_img)
exit_button = Button(screen_width // 2  + 150, screen_height // 2 - 100, exit_img)


def main():

    game_over = 0
    main_menu = True
    run = True

    while run  == True:
        clock.tick(fps)

        screen.blit(bg_img, (0, 0))
        screen.blit(sun_img, (100, 100))


        #show main menu
        if main_menu:
            if exit_button.draw():
                run = False
            if start_button.draw():
                main_menu = False

        else:
            world.draw()

            if game_over == 0:
                enemies.update()
            enemies.draw(screen)
            
            lava_group.draw(screen)
            game_over = player.update(game_over)

            #if died
            if game_over == -1:
                if restar_button.draw():
                    player.reset(100, screen_height - 130)
                    game_over = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            pygame.display.update()
    pygame.quit()

main()
# intro()