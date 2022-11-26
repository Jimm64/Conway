import random
import unittest
import numpy
from abc import ABC, abstractmethod

class UpdateStrategy(ABC):

  @abstractmethod
  def update(self, board_state):
      pass

class BoardObserver(ABC):

  @abstractmethod
  def on_update(self, board_state):
    pass

class BoardState:

    def update(self, strategy):

        strategy.update(self)
        self.new_cells, self.cells = self.cells, self.new_cells

        for observer in self.observers:
            observer.on_update(self)

    def add_observer(self, observer):
        self.observers.append(observer)

    def __init__(self, rows, cols):

        self.observers = []
        self.rows = rows
        self.cols = cols
        self.cells = numpy.zeros((rows+2) * (cols+2),dtype=numpy.uint8)
        self.new_cells = numpy.zeros((rows+2) * (cols+2),dtype=numpy.uint8)

    def from_string(string):

        row_strings = string.split("\n")
        rows = len(row_strings)
        cols = len(row_strings[0])

        for row in range(0, rows):
            if len(row_strings[row]) != cols:
                raise Exception("Row lengths are not equal")
        
        board_state = BoardState(rows, cols)

        for row in range(0, rows):
            for col in range (0, cols):
                if row_strings[row][col] == "X":
                    board_state.set_cell(row, col)
                elif row_strings[row][col] != "-":
                    raise Exception("Unrecognized character in board string")

        return board_state


    def randomize_state(self):
        for row in range(0, self.rows):
            for col in range (0, self.cols):
                if random.randint(0,1):
                    self.set_cell(row, col)
                else:
                    self.clear_cell(row, col)

        return

    def cellState(self, row, col):
        return False if self.cells[(row+1) * (self.cols+2) + (col+1)] == 0 else True

    def set_cell(self, row, col):
        self.cells[(row+1) * (self.cols+2) + (col+1)] = 1
        return

    def clear_cell(self, row, col):
        self.cells[(row+1) * (self.cols+2) + (col+1)] = 0
        return

    def to_string(self):
        board_string = ""
        for row in range(0, self.rows):
            for col in range(0, self.cols):
                board_string += "X" if self.cellState(row, col) else "-"
            if row < self.rows - 1:
                board_string += "\n" 
        return board_string


class BoardStateTests():

    def test_board_can_init_from_string(self):
        board_state = BoardState.from_string(
                "X-X\n" +
                "-X-\n" +
                "X-X")

        self.assertEqual(board_state.to_string(),
                "X-X\n" +
                "-X-\n" +
                "X-X")


    def test_all_cells_are_false_at_start(self):
        rows = 3
        cols = 4
        board_state = BoardState(rows=rows, cols=cols)

        self.assertEqual(board_state.to_string(),
                "----\n" +
                "----\n" +
                "----")

    def test_update_kills_cell_with_no_neighbors(self):
        board_state = BoardState(rows=3, cols=3)
        board_state.set_cell(0, 0)

        self.assertEqual(board_state.to_string(),
                "X--\n" +
                "---\n" +
                "---")

        board_state.update(strategy=self.strategy)

        self.assertEqual(board_state.to_string(),
                "---\n" +
                "---\n" +
                "---")


    def test_update_keeps_alive_cell_with_three_neighbors(self):

        board_state = BoardState.from_string(
                "XX-\n" +
                "XX-\n" +
                "---")

        board_state.update(strategy=self.strategy)

        self.assertEqual(board_state.to_string(),
                "XX-\n" +
                "XX-\n" +
                "---")



    def test_update_sets_cell_with_three_neighbors(self):

        board_state = BoardState.from_string(
                "XXX\n" +
                "---\n" +
                "---")

        board_state.update(strategy=self.strategy)

        self.assertEqual(board_state.to_string(),
                "-X-\n" +
                "-X-\n" +
                "---")

    def test_update_kills_cell_with_four_neighbors(self):

        board_state = BoardState.from_string(
                "-X-\n" +
                "XXX\n" +
                "-X-")

        board_state.update(strategy=self.strategy)

        self.assertEqual(board_state.to_string(),
                "XXX\n" +
                "X-X\n" +
                "XXX")

if __name__ == '__main__':
    unittest.main()
