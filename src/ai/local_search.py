from typing import Tuple, List

import random
from time import time
import threading
import _thread as thread
import copy

from src.constant import *
from src.model import State, Board, Player, Piece
from src.utility import is_full, is_out, check_streak, place, is_win


class LocalSearchGroup14:
    def __init__(self):
        pass

    def find(self, state: State, n_player: int, thinking_time: float) -> Tuple[str, str]:
        self.thinking_time = time() + thinking_time
        self.player = state.players[(state.round-1)%2]

        # best_movement = (random.randint(0, state.board.col), random.choice([ShapeConstant.CROSS, ShapeConstant.CIRCLE])) #minimax algorithm

        # Local search with thinking time
        best_movement = self.findHillClimbing(state, thinking_time, n_player)
            
        return best_movement

    def getShapeQuota(self, myPlayer: Player) -> int:
        hasil = None
        for k, v in myPlayer.quota.items():
            if(myPlayer.shape == k):
                hasil = v

        return int(hasil)

    def Generate(self, state: State, n_player: int) -> Tuple[int, str] :
        #choose column randomly
        col = random.randint(0, state.board.col-1)
        myPlayer = state.players[n_player]

        # choose shape
        
        if self.getShapeQuota(myPlayer) > 3:
            pick_shape = myPlayer.shape #my shape
        elif self.getShapeQuota(myPlayer) <= 3 and self.getShapeQuota(myPlayer) > 0:
            pick_shape = random.choice([ShapeConstant.CROSS, ShapeConstant.CIRCLE])
        else:
            pick_shape = state.players[1-n_player].shape #opponent shape

        #create new state, add new piece
        i = 0
        while (i < state.board.row and state.board[i, col].shape == ShapeConstant.BLANK):
            i = i+1
        i = i-1
        
        # set current board
        place(state, n_player, pick_shape , col)
        
        #tambah quota
        state.players[n_player].quota[pick_shape] += 1

        return (col, pick_shape)

    def getRandomNeighbor (self, state: State, pick_col: int, pick_shape: str, n_player: int) -> Tuple[int, str] :
        #choose shape and column randomly
        myPlayer = state.players[n_player]
        while True:
            # choose shape
            
            if self.getShapeQuota(myPlayer) > 3:
                sha = myPlayer.shape
            elif self.getShapeQuota(myPlayer) <= 3 and self.getShapeQuota(myPlayer) > 0:
                sha = random.choice([ShapeConstant.CROSS, ShapeConstant.CIRCLE])
            else:
                sha = state.players[1-n_player].shape #opponent shape

            # choose column
            col = random.randint(0, state.board.col-1)
            if (col != pick_col or (col == pick_col and sha != pick_shape)):
                break
            
        #create new state, add new piece
        i = 0
        while (i < state.board.row and state.board[i, pick_col].shape == ShapeConstant.BLANK):
            i = i+1
        i = i-1

        # set current board
        place(state, n_player, sha , col)

        #tambah quota
        state.players[n_player].quota[sha] += 1

        return (col, sha)

    # UTILITY FUNCTION
    # Menghitung kesamaan bidak
    def count(self, listpiece, piece) -> Tuple[int, int]:
        n_shape, n_color = 0, 0

        for prior in GameConstant.WIN_PRIOR:
            for el in listpiece:

                shape_condition = (
                    prior == GameConstant.SHAPE
                    and el.shape == piece.shape
                )
                color_condition = (
                    prior == GameConstant.COLOR
                    and el.color == piece.color
                )

                if shape_condition:
                    n_shape += 1
                if color_condition:
                    n_color += 1

        return (n_shape, n_color)

    # Menghitung score        
    def scoring(self, state: State, window, piece, n_player) -> int:
        score = 0

        opp_piece = Piece(state.players[1-n_player].shape, state.players[1-n_player].color)
        blank_piece = Piece(ShapeConstant.BLANK, ColorConstant.BLACK)

        ## Shape
        if self.count(window, piece)[0] == 4:
            score += 200
        elif self.count(window, piece)[0] == 3 and self.count(window, blank_piece)[0] == 1:
            score += 10
        elif self.count(window, piece)[0] == 2 and self.count(window, blank_piece)[0] == 2:
            score += 4

        ## Color
        if self.count(window, piece)[1] == 4:
            score += 100
        elif self.count(window, piece)[1] == 3 and self.count(window, blank_piece)[1] == 1:
            score += 5
        elif self.count(window, piece)[1] == 2 and self.count(window, blank_piece)[1] == 2:
            score += 2

         ## Opponent
        if self.count(window, opp_piece)[0] == 3 and self.count(window, blank_piece)[0] == 1:
            score -= 200
        if self.count(window, opp_piece)[1] == 3 and self.count(window, blank_piece)[1] == 1:
            score -= 100
        if self.count(window, opp_piece)[0] == 2 and self.count(window, blank_piece)[0] == 2:
            score -= 10
        if self.count(window, opp_piece)[1] == 2 and self.count(window, blank_piece)[1] == 2:
            score -= 5
        
        return score
        
    def value(self, state: State, piece, n_player) -> int:
        score = 0

        opp_piece = Piece(state.players[1-n_player].shape, state.players[1-n_player].color)

        ## Score center column
        center_array = [state.board[i, state.board.col//2] for i in range(state.board.row)]
        center_count = self.count(center_array, piece)[0] * 2 + self.count(center_array, piece)[1]
        score += center_count * 3

        # Score Horizontal
        for r in range(state.board.row):
            row_array = [p for p in list(state.board[r,:])]
            for c in range(state.board.col-3):
                window = row_array[c:c+GameConstant.N_COMPONENT_STREAK]
                score += self.scoring(state, window, piece, n_player)

        # Score Vertical
        for c in range(state.board.col):
            col_array = [state.board[i,c] for i in range(state.board.row)]
            for r in range(state.board.row-3):
                window = col_array[r:r+GameConstant.N_COMPONENT_STREAK]
                score += self.scoring(state, window, piece, n_player)

        # Score diagonal
        for r in range(state.board.row-3):
            for c in range(state.board.col-3):
                window = [state.board[r+i, c+i] for i in range(GameConstant.N_COMPONENT_STREAK)]
                score += self.scoring(state, window, piece, n_player)
                
        for r in range(state.board.row-3):
            for c in range(state.board.col-3):
                window = [state.board[r+3-i, c+i] for i in range(GameConstant.N_COMPONENT_STREAK)]
                score += self.scoring(state, window, piece, n_player)

        return score

    # # UTILITY FUNCTION - 2
    # def score (self, prior : str, player: Player, count: int, isKita: int) -> int:
    #     if (isKita == 1): #score kita
    #         if (prior == GameConstant.SHAPE):
    #             if (count == 2):
    #                 return 8
    #             elif (count==3):
    #                 return 15
    #             elif (count==4):
    #                 return 1000
    #         else:
    #             if (count == 2):
    #                 return 2
    #             elif (count==3):
    #                 return 5
    #             elif (count==4):
    #                 return 1000
    #     else:   #score lawan                     
    #         if (count == 2):
    #             return -4
    #         elif (count==3):
    #             return -10
    #         elif (count==4):
    #             return -10000
    #     return 0


    # def streakscorehorizontal(self, state: State, player: Player, isKita: int) -> int:
    #     # ambil shape pemain dan color pemain
    #     shape = player.shape
    #     color = player.color

    #     #ambil row sama col
    #     row = state.board.row
    #     col = state.board.col
        
    #     # mendapatkan total value dilihat dari streak horizontal dari pemain dengan shape dan color
    #     value = 0
    #     for prior in GameConstant.WIN_PRIOR:
    #         for i in range (row):
    #             startpoint = 0 # start point (kolom)
    #             while (startpoint < col):
    #                 count = 0
    #                 j = startpoint
    #                 while (j < col and count <= 4):
    #                     shape_condition = (
    #                         prior == GameConstant.SHAPE
    #                         and state.board[i,j].shape != shape
    #                     )
    #                     color_condition = (
    #                         prior == GameConstant.COLOR
    #                         and state.board[i,j].color != color
    #                     )
    #                     if shape_condition or color_condition:
    #                         break
    #                     count+=1
    #                     j+=1  
    #                 value = value + self.score(prior, player, count, isKita)
    #                 startpoint = startpoint + count + 1
    #     return value
    
    # def streakscorevertical(self, state: State, player: Player, isKita: int) -> int:
    #      # ambil shape pemain dan color pemain
    #     shape = player.shape
    #     color = player.color

    #     #ambil row sama col
    #     row = state.board.row
    #     col = state.board.col

    #      # mendapatkan total value dilihat dari streak vertikal dari pemain dengan shape dan color
    #     value = 0
    #     for prior in GameConstant.WIN_PRIOR:
    #         for j in range (col):
    #             startpoint = 0 # start point (baris)
    #             while (startpoint < row and state.board[startpoint,j].shape != ShapeConstant.BLANK):
    #                 count = 0
    #                 i = startpoint
    #                 while (i < row and count <=4):
    #                     shape_condition = (
    #                         prior == GameConstant.SHAPE
    #                         and state.board[i,j].shape != shape
    #                     )
    #                     color_condition = (
    #                         prior == GameConstant.COLOR
    #                         and state.board[i,j].color != color
    #                     )
    #                     if shape_condition or color_condition:
    #                         break
    #                     count+=1
    #                     i+=1
    #                 value = value + self.score(prior, player, count, isKita)
    #                 startpoint = startpoint + count + 1
    #     return value

    # def streakscorediagonalpositive(self, state: State, player: Player, isKita: int) -> int:
    #     # ambil shape pemain dan color pemain
    #     shape = player.shape
    #     color = player.color

    #     #ambil row sama col
    #     row = state.board.row
    #     col = state.board.col
        
    #      # mendapatkan total value dilihat dari streak diagonal positif (m=1) dari pemain dengan shape dan color
    #     value = 0

    #     for prior in GameConstant.WIN_PRIOR:
    #         for idx in range (row-2, -1, -1):
    #             i = idx # start point
    #             j = 0
    #             while (i < row and j < col):
    #                 count = 0
    #                 while (count <= 4 and i < row and j < col):
    #                     shape_condition = (
    #                         prior == GameConstant.SHAPE
    #                         and state.board[i,j].shape != shape
    #                     )
    #                     color_condition = (
    #                         prior == GameConstant.COLOR
    #                         and state.board[i,j].color != color
    #                     )
    #                     if shape_condition or color_condition:
    #                         i+=1
    #                         j+=1
    #                         break
    #                     count+=1
    #                     i+=1
    #                     j+=1
    #                 value = value + self.score(prior, player, count, isKita)

    #         for idx in range (1, col-1):
    #             j = idx 
    #             i = 0
    #             while (i < row and j < col):
    #                 count = 0
    #                 while (count <= 4 and i < row and j < col):
    #                     shape_condition = (
    #                         prior == GameConstant.SHAPE
    #                         and state.board[i,j].shape != shape
    #                     )
    #                     color_condition = (
    #                         prior == GameConstant.COLOR
    #                         and state.board[i,j].color != color
    #                     )
    #                     if shape_condition or color_condition:
    #                         i+=1
    #                         j+=1
    #                         break
    #                     count+=1
    #                     i+=1
    #                     j+=1
    #                 value = value + self.score(prior, player, count, isKita)
                
    #     return value

    # def streakscorediagonalnegative(self, state: State, player: Player, isKita: int) -> int:
    #     # ambil shape pemain dan color pemain
    #     shape = player.shape
    #     color = player.color

    #     #ambil row sama col
    #     row = state.board.row
    #     col = state.board.col

    #      # mendapatkan total value dilihat dari streak diagonal negatif (m=-1) dari pemain dengan shape dan color
    #     value = 0

    #     for prior in GameConstant.WIN_PRIOR:
    #         for idx in range (1, row):
    #             i = idx # start point
    #             j = 0
    #             while (i >= 0 and j < col):
    #                 count = 0
    #                 while (count <= 4 and i >= 0 and j < col):
    #                     shape_condition = (
    #                         prior == GameConstant.SHAPE
    #                         and state.board[i,j].shape != shape
    #                     )
    #                     color_condition = (
    #                         prior == GameConstant.COLOR
    #                         and state.board[i,j].color != color
    #                     )
    #                     if shape_condition or color_condition:
    #                         i-=1
    #                         j+=1
    #                         break
    #                     count+=1
    #                     i-=1
    #                     j+=1
    #                 value = value + self.score(prior, shape, count, isKita)

    #         for idx in range (1, col-1):
    #             j = idx 
    #             i = row-1
    #             while (i >= 0 and j < col):
    #                 count = 0
    #                 while (count <= 4 and i >= 0 and j < col):
    #                     shape_condition = (
    #                         prior == GameConstant.SHAPE
    #                         and state.board[i,j].shape != shape
    #                     )
    #                     color_condition = (
    #                         prior == GameConstant.COLOR
    #                         and state.board[i,j].color != color
    #                     )
    #                     if shape_condition or color_condition:
    #                         i-=1
    #                         j+=1
    #                         break
    #                     count+=1
    #                     i-=1
    #                     j+=1
    #                 value = value + self.score(prior, shape, count, isKita)
                
    #     return value

    # def valuepemain (self, state: State, pemain: Player, isKita: int) -> int:
    #     horizontal = self.streakscorehorizontal(state, pemain, isKita)
    #     vertical = self.streakscorevertical(state, pemain, isKita)
    #     diagonalpositive = self.streakscorediagonalpositive(state, pemain, isKita)
    #     diagonalnegative = self.streakscorediagonalnegative(state, pemain, isKita)
    #     return  horizontal + vertical + diagonalpositive + diagonalnegative

    # def value(self, state: State, piece : Piece, n_player: int) -> int:
    #     myPlayer = state.players[n_player] #kita
    #     opponent = myPlayer = state.players[1-n_player] #lawan
    #     #1 : kita dan 0 = lawan
    #     return self.valuepemain(state, myPlayer, 1) - self.valuepemain(state, opponent, 0)


    # STOCHASTIC HILL CLIMBING
    def findHillClimbing (self, state: State, thinking_time: int, n_player:int) -> Tuple[str, str]:

        # setting variables
        time_now= time()

        current = copy.deepcopy(state)

        # generate one random state
        hasil_generate = self.Generate(current, n_player)

        col = hasil_generate[0]
        pick_shape = hasil_generate[1]

        piece = Piece(state.players[n_player].shape, state.players[n_player].color)

        # iterate - stochastic hill climbing
        i=0
        value_current = self.value(current, piece, n_player)
        # print("awal ",value_current)
        # print("kolom ",col)

        while (is_win(current.board) == None and (time()-time_now) < (thinking_time - 0.2) and i <1000):
            neighbor = copy.deepcopy(state)
            hasil_neigboard = self.getRandomNeighbor(neighbor, col, pick_shape, n_player)
            value_neighboard = self.value(neighbor, piece, n_player)
            if value_neighboard > value_current :
                #ubah kolom dan shape yang dipilih
                col = hasil_neigboard[0]
                pick_shape = hasil_neigboard[1]

                #ubah current jadi neighboard
                current = copy.deepcopy(neighbor)
                value_current = value_neighboard 
            i+=1

        # print(col, "dan", value_current)

        return (col, pick_shape)