import random
from time import time

from src.constant import ShapeConstant, ColorConstant, GameConstant
from src.utility import check_streak
from src.model import State, Piece

from typing import Tuple, List


class Minimax:
    def __init__(self):
        pass

    def find(self, state: State, n_player: int, thinking_time: float) -> Tuple[str, str]:
        self.thinking_time = time() + thinking_time

        best_movement = (random.randint(0, state.board.col), random.choice([ShapeConstant.CROSS, ShapeConstant.CIRCLE])) #minimax algorithm
        print(self.value(state,Piece(state.players[n_player].shape, state.players[n_player].color)))

        return best_movement

    def count(self, listpiece, piece) -> int:
        n = 0
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
                    n += 2
                if color_condition:
                    n += 1
        return n
            
    def scoring(self, state: State, window, piece) -> int:
        score = 0
        opp_piece = state.players[1]
        if piece == state.players[1]:
            opp_piece = state.players[0]

        blank_piece = Piece(ShapeConstant.BLANK, ColorConstant.BLACK)

        if self.count(window, piece) == 4:
            score += 100
        elif self.count(window, piece) == 3 and self.count(window, blank_piece) == 1:
            score += 5
        elif self.count(window, piece) == 2 and self.count(window, blank_piece) == 2:
            score += 2

        if self.count(window, opp_piece) == 3 and self.count(window, blank_piece) == 1:
            score -= 4

        return score
        
    def value(self, state: State, piece) -> int:
        score = 0

        ## Score center column
        center_array = [p for p in list(state.board[:, state.board.col//2])]
        center_count = self.count(center_array, piece)
        score += center_count * 3

        ## Score Horizontal
        for r in range(state.board.row):
            row_array = [p for p in list(state.board[r,:])]
            for c in range(state.board.col-3):
                window = row_array[c:c+GameConstant.N_COMPONENT_STREAK]
                score += self.scoring(state, window, piece)

        ## Score Vertical
        for c in range(state.board.col-1):
            col_array = [p for p in list(state.board[:,c])]
            for r in range(state.board.row-3):
                window = col_array[r:r+GameConstant.N_COMPONENT_STREAK]
                score += self.scoring(state, window, piece)

        ## Score positive sloped diagonal
        for r in range(state.board.row-3):
            for c in range(state.board.col-3):
                window = [state.board[r+i, c+i] for i in range(GameConstant.N_COMPONENT_STREAK)]
                score += self.scoring(state, window, piece)
                
        ## Score negative sloped diagonal
        for r in range(state.board.row-3):
            for c in range(state.board.col-3):
                window = [state.board[r+3-i, c+i] for i in range(GameConstant.N_COMPONENT_STREAK)]
                score += self.scoring(state, window, piece)

        return score