import random
from time import time

from src.constant import ShapeConstant, GameConstant
from src.model import State, Board, Player, Piece
from src.utility import is_out

from typing import Tuple, List

class Value:
    WIN = 1000
    LOSE = -1000


class LocalSearch:
    def __init__(self, player: Player):
        self.player = player

    def find(self, state: State, n_player: int, thinking_time: float) -> Tuple[str, str]:
        self.thinking_time = time() + thinking_time

        best_movement = (random.randint(0, state.board.col), random.choice([ShapeConstant.CROSS, ShapeConstant.CIRCLE])) #minimax algorithm

        return best_movement

    def Generate(self, state: State) -> Board :
        #choose shape and column randomly
        self.shape = random.choice([ShapeConstant.CROSS, ShapeConstant.CIRCLE])
        self.col = random.randint(0, state.board.col)

        #create new state, add new piece
        i = 0
        while (i < state.board.row and state.board[i, self.col].shape == ShapeConstant.BLANK):
            i = i+1
        i = i-1
        
        newboard = state.board # red flag
        piece = Piece(self.shape, self.player.color)
        newboard.set_piece(i, self.col, piece)

        return newboard

    def getRandomNeighbor (self, state: State, current: Board) -> Board :
        #choose shape and column randomly
        while True:
            sha = random.choice([ShapeConstant.CROSS, ShapeConstant.CIRCLE])
            col = random.randint(0, state.board.col)
            if (col != self.col or (col == self.col and sha != self.player.shape)):
                break
            
        #create new state, add new piece
        i = 0
        while (i < state.board.row and state.board[i, self.col].shape == ShapeConstant.BLANK):
            i = i+1
        i = i-1

        newneighbor = state.board
        piece = Piece(sha, self.player.color)
        newneighbor.set_piece(i, self.col, piece)

        return newneighbor

    def one_value(self, board: Board, row: int, col: int, n: int) -> int:
        piece = board[row, col]
        if piece.shape == ShapeConstant.BLANK:
            return None

        streak_way = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

        for prior in GameConstant.WIN_PRIOR:
            mark = 0
            for row_ax, col_ax in streak_way:
                row_ = row + row_ax
                col_ = col + col_ax
                for _ in range(n - 1):
                    # tidak ada streak
                    if is_out(board, row_, col_):
                        mark = 0
                        break
                    
                    # kalau ada
                    shape_condition = (
                        prior == GameConstant.SHAPE 
                        and piece.shape != board[row_, col_].shape
                    )
                    color_condition = (
                        prior == GameConstant.COLOR 
                        and piece.color != board[row_, col_].color
                    )
                    if shape_condition or color_condition:
                        mark = 0
                        break

                    row_ += row_ax
                    col_ += col_ax
                    mark += 1

                if mark == GameConstant.n - 1:
                    player_set = [
                        (GameConstant.PLAYER1_SHAPE, GameConstant.PLAYER1_COLOR),
                        (GameConstant.PLAYER2_SHAPE, GameConstant.PLAYER2_COLOR),
                    ]
                    for player in player_set:
                        if prior == GameConstant.SHAPE:
                            if piece.shape == player[0]:
                                return (prior, player)
                                
                        elif prior == GameConstant.COLOR:
                            if piece.color == player[1]:
                                return (prior, player)


    def is_player_win(self, board: Board) -> Tuple[str, str]:
        """
        [DESC]
            Function to check if player won
        [PARAMS]
            board: Board -> current board
        [RETURN]
            None if there is no streak
            Tuple[shape, color] match with player set if there is a streak
        """
        temp_win = None
        for row in range(board.row):
            for col in range(board.col):
                checked = check_streak(board, row, col)
                if checked:
                    if checked[0] == GameConstant.WIN_PRIOR[0]:
                        return checked[1]
                    else:
                        temp_win = checked[1]
        return temp_win


    def value (self, board: Board) -> int:
        
        return 0

    def getColumnShape(self): 
        return (self.col, self.player.shape)

    def findHillClimbing (self, state: State, n_player: int, thinking_time: float) -> Tuple[str, str]:
        self.player = state.players[n_player]

        current = self.Generate(state)
        while (self.value(current)< Value.WIN) : #ganti jadi !is_win
            neighbor = self.getRandomNeighbor(state, current)
            if self.value(neighbor) > self.value(current) :
                current = neighbor
        return (self.getColumnShape())


    






    