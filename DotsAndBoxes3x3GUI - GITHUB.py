'''
Learning Boxes and Dots through reinforcement learning.
Learns to play the game over time.
Reinforcement Learning code adapted from Professor R. Vincent's Tic-Tac-Toe
reinforcement learning example.
GUI code adapted from ssolanki's Dot-Box-Game-Python on github
'''

import random
from tkinter import *
from tkinter import messagebox, font
import sys

# These define the reward function.
R_CONTINUE = -5.0
R_WIN = 0.0
R_LOSS = -100.0
R_TIE = -50.0
R_BOX = -1.0

#These define the TKinter GUI Parameters
TOL = 20
CELLSIZE = 60
OFFSET = 37
CIRCLERAD = 5
DOTOFFSET = OFFSET + CIRCLERAD
GAME_H = 200
GAME_W = 200

class MyFrame(Frame):
    '''GUI for Boxes and Dots game'''
    def __init__(self, master, boxes, player):
        Frame.__init__(self, master)
        self.GO_font = font.Font(self, name="GOFont", family = "Times",weight="bold",size=36)
        self.canvas = Canvas(self, height = GAME_H, width = GAME_W,bg="navy")
        self.canvas.bind("<Button-1>", lambda e:self.click(e))  #binds click function to left mouse button
        self.canvas.grid(row=1,column=0)
        self.dots = [[self.canvas.create_oval(CELLSIZE*i+OFFSET, CELLSIZE*j+OFFSET, CELLSIZE*i+OFFSET+2*CIRCLERAD, CELLSIZE*j+OFFSET+2*CIRCLERAD, fill="white") for j in range(3)] for i in range(3)]
        self.grid()
        self.boxes = boxes
        self.player = player
        self.boxes._state = self.boxes.start()
        self.AI_move() # AI Plays first

    def click(self, event):
        '''Moves made by players on each click'''
        line = self.player_move(event.x,event.y) # human player moves
        self.new_box_made(line)
        while self.boxes._turn == 0 and not self.boxes.done():
            line = self.AI_move() # AI player moves
            self.new_box_made(line)
        if self.boxes.done():
            # opens endgame popup
            if self.boxes.winner() == 1:
                MsgBox = messagebox.askquestion(title="GAME OVER", message = "You Win! :D \n Would you like to play again?")
            elif self.boxes.winner() == -1:
                MsgBox = messagebox.askquestion(title="GAME OVER", message = "You Tie! \n Would you like to play again?")
            else:
                MsgBox = messagebox.askquestion(title="GAME OVER", message = "You Lose! D: \n Would you like to play again?")
            if MsgBox == 'yes':
                #reinitializes frame and board
                self.canvas.delete("all")
                self.boxes.__init__(3,3)
                self.boxes._state = self.boxes.start()
                Frame.__init__(self, tk)
                self.dots = [[self.canvas.create_oval(CELLSIZE*i+OFFSET, CELLSIZE*j+OFFSET, CELLSIZE*i+OFFSET+2*CIRCLERAD, CELLSIZE*j+OFFSET+2*CIRCLERAD, fill="white") for j in range(3)] for i in range(3)]
                self.AI_move()
            else:
                tk.destroy()
                sys.exit(0)

    def AI_move(self):
        '''AI player making a move on the GUI board'''
        a = self.player.policy(self.boxes._state,self.boxes) # determines action
        s0 = self.boxes._state
        s1 = self.boxes.make_move(self.boxes._state,a,1)
        self.boxes.addEdge(s0,a)
        self.boxes._state = s1
        #converts action to initial and final nodes
        if a%(3*2-1) < 3-1:
            initial = a-(a//(3*2-1))*(3-1)
            final = initial + 1
        else:
            initial = a-(a//(3*2-1)+1)*(3-1)
            final = initial + 3
            # converts initial final nodes to coordinates on the GUI
        startx = (initial%3)*CELLSIZE + OFFSET + CIRCLERAD
        starty = (initial//3)*CELLSIZE + OFFSET + CIRCLERAD
        if final - initial == 1:
            endx = startx + CELLSIZE
            endy = starty
        else:
            endx = startx
            endy = starty + CELLSIZE
        # draws and returns line
        return self.canvas.create_line(startx,starty,endx,endy,fill="white")

    def player_move(self,x,y):
        '''Human player making a move on the GUI board'''
        orient = self.isclose(x,y)
        if orient:
            startx = CELLSIZE * ((x-OFFSET)//CELLSIZE) + DOTOFFSET
            starty = CELLSIZE * ((y-OFFSET)//CELLSIZE) + DOTOFFSET
            # converts from GUI coords to initial node
            initial = (startx - OFFSET - CIRCLERAD)//CELLSIZE + 3*(starty-OFFSET-CIRCLERAD)//CELLSIZE
            # converts from initial node and orientation to action
            if orient == HORIZONTAL and initial%3 < 2:
                endx = startx + CELLSIZE
                endy = starty
                a = initial%3 + 5*(initial//3)
            elif orient == VERTICAL and initial > -1 and initial < 12:
                endx = startx
                endy = starty + CELLSIZE
                a = initial%3+2+5*(initial//3)
            else:
                a = -1
            # if legal move, make move
            if a in self.boxes.legal_moves(self.boxes._state):
                s0 = self.boxes._state
                s1 = self.boxes.make_move(self.boxes._state,a,1)
                self.boxes.addEdge(s0,a)
                self.boxes._state = s1
                # draws and returns line
                return self.canvas.create_line(startx,starty,endx,endy,fill="white")
        return None

    def new_box_made(self, line):
        '''Determines when fill_in() needs to label a box'''
        if not line == None:
            for i in range(len(self.boxes._points)):
                if not self.boxes._points[i] == 0:
                    if self.boxes._points[i] == 1:
                        turn = "You"
                    else:
                        turn = "AI"
                    self.fill_in(((i%2+1/2)*CELLSIZE+OFFSET+CIRCLERAD,(i//2+1/2)*CELLSIZE+OFFSET+CIRCLERAD), turn)

    def fill_in(self, coords, turn):
        '''Labelling boxes obtained by a player'''
        x,y = coords
        # fills in box
        self.canvas.create_text(x,y,text=turn, fill="white")

    def isclose(self, x, y):
        ''' Returns orientation of lines nearby'''
        x -= OFFSET
        y -= OFFSET
        dx = x - (x//CELLSIZE)*CELLSIZE
        dy = y - (y//CELLSIZE)*CELLSIZE
        if abs(dx) < TOL:
            if abs(dy) < TOL:
                return None  # mouse in corner of box; ignore
            else:
                return VERTICAL
        elif abs(dy) < TOL:
            return HORIZONTAL
        else:
            return None

class generic_player(object):
    '''Generic player. Base object of all other player classes.'''
    def __init__(self, game, player_num):
        self.game = game
        self.player_num = player_num
        self.state = None

    def policy(self, s0, boxes):
        '''Selects a move at random.'''
        actions = self.game.legal_moves(s0)
        return random.choice(actions)

class tdzero_player(generic_player):
    '''Learns to play tic-tac-toe using basic temporal difference
    learning, known as TD(0).'''
    def __init__(self, game, player_num):
        super().__init__(game, player_num)
        self.V = {}
        self.alpha = 0.1
        self.gamma = 0.95
        self.epsilon = 0.0
        self.games = 0
        self.won = 0

    def getV(self, s):
        '''Return the estimated value of the given state.'''
        s_str = ""
        for i in s:
            s_str += str(i)
        return self.V.get(s_str, R_WIN)

    def learn(self, r, s1, s0):
        '''TD(0) update for value function.'''
        s0_str = ""
        s1_str = ""
        for i in s0:
            s0_str += str(i)
        for i in s1:
            s1_str += str(i)
        v0 = self.getV(s0_str)
        v1 = self.getV(s1_str)
        self.V[s0_str] = v0 + self.alpha * (r + self.gamma * v1 - v0)

    def policy(self, s0, boxes):
        '''Returns a move chosen by an epsilon-greedy policy.'''
        actions = self.game.legal_moves(s0)
        if len(actions) == 0:
            print("no legal moves")
            return -1

        if random.random() < self.epsilon:
            best_action = random.choice(actions)
        else:
            # select a greedy move, breaking ties randomly.
            best_value = -float('inf')
            best_action = -1
            n_ties = 1
            for action in actions:
                s1 = self.game.make_move(s0, action, self.player_num)
                value = self.getV(s1)
                if value > best_value:
                    best_value = value
                    best_action = action
                    n_ties = 1
                elif value == best_value:
                    # break the tie to encourage exploration.
                    n_ties += 1
                    if random.random() < 1 / n_ties:
                        best_value = value
                        best_action = action
        return best_action

class BoxesAndDots_rl(object):
    '''Boxes and Dots class initializes and handles the game, game learning,
    and board.'''
    def __init__(self, dimX, dimY):
        '''Initializes the game with a set of dimensions for the game board'''
        def buildBoxes(width,height):
            '''Creates a list of all the existing boxes where each box is
            represented as a list of the vertex nodes of that box'''
            counter = 0
            boxList = [list() for i in range((width-1)*(height-1))]
            for x in range(width*height):
                if (x+1)%width==0:
                    continue
                elif x>=(height*width-width):
                    continue
                else:
                    boxList[counter].append(x)
                    boxList[counter].append(x+1)
                    boxList[counter].append(x+width)
                    boxList[counter].append(x+width+1)
                    counter+=1
            return boxList

        self._width = dimX
        self._height = dimY
        self._edge = 0
        self._turn = 0
        self._boxcreated = False
        self._adj = [list() for i in range(dimX*dimY)]
        self._state = [0 for i in range ((dimX-1)*dimY +(dimY-1)*dimX)]
        self._boxes = buildBoxes(self._width, self._height)
        self._points = [0 for i in range(len(self._boxes))]

    def addEdge(self,s0, a):
        '''Adds edges between two vertices.'''
        #converts action to initial and final nodes
        if a%(self._width*2-1) < self._width-1:
            initial = a-(a//(self._width*2-1))*(self._width-1)
            final = initial + 1
        else:
            initial = a-(a//(self._width*2-1)+1)*(self._width-1)
            final = initial + self._width
        # if legal move, adds line to board
        if a in boxes.legal_moves(s0):
            self._adj[initial].append(final)
            self._adj[final].append(initial)
            self._edge += 1
            boxes.boxCheck(initial,final)
            # updates turn
            self._turn = 1 - self._turn
        else:
            print("non-legal move")

    def boxCheck(self, initial, final):
        '''Checks if box is completed'''
        boxesToCheck = []
        box_created = False
        for box in self._boxes:
            if (initial in box) and (final in box):
                boxesToCheck.append(box)
        for box in boxesToCheck:
            # checks to see if box is surrounded by edges
            if box[1] in self._adj[box[0]] and box[2] in self._adj[box[0]] and box[1] in self._adj[box[3]] and box[2] in self._adj[box[3]]:
                self._points[self._boxes.index(box)] = self._turn*2-1
                box_created = True
        if box_created:
            self._boxcreated = self._turn
            self._turn = 1 - self._turn
        else:
            self._boxcreated = -1

    def winner(self):
        '''Returns the winner of the game'''
        box_sum = 0
        for i in self._points:
            box_sum += i
        if box_sum > 0:
            return 1
        elif box_sum == 0:
            return -1
        else:
            return 0

    def legal_moves(self, state):
        '''Returns a list of all possible, legal actions'''
        legal_moves = []
        for i in range(len(state)):
            if state[i] == 0:
                legal_moves.append(i)
        return legal_moves

    def make_move(self, state, action, player):
        '''Updates the state with an action'''
        new_state = state.copy()
        new_state[action] = 1
        return new_state

    def done(self):
        '''Determines whether or not the game is completed'''
        if boxes._edge < (boxes._width-1)*(boxes._height) + (boxes._height-1)*(boxes._width):
            return False
        else:
            return True

    def reward(self, p1):
        '''Returns a reward for a completed action'''
        if p1 == 0:
            p2 = 1
        else:
            p2 = 0
        if self.done():
            if self.winner() == p1:
                return R_WIN
            elif self.winner() == p2:
                return R_LOSS
            else:
                return R_TIE
        if self._boxcreated == p1:
            return R_BOX
        return R_CONTINUE

    def start(self):
        '''Initialize the state of the game.'''
        return self._state

    @staticmethod
    def game(players):
        '''Play one game.'''
        boxes.__init__(boxes._width, boxes._height) # reinitializes game
        s0 = boxes.start()
        n_player = 0
        finished = False
        while not finished:
            player = players[n_player]
            a = player.policy(s0, boxes) # finds action
            s1 = boxes.make_move(s0, a, player.player_num) # takes action
            boxes.addEdge(s0,a) # updates board and state
            boxes._state = s1
            # both players learn from all moves.
            for player in players:
                r = boxes.reward(player.player_num) # get the reward.
                player.learn(r, s1, s0)
                if r != R_CONTINUE and r != R_BOX:
                    finished = True
            s0 = s1
            n_player = boxes._turn

    @staticmethod
    def play(players, n_games):
        '''Plays multiple games'''
        i = 0
        while i != n_games:
            i += 1
            boxes.game([players[0],players[1]])


width,height = 3,3
n_games = int(input("Choose number of games to train over: "))
boxes = BoxesAndDots_rl(width,height)
p1 = tdzero_player(boxes, 0) # AI playing first
p2 = tdzero_player(boxes, 1) # AI playing second
boxes.play([p1, p2], n_games) # train actual AI
p1.epsilon = 0.0 # exploit only.
boxes = BoxesAndDots_rl(width,height) # reinitialize game
# tkinter GUI
tk = Tk()
tk.f = MyFrame(tk,boxes,p1)
tk.mainloop()
