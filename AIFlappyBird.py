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
GEN =0

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
    def get_mask(self):
       return pygame.mask.from_surface(self.img)
    
class Pipe():
    GAP=200
    VEL=5 #Velocity of pipe

    def __init__(self,x): #No y because the height will be random
        self.x=x
        self.height=0
        self.gap=100
        self.top=0
        self.bottom=0
        self.PIPE_TOP=pygame.transform.flip(PIPE,False,True)
        self.PIPE_BOTTOM=PIPE
        self.passed=False
        self.set_height()
        

    def set_height(self): #Randomly define the top and bottom of the pipe
        self.height=random.randrange(50,450)
        self.top=self.height-self.PIPE_TOP.get_height()
        self.bottom=self.height+self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self,win):
        win.blit(self.PIPE_TOP,(self.x,self.top))
        win.blit(self.PIPE_BOTTOM,(self.x,self.bottom))

    def collide(self, bird, win):
        bird_mask=bird.get_mask()
        top_mask=pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask=pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))
        #Check collision of bird with top and bottom pipe
        b_point=bird_mask.overlap(bottom_mask,bottom_offset)
        t_point=bird_mask.overlap(top_mask,top_offset)

        if t_point or b_point:
            return True
        return False

class Base:
    VEL=5
    WIDTH=BASE.get_width()
    IMG=BASE

    def __init__(self,y): #No x becase it moves to the left
        self.y=y
        self.x1=0 #Start first image at 0
        self.x2=self.WIDTH #Start second image behind the first

    def move(self):
        self.x1 -= self.VEL #Image 1
        self.x2 -= self.VEL #Image 2

        #Cycle two images one after another if it goes off the screen
        if self.x1 + self.WIDTH < 0:
            self.x1=self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self,win):
        win.blit(self.IMG,(self.x1,self.y))
        win.blit(self.IMG,(self.x2,self.y))

def draw_win(win,birds,pipes,base,score , gen):
    win.blit(BACKGROUND, (0,0))

    for pipe in pipes:
        pipe.draw(win)

    text=FONT.render("Score: " + str(score),1,(255,255,255))
    win.blit(text,(WIDTH - 10 - text.get_width(),10))

    text=FONT.render("Gen: " + str(gen),1,(255,255,255))
    win.blit(text,( 10 ,10))

    base.draw(win)

    for bird in birds:
        bird.draw(win)

    #bird.draw(win)
    pygame.display.update()

def main(genomes,config):

    global GEN
    GEN +=1
    win = pygame.display.set_mode((WIDTH,HEIGHT))
    #gen += 1

    nets=[] #Keep track of the neural network that controls each bird
    ge=[] #Keep track of each bird
    #bird=Bird(230,350)
    birds=[] #Create multiple birds

    for _, g in genomes:
        net=neat.nn.FeedForwardNetwork.create(g,config) #Create the neural network
        nets.append(net) #Append NN to the list
        birds.append(Bird(230,350)) #Create a bird object that starts at the same position as other birds
        g.fitness=0 #Initial fitness
        ge.append(g)

    base=Base(730)
    pipes=[Pipe(650)]
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    score=0

    run=True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                run=False
                pygame.quit()
                quit()

        #In case there are 3 or more pipes on the screen at the same time, we have to still consider
        #the distance of the first 2 pipes
        pipe_ind=0
        if len(birds) > 0:
            #Change the pipe the bird is looking at to  the second pipe in the list
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind=1
        else:
            run = False
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1 #Give the bird some fitness so it survives for a little while

            #Activate the NN with inputs
            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:
                bird.jump()

        #bird.move()
        add_pipe=False
        rem=[]
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird,win):
                    ge[x].fitness -= 1 #If the bird hits the pipe, deduct the score
                    #Remove underperforming birds and don't use them in the next interation
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                #Check if bird has passed the pipe
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed=True
                    add_pipe=True

            #If pipe moves off screen append them to the removed list
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            pipe.move()

        if add_pipe:
            score += 1
            #Increse the fitness score
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(600)) #Create new pipe

        #Remove off screen pipes
        for r in rem:
            pipes.remove(r)

        for x, bird in enumerate(birds):
            #Check if bird hits the ground or flies all the way up
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        base.move()
        draw_win(win,birds,pipes,base,score, GEN)

def run(config_path):
    config=neat.config.Config(neat.DefaultGenome,neat.DefaultReproduction,neat.DefaultSpeciesSet,neat.DefaultStagnation,config_path)

    p=neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats=neat.StatisticsReporter()
    p.add_reporter(stats)

    winner=p.run(main,50)

if __name__ == "__main__":
    local_dir=os.path.dirname(__file__)
    config_path=os.path.join(local_dir,"configFile.txt")
    run(config_path)