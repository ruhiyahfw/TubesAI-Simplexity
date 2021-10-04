import random
from time import time

from src.constant import ShapeConstant, ColorConstant, GameConstant
from src.model import State, Piece

from typing import Tuple, List


class Minimax:
    def __init__(self):
        pass

    def find(self, state: State, n_player: int, thinking_time: float) -> Tuple[str, str]:
        self.thinking_time = time() + thinking_time

        best_movement = (random.randint(0, state.board.col), random.choice([ShapeConstant.CROSS, ShapeConstant.CIRCLE])) #minimax algorithm
        #print(n_player, self.value(state,Piece(state.players[n_player].shape, state.players[n_player].color),n_player))

        return best_movement

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
            
    def scoring(self, state: State, window, piece, n_player) -> int:
        score = 0

        opp_piece = Piece(state.players[1-n_player].shape, state.players[1-n_player].color)
        blank_piece = Piece(ShapeConstant.BLANK, ColorConstant.BLACK)

        ## SHAPE
        if self.count(window, piece)[0] == 4:
            score += 200
        elif self.count(window, piece)[0] == 3 and self.count(window, blank_piece)[0] == 1:
            score += 10
        elif self.count(window, piece)[0] == 2 and self.count(window, blank_piece)[0] == 2:
            score += 4

        ## COLOR
        if self.count(window, piece)[1] == 4:
            score += 100
        elif self.count(window, piece)[1] == 3 and self.count(window, blank_piece)[1] == 1:
            score += 5
        elif self.count(window, piece)[1] == 2 and self.count(window, blank_piece)[1] == 2:
            score += 2

        ## OPPONENT
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

        ## Score Horizontal
        for r in range(state.board.row):
            row_array = [p for p in list(state.board[r,:])]
            for c in range(state.board.col-3):
                window = row_array[c:c+GameConstant.N_COMPONENT_STREAK]
                score += self.scoring(state, window, piece, n_player)

        ## Score Vertical
        for c in range(state.board.col):
            col_array = [state.board[i,c] for i in range(state.board.row)]
            for r in range(state.board.row-3):
                window = col_array[r:r+GameConstant.N_COMPONENT_STREAK]
                score += self.scoring(state, window, piece, n_player)

        ## Score positive sloped diagonal
        for r in range(state.board.row-3):
            for c in range(state.board.col-3):
                window = [state.board[r+i, c+i] for i in range(GameConstant.N_COMPONENT_STREAK)]
                score += self.scoring(state, window, piece, n_player)
                
        ## Score negative sloped diagonal
        for r in range(state.board.row-3):
            for c in range(state.board.col-3):
                window = [state.board[r+3-i, c+i] for i in range(GameConstant.N_COMPONENT_STREAK)]
                score += self.scoring(state, window, piece, n_player)

        return score