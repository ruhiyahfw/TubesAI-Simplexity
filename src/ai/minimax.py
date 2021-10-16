import random
import numpy as np
import copy
import sys
import threading
import _thread as thread
from time import time

from src.constant import ShapeConstant, ColorConstant, GameConstant
from src.utility import check_streak, is_win, place
from src.model import State, Piece
from src.model.piece import Piece

from typing import Tuple, List


class Minimax:
    def __init__(self):
        pass

    def find(self, state: State, n_player: int, thinking_time: float) -> Tuple[str, str]:
        self.thinking_time = time() + thinking_time

        # Minimax with thinking time
        timer = threading.Timer(thinking_time-0.2, self.quit_function, args=[self.alpha_beta_search])
        timer.start()
        try:
            minimax = self.alpha_beta_search(state, n_player, 3, -np.inf, np.inf, True) # Minimax 3-ply
            best_movement = (minimax[1], minimax[0])

        # Alternatif
        except KeyboardInterrupt:
            best_movement = self.InstantMinimax(state, n_player)

        finally:
            timer.cancel()
            best_movement = self.InstantMinimax(state, n_player)

        return best_movement

    def quit_function(self,fn_name):
        sys.stderr.flush()
        thread.interrupt_main()

    def InstantMinimax(self, state, n_player):
        minimax = self.alpha_beta_search(state, n_player, 1, -np.inf, np.inf, True)
        return (minimax[1], minimax[0])

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
            score -= 8
        if self.count(window, opp_piece)[1] == 3 and self.count(window, blank_piece)[1] == 1:
            score -= 4

        return score
        
    def value(self, state: State, piece, n_player) -> int:
        score = 0

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
    

    # MINIMAX ALGORITHM
    
    def is_location_valid(self, state : State, col):
        # tanda bidak kosong adalah board[i][j] = Piece(Black, Black)
        return state.board[0, col].shape == ShapeConstant.BLANK
    
    def get_location_valid(self, cur_state : State):
        valid_local = []

        for col in range(cur_state.board.col):
            if self.is_location_valid(cur_state, col):
                valid_local.append(col)

        return valid_local
    
    def is_terminal_node(self, cur_state: State):
        return (is_win(cur_state.board) or (len(self.get_location_valid(cur_state)) == 0) )
    
    def get_next_open_row(self, state: State, col):
        for row in range(state.board.row):
            if(state.board[row, col] == Piece(ShapeConstant.BLANK, ColorConstant.BLACK)):
                return row
    
    def alpha_beta_search(self, cur_state : State, n_player, depth, alpha, beta, maximizing) -> Tuple[str, int, int]:
        # return (shape : str, col : int, val : int)
        is_terminal = self.is_terminal_node(cur_state)
        valid_locations = self.get_location_valid(cur_state)

        if depth == 0 or is_terminal:
            win = is_win(cur_state.board) # [shape, color]
            if win: # pemain menang, lawan menang, game selesai (no more valid move)
                # ini belum termasuk kondisi menang dengan warna ?? jawab: udah ada dalam is_win
                if (win[0] == cur_state.players[n_player].shape): # yang menang AI
                    return (None, None, 10000000000)
                elif (win[0] == cur_state.players[1-n_player].shape): # yang menang player
                    return (None, None, -10000000000)
                else:
                    return (None,None, 0)
            else:
                piece = Piece(cur_state.players[n_player].shape, cur_state.players[n_player].color) # piece = (shape,color) dari ai
                return (None, None, self.value(cur_state, piece, n_player)) 
        
        if maximizing:
            v = -np.inf
            column = random.choice(valid_locations)

            for shp in [cur_state.players[n_player].shape, cur_state.players[1-n_player].shape]:
                for col in valid_locations:

                    row = self.get_next_open_row(cur_state, col)
                    state_temp = copy.deepcopy(cur_state)
                    place(state_temp, n_player, shp, col) # misal ai = 1, player = 0
                    new_score = self.alpha_beta_search(state_temp, n_player, depth-1, alpha, beta, False)[2] # value
                    
                    if(new_score >= v):
                        v = new_score
                        column = col
                        shape = shp
                    alpha = max(alpha, v)
                    # Pruning
                    if alpha >= beta:
                        break

            return shape, column, v #cara return shape col dan val



        else: # minimizing
            v = np.inf
            column = random.choice(valid_locations)

            for shp in [cur_state.players[1-n_player].shape, cur_state.players[n_player].shape]:
                for col in valid_locations:

                    row = self.get_next_open_row(cur_state, col)
                    state_temp = copy.deepcopy(cur_state)
                    place(state_temp, 1-n_player, shp, col) # misal ai = 1, player = 0
                    new_score = self.alpha_beta_search(state_temp, n_player, depth-1, alpha, beta, True)[2] # value

                    if(new_score <= v):
                        v = new_score
                        column = col
                        shape = shp
                    beta = min(beta, v)
                    # Pruning
                    if(alpha >= beta):
                        break

            return shape, column, v