from typing import List
from random import randint
import pygame
from math import atan2, pi

is_p1_ai = False
pygame.init()
score_font = pygame.font.Font('freesansbold.ttf',30)
screenwidth = 800
turn_number = 5
screenheight = 600
mid_width = screenwidth / 2
mid_height = screenheight / 2
boxsize = 60                                                    #size of players
xboundary = screenwidth - boxsize                               #boxes' x & y can't go > these numbers to avoid going past boundaries
yboundary = screenheight - boxsize
score = 0                                                       #score goes up when p2 is it; goes down when p1 is it; goal for p1 is to have the highest score after three turns each
game_end_counter = 0                                            #after each player has had 3 turns as it, game ends
screen = pygame.display.set_mode((screenwidth,screenheight))
done = False
moveAngle = [pi/2, pi/4, 0, -pi/4, -pi/2, -pi * 3/4, pi, pi * 3/4]
color1 = (0, 128, 255)
color2 = (228, 18, 18)
colorit = (0, 255, 0)
color_text = (255, 255, 255)
clock = pygame.time.Clock()
ai_reaction_time = 20 # ai's reaction time in sixtieths of a second

aversion_weight = 3000
border_weight = 150
line_weight = 0.05
last_move_weight = 25

class box:

    def __init__(self, colourkey, x, y, it):
        self.weight_list = [0, 0, 0, 0, 0, 0, 0, 0, 1]         #List of weights that will be used by AI to determine which direction to go, starting from north and going clockwise; last one is stay in place
        self.it = it
        self.colourkey = colourkey
        self.x = x
        self.y = y
        self.x_position_list: List[int] = []
        self.y_position_list: List[int] = []
        self.new_distance = [0, 0, 0, 0, 0, 0, 0, 0]
        self.last_move = 8
        for i in range(ai_reaction_time * 2):
            self.x_position_list.append(self.x)
            self.y_position_list.append(self.y)
    def move(self, pressed):   #moves 7 pixels in one direction, or 5 pixels in two directions (e.g. northwest)
        if pressed[pygame.K_w]:
            self.y -= 5
            if not pressed[pygame.K_a] and not pressed[pygame.K_d]:
                self.y -=2
        if pressed[pygame.K_a]:
            self.x -= 5
            if not pressed[pygame.K_s] and not pressed[pygame.K_w]:
                self.x -=2
        if pressed[pygame.K_s]:
            self.y += 5
            if not pressed[pygame.K_a] and not pressed[pygame.K_d]:
                self.y +=2
        if pressed[pygame.K_d]:
            self.x += 5
            if not pressed[pygame.K_s] and not pressed[pygame.K_a]:
                self.x +=2
        self.boundaries()
    def draw(self):
        pygame.draw.rect(screen, self.colourkey, pygame.Rect(self.x, self.y, 60, 60))
        if self.it == True:
            pygame.draw.rect(screen, colorit, pygame.Rect((self.x + 20), (self.y + 20), 20, 20))
    def ai_move(self, opponent):
        if opponent == 1:
            self.opp_x = p1.x_position_list[ai_reaction_time - 1]
            self.old_opp_x = p1.x_position_list[ai_reaction_time]
            self.opp_y = p1.y_position_list[ai_reaction_time - 1]
            self.old_opp_y = p1.y_position_list[ai_reaction_time]
        else:
            self.opp_x = p2.x_position_list[ai_reaction_time - 1]
            self.old_opp_x = p2.x_position_list[ai_reaction_time]
            self.opp_y = p2.y_position_list[ai_reaction_time - 1]
            self.old_opp_y = p2.y_position_list[ai_reaction_time]
        self.projected_opp_x = self.opp_x + (self.opp_x - self.old_opp_x) * ai_reaction_time
        self.projected_opp_y = self.opp_y + (self.opp_y - self.old_opp_y) * ai_reaction_time
        self.x_line_2 = self.x - self.opp_x                  #uses ai's old position
        self.y_line_2 = self.y - self.opp_y
        #self.distance = (self.x_line**2 + self.y_line**2)**0.5

        self.x_line = self.x - self.projected_opp_x
        self.y_line = self.y - self.projected_opp_y
        self.distance = (self.x_line**2 + self.y_line**2)**0.5      #this distance number isn't perfect but does do the job I think
        if self.it == True:
            self.ai_weight_it(self.x_line, self.y_line)
        else:
            self.ai_weight_not_it(self.x_line, self.y_line)
     
        '''random_choice = randint(0, sum(self.weight_list))
        tracker = 0
        choice = 8
        for z in range(0, 9):
            tracker += self.weight_list[z]
            if random_choice <= tracker:
                choice = z
                break
        '''
        '''if randint(0, 20) == 10:
            temp_list = self.weight_list
            temp_list.remove(max(temp_list))
            choice = temp_list.index(max(temp_list))
        else:'''
        choice = self.weight_list.index(max(self.weight_list))
        if choice == 0:
            self.y -= 7
            self.last_move = 0
        elif choice == 1:
            self.x += 5
            self.y -= 5
            self.last_move = 1
        elif choice == 2:
            self.x += 7
            self.last_move = 2
        elif choice == 3:
            self.x += 5
            self.y += 5
            self.last_move = 3
        elif choice == 4:
            self.y += 7
            self.last_move = 4
        elif choice == 5:
            self.x -= 5
            self.y += 5
            self.last_move = 5
        elif choice == 6:
            self.x -= 7
            self.last_move = 6
        elif choice == 7:
            self.x -= 5
            self.y -= 5
            self.last_move = 7

        self.boundaries()

    def ai_weight_it(self, x_line, y_line):
        self.get_move_distance(x_line, y_line)
        multiplier = 10
        for i in range(0, 8):
            weight_mod = self.distance -  self.new_distance[i]
            if weight_mod < 0:
                weight_mod = weight_mod * 2
            self.weight_list[i] += weight_mod * multiplier
            self.weight_list[i] = int(round(self.weight_list[i]))
        #if score % 60 == 0:
            #print(self.weight_list)
    def ai_weight_not_it(self, x_line, y_line):

        self.get_move_distance(x_line, y_line)
        multiplier = aversion_weight / self.distance
        for i in range(0, 8):
            weight_mod = self.new_distance[i] - self.distance
            if weight_mod < 0:
                weight_mod = weight_mod * 2
            self.weight_list[i] += weight_mod * multiplier

        x_distance = min(self.x + 30, screenwidth - self.x + 30)
        y_distance = min(self.y + 30, screenheight - self.y + 30)
        x_move = ((self.x + 30 - mid_width)  / mid_width) * border_weight / x_distance
        y_move = ((self.y  + 30 - mid_height)/ mid_height) * border_weight / y_distance
        #if score % 60 == 0:
            #print("%.2f, %.2f, %d" % (x_move, y_move, mid_width)
        self.weight_list[0] += 100 * y_move
        self.weight_list[1] += 71 * y_move - 71 * x_move
        self.weight_list[2] -= 100 * x_move
        self.weight_list[3] -= 71 * y_move + 71 * x_move
        self.weight_list[4] -= 100 * y_move
        self.weight_list[5] -= 71 * y_move + -71 * x_move
        self.weight_list[6] += 100 * x_move
        self.weight_list[7] -= -71 * y_move + -71 * x_move
        
        if y_move < 0:                                      #doubling negative weights
            self.weight_list[0] += 100 * y_move
            self.weight_list[1] += 71 * y_move
            self.weight_list[7] += 71 * y_move
        else:
            self.weight_list[4] -= 100 * y_move
            self.weight_list[3] -= 71 * y_move
            self.weight_list[5] -= 71 * y_move
        if x_move < 0:
            self.weight_list[5] += 71 * x_move
            self.weight_list[6] += 100 * x_move
            self.weight_list[7] += 71 * x_move
        else:
            self.weight_list[1] -= 71 * x_move
            self.weight_list[2] -= 100 * x_move
            self.weight_list[3] -= 71 * x_move
        if self.y < 5:
            self.weight_list[0] -= 1000
            self.weight_list[1] -= 1000
            self.weight_list[7] -= 1000
        elif self.y > yboundary - 5:
            self.weight_list[3] -= 1000
            self.weight_list[4] -= 1000
            self.weight_list[5] -= 1000
        if self.x < 5:
            self.weight_list[5] -= 1000
            self.weight_list[6] -= 1000
            self.weight_list[7] -= 1000
        elif self.x > xboundary - 5:
            self.weight_list[1] -= 1000
            self.weight_list[2] -= 1000
            self.weight_list[3] -= 1000

        self.weight_list[self.last_move] += last_move_weight

        self.weight_list[8] -= 200

        line_lengths = self.drawing_lines(self.x, self.y, self.projected_opp_x, self.projected_opp_y)
        for i in range (0, 8):
            self.weight_list[i] += line_lengths[i] * line_weight
        '''for i in range (0, 9):
            
            self.weight_list[i] = int(round(self.weight_list[i]))
            if self.weight_list[i] < 0:
                self.weight_list[i] = 0'''

    def get_move_distance(self, x_line, y_line):
        self.new_distance[0] = ((x_line) ** 2 + (y_line - 7) ** 2) ** 0.5
        self.new_distance[1] = ((x_line + 5) ** 2 + (y_line - 5) ** 2) ** 0.5
        self.new_distance[2] = ((x_line + 7) ** 2 + (y_line) ** 2) ** 0.5
        self.new_distance[3] = ((x_line + 5) ** 2 + (y_line + 5) ** 2) ** 0.5
        self.new_distance[4] = ((x_line) ** 2 + (y_line + 7) ** 2) ** 0.5
        self.new_distance[5] = ((x_line - 5) ** 2 + (y_line + 5) ** 2) ** 0.5
        self.new_distance[6] = ((x_line - 7) ** 2 + (y_line) ** 2) ** 0.5
        self.new_distance[7] = ((x_line - 5) ** 2 + (y_line - 5) ** 2) ** 0.5

    def drawing_lines(self, own_x, own_y, line_opp_x, line_opp_y):
        line = [0, 0, 0, 0, 0, 0, 0, 0]
        if line_opp_x > own_x - boxsize and line_opp_x < own_x + boxsize and line_opp_y < own_y - boxsize:
            line[0] = own_y - (line_opp_y + boxsize)
        else:
            line[0] = own_y

        constant = own_y + own_x
        if line_opp_y + line_opp_x > constant - boxsize * 2 and line_opp_y + line_opp_x < constant + boxsize * 2 and line_opp_y - line_opp_x < own_y - own_x - boxsize * 2:
            if line_opp_x - (own_x + boxsize) > own_y - (line_opp_y + boxsize):
                line[1] = (line_opp_x - (own_x + boxsize)) * 1.4
            else:
                line[1] = (own_y - (line_opp_y + boxsize)) * 1.4
        elif screenwidth - (own_x + boxsize)< own_y:
            line[1] = (screenwidth - (own_x + boxsize)) * 1.4
        else:
            line[1] = (own_y) * 1.4

        if line_opp_y > own_y - 60 and line_opp_y < own_y + 60 and line_opp_x > own_x + boxsize:
            line[2] = line_opp_x - (own_x + boxsize)
        else:
            line[2] = screenwidth - (own_x + boxsize)

        constant = own_y - own_x
        opp_constant = line_opp_y - line_opp_x
        if opp_constant > constant - boxsize * 2 and opp_constant < constant + boxsize * 2 and line_opp_y + line_opp_x > own_y + own_x + boxsize * 2:
            if line_opp_x - (own_x + boxsize) > line_opp_y - (own_y + boxsize):
                line[3] = (line_opp_x - (own_x + boxsize)) * 1.4
            else:
                line[3] = (line_opp_y - (own_y + boxsize)) * 1.4
        elif screenwidth - (own_x + boxsize)< screenheight - (own_y + boxsize):
            line[3] = (screenwidth - (own_x + boxsize)) * 1.4
        else:
            line[3] = (screenheight - (own_y + boxsize)) * 1.4

        if line_opp_x > own_x - boxsize and line_opp_x < own_x + boxsize and line_opp_y > own_y + boxsize:
            line[4] = line_opp_y - (own_y + boxsize)
        else:
            line[4] = screenheight - (own_y + boxsize)

        constant = own_y + own_x
        if line_opp_y + line_opp_x > constant - boxsize * 2 and line_opp_y + line_opp_x < constant + boxsize * 2 and line_opp_y - line_opp_x > own_y - own_x + boxsize:
            if line_opp_x - (own_x + boxsize) > line_opp_y - (own_y + boxsize):
                line[5] = (own_x - (line_opp_x + boxsize)) * 1.4
            else:
                line[5] = (line_opp_y - (own_y + boxsize)) * 1.4
        elif own_x < screenheight - (own_y + boxsize):
            line[5] = own_x * 1.4
        else:
            line[5] = (screenheight - (own_y + boxsize)) * 1.4

        if line_opp_y > own_y - 60 and line_opp_y < own_y + 60 and line_opp_x + boxsize < own_x:
            line[6] = own_x - (line_opp_x + boxsize)
        else:
            line[6] = own_x

        constant = own_y - own_x
        opp_constant = line_opp_y - line_opp_x
        if opp_constant > constant - boxsize * 2 and opp_constant < constant + boxsize * 2 and line_opp_y + line_opp_x < own_y + own_x - boxsize:
            if own_x - (line_opp_x + boxsize) > own_y - (line_opp_y + boxsize):
                line[7] = (own_x - (line_opp_x + boxsize)) * 1.4
            else:
                line[7] = (own_y - (line_opp_y + boxsize)) * 1.4
        elif own_x < own_y:
            line[7] = own_x * 1.4
        else:
            line[7] = own_y * 1.4
        return line

    def boundaries(self):  #enforces boundaries, resets weights to 0, and stores where player was for past X frames, where X is ai_reaction_time
        self.weight_list = [0, 0, 0, 0, 0, 0, 0, 0, 1]
        if self.y < 0:
            self.y = 0
        elif self.y > yboundary:
            self.y = yboundary
        if self.x < 0:
            self.x = 0
        elif self.x > xboundary:
            self.x = xboundary
        for t in range ((ai_reaction_time * 2 - 1), -1, -1):
            if t != 0:
                self.x_position_list[t] = self.x_position_list[t - 1]
                self.y_position_list[t] = self.y_position_list[t - 1]
            else:
                self.x_position_list[t] = self.x
                self.y_position_list[t] = self.y
p1 = box(color1, 30, 30, False)
p2 = box(color2, screenwidth - 90, screenheight - 90, True)
while not done:
    for z in pygame.event.get():
        if z.type == pygame.QUIT:
            done = True

    key = pygame.key.get_pressed()
    if p1.x > (p2.x - 60) and p1.x < (p2.x + 60) and p1.y > (p2.y - 60) and p1.y < (p2.y + 60):
        p1.x = 30
        p1.y = 30
        p2.x = screenwidth - 90
        p2.y = screenheight - 90
        p1.it = not p1.it
        p2.it = not p2.it
        game_end_counter += 1
    screen.fill((0, 0, 0))
    if p1.it == True:
        score -= 1
    elif p1.it == False:
        score += 1
    if is_p1_ai == True:
        p1.ai_move(2)
    else:
        p1.move(key)

    p2.ai_move(1)
    p1.draw()
    p2.draw()
    score_surface = score_font.render("%d" % (score / 6), True, color_text)
    score_rect = score_surface.get_rect()
    score_rect.center = ((screenwidth / 2),20)
    screen.blit(score_surface, score_rect)
    pygame.display.flip()
    clock.tick(60)
    if game_end_counter == turn_number * 2:
        print ("Your final score is %d" % (score / 6))
        pygame.quit()
        done = True