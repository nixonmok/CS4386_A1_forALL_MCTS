 ###################################
 # CS4386 Semester B, 2022-2023
 # Assignment 1
 # Name: [Your name]
 # Student ID: [Your student ID] 
 ###################################

import copy 
from math import inf as infinity
import random
class AIPlayer(object):
        def __init__(self, name, symbole, isAI=False):
            self.name = name
            self.symbole = symbole
            self.isAI = isAI
            self.score=0

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

        def available_cells(self,state,player):
            print(state[0,0])
            cells = []
            #print(list(enumerate(state)))

            for x, row in enumerate(state): #row = each row, e.g: [(0, None), (1, None), (2, None), (3, None), (4, None), (5, None)]
                for y, cell in enumerate(row): #cell = each block, e.g: None, X, Y
                    if (cell is None):
                        if (self.symbole=="X") and ((x+y)%2==0):
                            cells.append([x, y])
                        if (self.symbole=="O") and ((x+y)%2==1):    
                            cells.append([x, y])
            print(cells)                    
            return cells
        
        def calculate_Score(self, state,x ,y): #calculate score of the current board, copy from game.py
            #print("xy:",x,y)
            score=0

            #1.check horizontal
            if((state[x][0] == self.get_symbole()) and (state[x][1] == self.get_symbole()) and  (state[x][2]== self.get_symbole()) and (state[x][3] == self.get_symbole()) and (state[x][4] == self.get_symbole()) and (state[x][5]  == self.get_symbole())):  
                score+=6
                #print("horizontal 6")
            else:
                if (state[x][0] == self.get_symbole()) and (state[x][1] == self.get_symbole()) and  (state[x][2]== self.get_symbole()) and (state[x][3] == None):
                    if y==0 or y==1 or y==2:
                        score+=3
                        #print("1horizontal 3")
                elif (state[x][0] == None) and (state[x][1] == self.get_symbole()) and  (state[x][2]== self.get_symbole()) and (state[x][3] == self.get_symbole()) and (state[x][4] == None):
                    if y==1 or y==2 or y==3:
                        score+=3
                        #print("2horizontal 3")
                elif  (state[x][1] == None) and (state[x][2] == self.get_symbole()) and  (state[x][3]== self.get_symbole()) and (state[x][4] == self.get_symbole()) and (state[x][5] == None):
                    if y==2 or y==3 or y==4:
                        score+=3
                        #print("3horizontal 3")
                elif  (state[x][2] == None) and  (state[x][3]== self.get_symbole()) and (state[x][4] == self.get_symbole()) and (state[x][5] == self.get_symbole()):
                    if y==3 or y==4 or y==5:
                        score+=3
                        #print("4horizontal 3")
                    
                #2.check vertical
                if((state[0][y] == self.get_symbole()) and (state[1][y] == self.get_symbole()) and (state[2][y] == self.get_symbole()) and (state[3][y]== self.get_symbole()) and (state[4][y]== self.get_symbole()) and (state[5][y]== self.get_symbole())):
                    score+=6
                    #print("vertical 6")
                else:
                    if (state[0][y] == self.get_symbole()) and (state[1][y] == self.get_symbole()) and  (state[2][y]== self.get_symbole()) and (state[3][y] == None):
                        if x==0 or x==1 or x==2:
                            score+=3
                            #print("1vertical 3")
                    elif (state[0][y] == None) and (state[1][y] == self.get_symbole()) and  (state[2][y]== self.get_symbole()) and (state[3][y] == self.get_symbole()) and (state[4][y] == None):
                        if x==1 or x==2 or x==3:
                            score+=3
                            #print("2vertical 3")
                    elif (state[1][y] == None) and (state[2][y] == self.get_symbole()) and  (state[3][y]== self.get_symbole()) and (state[4][y] == self.get_symbole()) and (state[5][y] == None):
                        if x==2 or x==3 or x==4:
                            score+=3
                            #print("3vertical 3")
                    elif  (state[2][y] == None) and  (state[3][y]== self.get_symbole()) and (state[4][y]== self.get_symbole()) and (state[5][y] == self.get_symbole()):
                        if x==3 or x==4 or x==5:
                            score+=3
                            #print("4vertical 3")


            return score
        
        def game_over(self, state):
            for rows in state:
                for cell in rows:
                    if cell is None:
                        return False
            return True

        def minimax(self, state, depth, maxTurn, turn, myScore, oppScore):
            nextMax = maxTurn
            if depth == 0 or self.game_over(state):
                return myScore - oppScore
            if maxTurn:
                bestScore = -infinity
                nextMax = False
            else:
                bestScore = infinity
                nextMax = True
            
            avaliableMove = self.available_cells(state, turn)
            for move in avaliableMove:#!!!need to calculate the score of the player!!!
                simulationState = copy.deepcopy(state) #copy the board
                x = move[0]
                y = move[1]
                simulationState[x,y] = self.get_symbole()
                if maxTurn:
                    myScore += self.calculate_Score(state,x,y)
                else:
                    oppScore += self.calculate_Score(state,x,y)
                currentScore = self.minimax(simulationState, depth - 1, nextMax, turn, myScore, oppScore)
                if maxTurn:
                    bestScore = max(bestScore, currentScore)
                else:
                    bestScore = min(bestScore, currentScore)
                
        
            
        def get_move(self,state,player):
            avaliableMove = self.available_cells(state,player)
            bestMove = None
            bestScore = -infinity #self.score or infinity?
            for move in avaliableMove: #move = pair<char>(x,y)
                #idea: for each move, simulate all possibility and return the best score, return move that have largest score
                simulationState = copy.deepcopy(state) #copy the board
                x = move[0]
                y = move[1]
                simulationState[x,y] = self.get_symbole()
                initialScore = self.calculate_Score(simulationState,x,y)
                currentScore = self.minimax(simulationState, 5, False, player,initialScore,0)
                if currentScore > bestScore:
                    bestScore = currentScore
                    bestMove = move
            return bestMove
        
        

               
