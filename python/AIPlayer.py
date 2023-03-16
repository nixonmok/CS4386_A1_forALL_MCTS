 ###################################
 # CS4386 Semester B, 2022-2023
 # Assignment 1
 # Name: Mok Chun Ho
 # Student ID: 56819145
 ###################################

from collections import defaultdict,namedtuple
import copy 
from math import inf as infinity
import random
import time
import math
import random
import numpy as np

namedTuple = namedtuple("stateNode", "state player move score originalPlayer")
class AIPlayer(object):
    def __init__(self, name, symbole, isAI=False):
        self.name = name
        self.symbole = symbole
        self.isAI = isAI
        self.score=0
        self.timeLimit=1

    def stat(self):
        return self.name + " won " + str(self.won_games) + " games, " + str(self.draw_games) + " draw."

    def __str__(self):
        return self.name
    def get_isAI(self):
        return self.isAI
    def get_symbole(self):
        return self.symbole
    def get_score(self):
        return self.score
    def add_score(self,score):
        self.score+=score
        
    def get_move(self,state,player):
        oneDlistState = []
        for x, row in enumerate(state): #row = each row, e.g: [(0, None), (1, None), (2, None), (3, None), (4, None), (5, None)]
            for y, cell in enumerate(row): #cell = each block, e.g: None, X, Y
                if state[x][y] == 'X': #X=black=p1=true,O=white=p2=false
                    oneDlistState.append(True)
                elif state[x][y] == 'O':
                    oneDlistState.append(False)
                else:
                    oneDlistState.append(None)
        stateTuple = tuple(oneDlistState) #use tuple becuase it is hashable
        print(stateTuple)
        monteCarlosTree = MCTS(player)
        board = stateNode(stateTuple,player,-1, 0, player) #state player move score originalPlayer
        startTime = time.time()
        while True:
            curTime = time.time()
            if curTime - startTime >= 2:
                break
            monteCarlosTree.do_rollout(board)
        bestMove = monteCarlosTree.choose(board) #returned a stateNode
        x = bestMove // 6
        y = bestMove % 6
        print(x,y)
        return list([x,y]) #should return a pair [6*x+y]
        
class MCTS():
    "Monte Carlo tree searcher. First rollout the tree then choose a move."

    def __init__(self,originalPlayer, exploration_weight=1):
        self.Q = defaultdict(int)  # total reward of each node
        self.N = defaultdict(int)  # total visit count for each node
        self.children = dict()  # children of each node
        self.exploration_weight = exploration_weight
        self.originalPlayer = originalPlayer

    def choose(self, node): #choose = return move
        "Choose the best successor of node. (Choose a move in the game)"
        if node.is_terminal():
            raise RuntimeError(f"choose called on terminal node {node}")

        if node not in self.children:
            return node.find_random_child()

        def score(n):
            if self.N[n] == 0:
                return float("-inf")  # avoid unseen moves
            return self.Q[n] / self.N[n]  # average reward
        maxNode = max(self.children[node], key=score)
        print(maxNode)
        return maxNode.move

    def do_rollout(self, node): #do rollout, then choose
        "Make the tree one layer better. (Train for one iteration.)"
        path = self._select(node) #揀未explore嘅,目前層數explore曬就揀最高uct
        leaf = path[-1] #[-1] mean last element
        #print("\n---------leaf--------\n",leaf,"\n--------------boardline-------------\n")
        self._expand(leaf)
        reward = self._simulate(leaf)
        self._backpropagate(path, reward)
        #print("finished one cycle")

    def _select(self, node):
        "Find an unexplored descendent of `node`"
        path = []
        while True:
            path.append(node) #目前node加落路徑
            if node not in self.children: #係兩舊野入面 = visit過
                #print("not in child, path: ",path)
                # node is either unexplored or terminal
                return path
            #objective: add one of unexplored node
            unexplored = self.children[node] - self.children.keys()
            #print(self.children[node])
            #print(self.children.keys())
            #print("unexplored: ",unexplored)
            if unexplored:
                #print("entered")
                n = unexplored.pop()
                path.append(n)
                return path
            node = self._uct_select(node)  # descend a layer deeper,揀uct最大嘅node,繼續while loop

    def _expand(self, node):
        "Update the `children` dict with the children of `node`"
        if node in self.children:
            #print("here")
            return  # already expanded
        #print("\nnode is: ", node,"\ntype: ",type(node), "\n")
        self.children[node] = node.find_children()

    def _simulate(self, node):
        "Returns the reward for a random simulation (to completion) of `node`"
        score = 0
        while True:
            if node.is_terminal():
                reward = node.reward(score) 
                return reward
            node = node.find_random_child()
            #print(node)
            score += node.score

    def _backpropagate(self, path, reward):
        "Send the reward back up to the ancestors of the leaf"
        for node in reversed(path): #計路徑所有node嘅結果(win/played)
            self.N[node] += 1
            self.Q[node] += reward
            reward = 1 - reward  # 1 for me is 0 for my enemy, and vice versa

    def _uct_select(self, node):
        "Select a child of node, balancing exploration & exploitation"


        log_N_vertex = math.log(self.N[node])

        def uct(n):
            "Upper confidence bound for trees"
            return self.Q[n] / self.N[n] + self.exploration_weight * math.sqrt(
                log_N_vertex / self.N[n]
            )
        print(self.children[node])
        return max(self.children[node], key=uct)  #return目前node嘅所以children入面,uct最多嘅一個

class stateNode(namedTuple): #一個board state(版面)
    # def __init__(self, state, player, originalPlayer):
    #     self.state = state #should be 1d array, board[36]
    #     self.player = player #current player = next move player
    #     self.move = -1
    #     self.score = 0
    #     self.originalPlayer = originalPlayer
        #either 0,3,6,-3,-6 -> after changing to this state, the score
    
    def find_children(self):
        "All possible successors of this board state"
        if self.game_over(self.state):#if current board is fulled = gameover = can't evaluate anymore
            return set()
        l = list()
        for i in self.available_cells():
            simulationState = copy.deepcopy(self.state) #simulation state is a tuple
            convert = list(simulationState)
            
            if self.player == 'X': #解決 -> tuple item assignment
                convert[i] = True
            else:
                convert[i] = False
            simulationState = tuple(convert)
            
            score = self.calculate_Score(simulationState,i)
            newNode = stateNode(simulationState,self.player_opponent(),i,score,self.originalPlayer) #state player move score originalPlayer
            l.append(newNode)
        
        s = set(l)
        
        #print("lllllll", l)
        #print("ssssssss ", s)
        return l

    def find_random_child(self):
        "Random successor of this board state (for more efficient simulation)"
        if self.game_over(self.state):#if current board is fulled = gameover = can't evaluate anymore
            return None
        stateList = list()
        for i in self.available_cells():
            simulationState = copy.deepcopy(self.state)
            convert = list(simulationState)
            
            if self.player == 'X': #解決 -> tuple item assignment
                convert[i] = True
            else:
                convert[i] = False
            simulationState = tuple(convert)
            
            score = self.calculate_Score(simulationState,i)
            newNode = stateNode(simulationState,self.player_opponent(),i,score,self.originalPlayer)    
                    
            stateList.append(newNode)
        return random.choice(stateList)

    def is_terminal(self):
        "Returns True if the node has no children"
        return self.game_over(self.state)


    def reward(self,score):
        "Assumes `self` is terminal node. 1=win, 0=loss, .5=tie, etc"
        if not self.game_over(self.state):
            raise RuntimeError(f"reward called on nonterminal board {self.state}")
        
        if score < 0:
            return 0  # Your opponent has just won. Bad.
        if score == 0:
            return 0.5  # Board is a tie
        return 1
    
    def available_cells(self):
        
        cells = [] 
        count = 0
        for i in self.state: #1d array version of provided available_cells
            x = count // 6
            y = count % 6
            if(i is None):
                if (self.player=="X") and ((x+y)%2==0):
                    cells.append(count)
                if (self.player=="O") and ((x+y)%2==1):    
                    cells.append(count)
            count += 1
        return cells
    
    def calculate_Score(self,state,i): #calculate score of the current board, copy from game.py, changed to 1d array version
        scoreAdded=0
        x = i // 6
        y = i % 6
        #1.check horizontal
        #6x+y
        if((state[6*x+0] != None) and (state[6*x+1] != None) and  (state[6*x+2]!= None) and (state[6*x+3] != None) and (state[6*x+4] != None) and (state[6*x+5] != None)):  
            scoreAdded+=6
            #print("horizontal 6")
        else:
            if (state[6*x+0] != None) and (state[6*x+1] != None) and  (state[6*x+2]!= None) and (state[6*x+3] == None):
                if y==0 or y==1 or y==2:
                    scoreAdded+=3
                    #print("1horizontal 3")
            elif (state[6*x+0] == None) and (state[6*x+1] != None) and  (state[6*x+2]!= None) and (state[6*x+3] != None) and (state[6*x+4] == None):
                if y==1 or y==2 or y==3:
                    scoreAdded+=3
                    #print("2horizontal 3")
            elif  (state[6*x+1] == None) and (state[6*x+2] != None) and  (state[6*x+3]!= None) and (state[6*x+4] != None) and (state[6*x+5] == None):
                if y==2 or y==3 or y==4:
                    scoreAdded+=3
                    #print("3horizontal 3")
            elif  (state[6*x+2] == None) and  (state[6*x+3]!= None) and (state[6*x+4] != None) and (state[6*x+5] != None):
                if y==3 or y==4 or y==5:
                    scoreAdded+=3
                    #print("4horizontal 3")
                
        #2.check vertical
        if((state[0+6*y] != None) and (state[1+6*y] != None) and (state[2+6*y] != None) and (state[3+6*y] != None) and (state[4+6*y]!= None) and (state[5+6*y]!= None)):
            scoreAdded+=6
            #print("vertical 6")
        else:
            if (state[0+6*y] != None) and (state[1+6*y] != None) and  (state[2+6*y]!= None) and (state[3+6*y] == None):
                if x==0 or x==1 or x==2:
                    scoreAdded+=3
                    #print("1vertical 3")
            elif (state[0+6*y] == None) and (state[1+6*y] != None) and  (state[2+6*y]!= None) and (state[3+6*y] != None) and (state[4+6*y] == None):
                if x==1 or x==2 or x==3:
                    scoreAdded+=3
                    #print("2vertical 3")
            elif (state[1+6*y] == None) and (state[2+6*y] != None) and  (state[3+6*y]!= None) and (state[4+6*y] != None) and (state[5+6*y] == None):
                if x==2 or x==3 or x==4:
                    scoreAdded+=3
                    #print("3vertical 3")
            elif  (state[2+6*y] == None) and  (state[3+6*y]!= None) and (state[4+6*y] != None) and (state[5+6*y] != None):
                if x==3 or x==4 or x==5:
                    scoreAdded+=3
                    #print("4vertical 3")
        if self.player != self.originalPlayer:
            scoreAdded *= -1
        return scoreAdded
    
    def game_over(self, state):
        for i in state:
            if i == None:
                return False
        #print("entered here")
        return True
    
    def player_opponent(self):
        if self.player == 'X':
            return 'O'
        return 'X'
    
    def __hash__(self):
        "Nodes must be hashable"
        return 123456789

    def __eq__(self, other):
        "Nodes must be comparable"
        if isinstance(other, stateNode):
            return self.state == other.state and \
                self.player == other.player and \
                self.score == other.score and \
                self.originalPlayer == other.originalPlayer and \
                self.move == other.move
        return False               
