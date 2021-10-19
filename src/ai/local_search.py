from typing import Tuple, List

import random
from time import time
import threading
import _thread as thread
import copy

from src.constant import *
from src.model import State, Board, Player, Piece
from src.utility import is_full, is_out, check_streak, place, is_win


class LocalSearch:
    def __init__(self):
        pass

    def find(self, state: State, n_player: int, thinking_time: float) -> Tuple[str, str]:
        self.thinking_time = time() + thinking_time
        self.player = state.players[(state.round-1)%2]

        # best_movement = (random.randint(0, state.board.col), random.choice([ShapeConstant.CROSS, ShapeConstant.CIRCLE])) #minimax algorithm

        # Local search with thinking time
        best_movement = self.findHillClimbing(state, thinking_time, n_player)
            
        return best_movement

    def Generate(self, state: State, n_player: int) -> Tuple[int, str] :
        #choose column randomly
        col = random.randint(0, state.board.col-1)
        myPlayer = state.players[n_player]

        # choose shape
        if myPlayer.quota == 3 and myPlayer.quota > 0:
            pick_shape = random.choice([ShapeConstant.CROSS, ShapeConstant.CIRCLE])
        else:
            pick_shape = myPlayer.shape

        #create new state, add new piece
        i = 0
        while (i < state.board.row and state.board[i, col].shape == ShapeConstant.BLANK):
            i = i+1
        i = i-1
        
        # set current board
        place(state, n_player, pick_shape , col)

        return (col, pick_shape)

    def getRandomNeighbor (self, state: State, pick_col: int, pick_shape: str, n_player: int) -> Tuple[int, str] :
        #choose shape and column randomly
        while True:
            # choose shape
            myPlayer = state.players[n_player]
            if myPlayer.quota == 3 and myPlayer.quota > 0:
                sha = random.choice([ShapeConstant.CROSS, ShapeConstant.CIRCLE])
            else:
                sha = myPlayer.shape

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

    def findHillClimbing (self, state: State, thinking_time: int, n_player:int) -> Tuple[str, str]:

        # setting variables
        time_now= time()

        current = copy.deepcopy(state)
        neighbor = copy.deepcopy(state)

        # generate one random state
        hasil_generate = self.Generate(current, n_player)

        col = hasil_generate[0]
        pick_shape = hasil_generate[1]

        piece = Piece(state.players[n_player].shape, state.players[n_player].color)

        # iterate - stochastic hill climbing
        i=0
        while (is_win(neighbor.board) == None and (time()-time_now) < 2.8):
            hasil_neigboard = self.getRandomNeighbor(neighbor, col, pick_shape, n_player)
            if self.value(neighbor, piece, n_player) > self.value(current, piece, n_player) :
                col = hasil_neigboard[0]
                pick_shape = hasil_neigboard[1]
            i+=1

        return (col, pick_shape)