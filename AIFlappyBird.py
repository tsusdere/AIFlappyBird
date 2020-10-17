#----------------------------------------------------------------------------------
#AIFlappyBird.py written by Fabian Aguilar Gomez, Roan Dominguez,
#                           Noor Alaskari, Ivan Rivera, Jose Carlos Gomez-Vazquez
#Purpose:
#   The purpose of this program is to train Flappy Bird to beat the game using
#   NeuroEvolution of Augmenting Topologies (NEAT) genetic algorithm with
#   neural networks to train the bird to beat the game.
#Notes:
#   - Used YouTube tutorials and GitHub repos to accomplish the task
#   - The game is created as an Object Oriented Program
#----------------------------------------------------------------------------------

#import modules
import pygame
import neat
import time
import os
import random

#Constants for the window
WIDTH = 500
HEIGHT = 800

'''
Load the images to 
create the bird and
enviroment
'''
#bird images to create animation
BIRDS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird1.png"))),
         pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird2.png"))),
         pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird3.png")))]

#Load pipe image
PIPE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")))

#Load Base of the game
BASE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")))

#Load the background of the game
BACKGROUND = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bg.png")))

#Bird object
class Bird:
    #Attributes of the bird
    IMGS = BIRDS
    MAX_ROT = 25
    ROT_VEl = 20
    ANI_TIME = 5

    #Constructor
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    #Jump setting for the bird
    #to jump
    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    #Function to move the
    #bird each tick
    def move(self):
        self.tick_count += 1

        #Using the current velocity of the bird
        #determine how much we are moving forward
        d = self.vel*self.tick_count+1.5*self.tick_count**2

        #Point to stop accelerating
        if d >= 16:
            d = 16

        #If the bird keeps going up
        #keep going up
        if d < 0:
            d -= 2
        self.y += d

        #Tilt the bird up
        if d < 0 or self.y < self.height + 50:
            #If bird goes over max rotation
            if self.tilt < self.MAX_ROT:
                self.tilt = self.MAX_ROT
        #Make the bird tilt down when we are
        #falling
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEl

    #draw the bird & keep track of ticks
    def draw(self,win):
        #Keep track of the ticks
        self.img_count += 1

        #Create the bird animation using
        #the array of picures
        if self.img_count < self.ANI_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANI_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANI_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANI_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANI_TIME*4 +1:
            self.img = self.IMGS[0]
            self.img_count = 0

        #Animation if bird is going down
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANI_TIME*2

        #Rotate the image of the bird around the center
        rotated = pygame.transform.rotate(self.img,self.tilt)
        center = rotated.get_rect(center=self.img.get_rect(topleft=(self.x,self.y)).center)
        win.blit(rotated,center.topleft)

    #Colliders for the bird
    def mask(self):
        return pygame.mask.from_surface(self.img)

#Draw the window of the game
def draw_win(win,bird):
    win.blit(BACKGROUND,(0,0))
    bird.draw(win)
    pygame.display.update()

def main():
    #Create a bird and a window
    bird = Bird(200,200)
    win = pygame.display.set_mode((WIDTH,HEIGHT))

    #Set tick rate
    ticks = pygame.time.Clock()

    #Run the game until we press the "X" on the window
    run = True
    while run:
        ticks.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        bird.move()
        draw_win(win,bird)
    pygame.quit()
    quit()

#TODO:Code the Pipes to spawn

main()
