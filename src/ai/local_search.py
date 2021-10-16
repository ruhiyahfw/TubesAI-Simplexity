import random
from time import time
import threading
import _thread as thread

from src.constant import ShapeConstant, GameConstant
from src.model import State, Board, Player, Piece
from src.utility import is_out, check_streak

from typing import Tuple, List

class Value:
    WIN = 1000
    LOSE = -1000


class LocalSearch:
    def __init__(self):
       pass

    def find(self, state: State, n_player: int, thinking_time: float) -> Tuple[str, str]:
        self.thinking_time = time() + thinking_time
        self.player = state.players[(state.round-1)%2]

        # best_movement = (random.randint(0, state.board.col), random.choice([ShapeConstant.CROSS, ShapeConstant.CIRCLE])) #minimax algorithm

        # Local search with thinking time
        best_movement = self.findHillClimbing(state, thinking_time)
            
        return best_movement

    def quit_function(self,fn_name):
        sys.stderr.flush()
        thread.interrupt_main()

    def Generate(self, state: State) -> Board :
        #choose column randomly
        self.col = random.randint(0, state.board.col)
        if self.player.quota == 3 and self.player.quota > 0:
            self.pick_shape = random.choice([ShapeConstant.CROSS, ShapeConstant.CIRCLE])
        else:
            self.pick_shape = self.player.shape

        #create new state, add new piece
        i = 0
        while (i < state.board.row and state.board[i, self.col].shape == ShapeConstant.BLANK):
            i = i+1
        i = i-1
        
        newboard = state.board # red flag
        piece = Piece(self.pick_shape, self.player.color)
        newboard.set_piece(i, self.col, piece)

        return newboard

    def getRandomNeighbor (self, state: State, current: Board) -> Board :
        #choose shape and column randomly
        while True:
            sha = random.choice([ShapeConstant.CROSS, ShapeConstant.CIRCLE])
            col = random.randint(0, state.board.col)
            if (col != self.col or (col == self.col and sha != self.pick_shape)):
                break
            
        #create new state, add new piece
        i = 0
        while (i < state.board.row and state.board.board[i, self.col].shape == ShapeConstant.BLANK):
            i = i+1
        i = i-1

        newneighbor = state.board
        piece = Piece(sha, self.player.color)
        newneighbor.set_piece(i, self.col, piece)

        return newneighbor

    def score (self, prior : GameConstant, shape: str, count: int) -> int:
        if (shape == self.player.shape):
            if (prior == GameConstant.SHAPE):
                if (count == 2):
                    return 4
                elif (count==3):
                    return 10
                elif (count==4):
                    return 1000
            else:
                if (count == 2):
                    return 2
                elif (count==3):
                    return 5
                elif (count==4):
                    return 1000
        else:                        
            if (prior == GameConstant.SHAPE):
                if (count == 2):
                    return -4
                elif (count==3):
                    return -10
                elif (count==4):
                    return -10000

    def streakscorehorizontal(self, board: Board, shape:str, color:str) -> int:
        # mendapatkan total value dilihat dari streak horizontal dari pemain dengan shape dan color
        value = 0
        for prior in GameConstant.WIN_PRIOR:
            for i in range (board.row):
                startpoint = 0 # start point
                while (startpoint < board.col and board[i,startpoint] != ShapeConstant.BLANK):
                    count = 0
                    for j in range (startpoint, startpoint+5):
                        shape_condition = (
                            prior == GameConstant.SHAPE
                            and board.board[i,j].shape != shape
                        )
                        color_condition = (
                            prior == GameConstant.COLOR
                            and board.board[i,j].color != color
                        )
                        if shape_condition or color_condition:
                            break
                        count+=1
                    value = value + self.score(prior, shape, count)
                    startpoint = startpoint + count + 1
        return value
    
    def streakscorevertical(self, board: Board, shape: str, color: str) -> int:
         # mendapatkan total value dilihat dari streak vertikal dari pemain dengan shape dan color
        value = 0
        for prior in GameConstant.WIN_PRIOR:
            for j in range (board.col):
                startpoint = 0 # start point
                while (startpoint < board.row and board[startpoint,j] != ShapeConstant.BLANK):
                    count = 0
                    for i in range (startpoint, startpoint+5):
                        shape_condition = (
                            prior == GameConstant.SHAPE
                            and board.board[i,j].shape != shape
                        )
                        color_condition = (
                            prior == GameConstant.COLOR
                            and board.board[i,j].color != color
                        )
                        if shape_condition or color_condition:
                            break
                        count+=1
                    value = value + self.score(prior, shape, count)
                    startpoint = startpoint + count + 1
        return value

    def streakscorediagonalpositive(self, board: Board, shape: str, color: str) -> int:
         # mendapatkan total value dilihat dari streak diagonal positif (m=1) dari pemain dengan shape dan color
        value = 0

        for prior in GameConstant.WIN_PRIOR:
            for idx in range (board.row-1, -1, -1):
                i = idx # start point
                j = 0
                while (i < board.row and j < board.col):
                    count = 0
                    while (count <= 4 and i < board.row and j < board.col):
                        shape_condition = (
                            prior == GameConstant.SHAPE
                            and board.board[i,j].shape != shape
                        )
                        color_condition = (
                            prior == GameConstant.COLOR
                            and board.board[i,j].color != color
                        )
                        if shape_condition or color_condition:
                            i+=1
                            j+=1
                            break
                        count+=1
                        i+=1
                        j+=1
                    value = value + self.score(prior, shape, count)
                    i+=1
                    j+=1

            for idx in range (1, board.col-1):
                j = idx 
                i = 0
                while (i < board.row and j < board.col):
                    count = 0
                    while (count <= 4 and i < board.row and j < board.col):
                        shape_condition = (
                            prior == GameConstant.SHAPE
                            and board.board[i,j].shape != shape
                        )
                        color_condition = (
                            prior == GameConstant.COLOR
                            and board.board[i,j].color != color
                        )
                        if shape_condition or color_condition:
                            i+=1
                            j+=1
                            break
                        count+=1
                        i+=1
                        j+=1
                    value = value + self.score(prior, shape, count)
                    i+=1
                    j+=1
                
        return value

    def streakscorediagonalnegative(self, board: Board, shape: str, color: str) -> int:
         # mendapatkan total value dilihat dari streak diagonal negatif (m=-1) dari pemain dengan shape dan color
        value = 0

        for prior in GameConstant.WIN_PRIOR:
            for idx in range (1, board.row):
                i = idx # start point
                j = 0
                while (i >= 0 and j < board.col):
                    count = 0
                    while (count <= 4 and i >= 0 and j < board.col):
                        shape_condition = (
                            prior == GameConstant.SHAPE
                            and board.board[i,j].shape != shape
                        )
                        color_condition = (
                            prior == GameConstant.COLOR
                            and board.board[i,j].color != color
                        )
                        if shape_condition or color_condition:
                            i-=1
                            j+=1
                            break
                        count+=1
                        i-=1
                        j+=1
                    value = value + self.score(prior, shape, count)
                    i-=1
                    j+=1

            for idx in range (1, board.col-1):
                j = idx 
                i = board.row-1
                while (i >= 0 and j < board.col):
                    count = 0
                    while (count <= 4 and i >= 0 and j < board.col):
                        shape_condition = (
                            prior == GameConstant.SHAPE
                            and board.board[i,j].shape != shape
                        )
                        color_condition = (
                            prior == GameConstant.COLOR
                            and board.board[i,j].color != color
                        )
                        if shape_condition or color_condition:
                            i-=1
                            j+=1
                            break
                        count+=1
                        i-=1
                        j+=1
                    value = value + self.score(prior, shape, count)
                    i-=1
                    j+=1
                
        return value

    def valuepemain (self, board: Board, pemain: Player) -> int:
        horizontal = self.streakscorehorizontal(board,pemain.shape, pemain.color)
        vertical = self.streakscorevertical(board,pemain.shape, pemain.color)
        diagonalpositive = self.streakscorediagonalpositive(board,pemain.shape, pemain.color)
        diagonalnegative = self.streakscorediagonalnegative(board,pemain.shape, pemain.color)
        return  horizontal + vertical + diagonalpositive + diagonalnegative

    def value(self, board:Board, state : State) -> int:
        pemain1 = self.player #kita
        pemain2 = state.players[(state.round)%2] #lawan
        return self.valuepemain(board, pemain1) - self.valuepemain(board, pemain2)

    def getColumnShape(self): 
        return (self.col, self.pick_shape)

    def findHillClimbing (self, state: State, thinking_time: int) -> Tuple[str, str]:

        timer = threading.Timer(thinking_time-0.2, self.quit_function)
        timer.start()

        self.player = state.players[(state.round-1)%2]

        current = self.Generate(state)
        try:
            while (self.value(current, state) < Value.WIN) :
                neighbor = self.getRandomNeighbor(state, current)
                if self.value(neighbor, state) > self.value(current, state) :
                    current = neighbor
        finally:
            timer.cancel()

        return (self.getColumnShape())


    






    