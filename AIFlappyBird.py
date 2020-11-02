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
import sys
import neat
import time
import os
import random
#initslazing the font 
pygame.font.init()

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

#font 
FONT = pygame.font.SysFont("comicsans", 50)


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
    
class Pipe():
    
    #represents a pipe object
 
    GAP = 200
    VEL = 5

    def __init__(self, x):
        
        #initialize pipe object
        
        self.x = x
        self.height = 0

        # where the top and bottom of the pipe is
        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(PIPE, False, True)
        self.PIPE_BOTTOM = PIPE

        self.passed = False

        self.set_height()

    def set_height(self):
        
        #set the height of the pipe, from the top of the screen

        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        #move pipe based on vel
        self.x -= self.VEL

    def draw(self, win):

        # draw both the top and bottom of the pipe
        # draw top
        win.blit(self.PIPE_TOP, (self.x, self.top))
        # draw bottom
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))


    def collide(self, bird):
 
        #returns if a point is colliding with the pipe
       
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask,top_offset)

        if b_point or t_point:
            return True

        return False

class Base:

    #Represnts the moving floor of the game
    VEL = 5
    WIDTH = BASE.get_width()
    IMG = BASE

    def __init__(self, y):

        #Initialize the object
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        #move floor so it looks like its scrolling
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        #Draw the floor. This is two images that move together.       
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))
        
        
#Draw the window of the game
def draw_win(win,bird,pipe,base,score):
    win.blit(BACKGROUND,(8,0))
    for pipes in pipe:
        pipes.draw(win)
       
    #rendering the font of the score    
    text = FONT.render("Score: "+ str(score), 1, (255,255,255))
    win.blit(text, (WIDTH - 10 - text.get_width(),20))
        
    base.draw(win)
        
    bird.draw(win)
    pygame.display.update()

def main(genomes, config):
    nets = []
    ge =[]
    birds = []

    for g in genomes:
        net = neat.nn.FeedForwardNetwork(g, config)
        nets.append(net)
        birds.append(Bird(230,350))
        g.fitness = g
        ge.append(g)

        

    #Create a bird and a window
    birds = []
    base = Base(730)
    pipes = [Pipe(700)]
    win = pygame.display.set_mode((WIDTH,HEIGHT))
    score =0
    #Set tick rate
    ticks = pygame.time.Clock()

    #Run the game until we press the "X" on the window
    run = True
    while run:
        ticks.tick(30)
        add_pipe = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        #bird.move()
        rem = []
        add_pipe = False
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)
                
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed =True
                    add_pipe =True
            
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            pipe.move()

        if add_pipe:
            score+=1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(700))
            
        for r in rem:
            pipes.remove(r)

        for x,bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)
             
        base.move()
        draw_win(win,bird,pipes,base, score)
    pygame.quit()
    sys.exit()

main()

def run(config_path):
    #Sets config parameters from configFile
    config = neat.config.Config(neat.DefaultGenome, 
                neat.DefaultReproduction, neat.DefaultSpeciesSet, 
                 neat.DefaultStagnation, config_path)
    #Set population
    pop = neat.Population(config)
    #Gives us stats
    pop.add_reporter(neat.StdOutReporter(True))
    #Get stats
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    winner = pop.run(main,50)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "configFile.txt")
    run(config_path)
