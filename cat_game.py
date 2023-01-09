import random
import os
from os import path
import pygame
from pygame.locals import *
import pickle
import json

pygame.init()

WIDTH, HEIGHT = 1000, 1000

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Cat game')

#different variables
tile_size = 50
game_over = 0
main_menu = True
level = 0
max_levels = 5

#colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
PURPLE = (255, 0, 255)

#music
#setting up the current path for music file
current_path = os.path.dirname(__file__)
assets_path = os.path.join(current_path)

#turning on music for unlimited playing
pygame.mixer.music.load(os.path.join(assets_path, 'theme_music.wav'))
pygame.mixer.music.play(-1)

#load images
bk = pygame.image.load('cat_game/background.png')
bk_s = pygame.transform.scale(bk, (1000, 1000))
restart  = pygame.image.load('cat_game/restart.png')
restart_img = pygame.transform.scale(restart, (400, 400))
start = pygame.image.load('cat_game/start.png')
start_img = pygame.transform.scale(start, (400, 400))
exit1 = pygame.image.load('cat_game/outof.png')
exit_img = pygame.transform.scale(exit1, (400, 400))

#dividing the screen to the grid to see how it looks like
#def draw_grid():
 #   for line in range(0, 6):
  #      pygame.draw.line(screen, (WHITE), (0, line * tile_size), (WIDTH, line * tile_size))
   #     pygame.draw.line(screen, (WHITE), (line * tile_size, 0), (line * tile_size, HEIGHT))
#reset level function
def reset_level(level):
    player.reset(100, HEIGHT - 130)
    rat_group.empty()
    pond_group.empty()
    exit_group.empty()

    if path.exists(f'cat_game/level{level}_data'):
            level_file = open(f'cat_game/level{level}_data', 'rb')
            world_data = pickle.load(level_file)
    world = World(world_data)

    return world

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False
    
    def draw(self):
        action = False
        #get mouse position
        pos = pygame.mouse.get_pos()

        #checking mouse is over and clicked condition
        if self.rect.collidepoint(pos):
            #print('no mouse') #checking
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

        #drawing function button
        screen.blit(self.image, self.rect)

        return action


class Player():
    #global game_over
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, game_over):
        dx = 0
        dy = 0
        walk_cooldown = 5

        if game_over == 0:
            #get key pressed
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped == False and self.in_jump == False:
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
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]


            #handling animation
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]


            #adding gravity - acceleration
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y
            #calculate new player position
            #check collision at new position
            self.in_jump = True
            for tile in world.tile_list:
                #checking for collision in x axis
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                #checking for collision in y direction
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #check if below the ground, like jumping
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    #checking if above the ground, liek falling
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_jump = False
            #checking for collision with enemes
            if pygame.sprite.spritecollide(self, rat_group, False):
                game_over = -1
                #cjecking for collisions with water
            if pygame.sprite.spritecollide(self, pond_group, False):
                game_over = -1
                #print(game_over) #checking
            #checking for collision with exit
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1

            #adjust player position
            #update player coordinate
            self.rect.x += dx
            self.rect.y += dy
        elif game_over == -1:
            self.image = self.dead_img
            if self.rect.y > 200:
                self.rect.y  -= 5
            #if self.rect.bottom > HEIGHT:
             #   self.rect.bottom = HEIGHT

        #draw player in the screen
        screen.blit(self.image, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

        return game_over

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 3):
            img_left = pygame.image.load(f'cat_game/cat{num}.png')
            img_left = pygame.transform.scale(img_left, (80, 80))
            img_right = pygame.transform.flip(img_left, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        dead = pygame.image.load('cat_game/cat_scared.png')
        self.dead_img = pygame.transform.scale(dead, (80, 80))
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_y = 0
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.jumped = False
        self.direction = 0
        self.in_jump = True

class World():
    def __init__(self, data):
        self.tile_list = []

        #load images
        cloud_img = pygame.image.load('cat_game/cloud1.png')
        cloud_img2 = pygame.image.load('cat_game/cloud2.png')

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile ==1:
                    img = pygame.transform.scale(cloud_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile ==2:
                    img = pygame.transform.scale(cloud_img2, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    rat = Enemy(col_count * tile_size, row_count * tile_size+15)
                    rat_group.add(rat)
                if tile == 6:
                    pond = Falling(col_count * tile_size, row_count * tile_size + (tile_size // 2))
                    pond_group.add(pond)
                if tile == 8:
                    exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
                    exit_group.add(exit)
                col_count += 1
            row_count += 1

    def draw(self):
        #gong through the grid to put what we want in the exact grid
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            #checking how the layer looks like
            #pygame.draw.rect(screen, (WHITE), tile[1], 2)

#enemy class is a child of a sprite class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img_rat = pygame.image.load('cat_game/mouse.png')
        self.image = pygame.transform.scale(img_rat, (70, 70))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    #making new update class for enemies moving leftf and right in the same point
    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 30:
            self.move_direction *= -1
            self.move_counter *= -1


class Falling(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('cat_game/water1.png')
        self.image = pygame.transform.scale(img, (100, tile_size //2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('cat_game/exit.png')
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

#load levels and create the world

leveldatafile = f'cat_game/level{level}_data'
if path.exists(leveldatafile):
    pickle_in = open(f'cat_game/level{level}_data', 'rb')
    world_data = pickle.load(pickle_in)
#world = World(world_data)
#


player = Player(100, HEIGHT - 130)

rat_group = pygame.sprite.Group()
pond_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
world = World(world_data)

#creating buttons
restart_button = Button(WIDTH // 2 - 200, HEIGHT //2 - 200, restart_img)
start_button = Button(WIDTH // 2 - 170, HEIGHT // 2 - 250, start_img)
exit_button = Button(WIDTH // 2 + 110, HEIGHT // 2 + 120, exit_img)

speed = 60
clock = pygame.time.Clock()
run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        #if event.type == pygame.MOUSEBUTTONDOWN: #checking later if smth was done in the screen
            #pygame.quit()
    #background
    #screen.fill(BLACK)
    screen.blit(bk_s, (0,0))

    if main_menu == True:
        if exit_button.draw() == True:
            run = False
        if start_button.draw() == True:
            main_menu = False
    else:
        world.draw()

        if game_over == 0:
            rat_group.update()


        rat_group.draw(screen)
        pond_group.draw(screen)
        exit_group.draw(screen)
        
        #constant loop
        game_over = player.update(game_over)

        #if player dies
        if game_over == -1:
            if restart_button.draw():
                world_data = []
                world = reset_level(level)
                game_over = 0
        #if player has completed the level
        if game_over == 1:
            #reset the game and go to the next level
            level += 1
            if level <= max_levels:
                #reset level
                world_data = []
                world = reset_level(level)
                game_over = 0
            else:
                #restart the game
                if restart_button.draw():
                    level = 1
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
        #print(world.tile_list)

        #finishing the loop 
    pygame.display.update()
        #pygame.display.flip()
    clock.tick(speed)
pygame.quit()

#if __name__ == "__main__":
 #   main()

