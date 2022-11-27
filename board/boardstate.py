import random
import unittest
import numpy
from abc import ABC, abstractmethod

class UpdateStrategy(ABC):
  """
    Object for implementing a given way to update the board state.
  """

  @abstractmethod
  def update(self, board_state):
    pass

class BoardObserver(ABC):
  """
    Object that can be registered with the BoardState via
    BoardState.add_observer, to be called when the state changes.
  """

  @abstractmethod
  def on_update(self, board_state):
    """Called whenver the board state changes."""
    pass

class BoardState:
    """Stores the state of the cells (alive or dead) on the board."""

    def update(self, strategy):
      """
        Perform one iteration of the game, updating which cells
        are alive or dead.
      """
      
      # Delegate to whatever strategy was chosen.
      strategy.update(self)

      # Swap the cell arrays.
      self.new_cells, self.cells = self.cells, self.new_cells

      # Notify observers
      for observer in self.observers:
        observer.on_update(self)

    def add_observer(self, observer):
      """Add an observer so that it receives notification of state updates."""
      self.observers.append(observer)

    def __init__(self, rows, cols):

      self.observers = []
      self.rows = rows
      self.cols = cols

      # Use numpy arrays to support updating via CUDA (though they also
      # work with straight Python)
      self.cells = numpy.zeros((rows+2) * (cols+2),dtype=numpy.uint8)
      self.new_cells = numpy.zeros((rows+2) * (cols+2),dtype=numpy.uint8)

    def from_string(string):
      """
        Create a BoardState with state specified by a string which uses:
        - 'X' as a live cell
        - '-' as a dead cell
        - '\\n' (newline) as the end of a row

        Example:

          board_state = BoardState.from_string(
            "XXX\\n" +
            "---\\n" +
            "---")
      """

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
      """Set board state to a random set of live/dead cells."""

      for row in range(0, self.rows):
        for col in range (0, self.cols):
          if random.randint(0,1):
            self.set_cell(row, col)
          else:
            self.clear_cell(row, col)

      return

    def cell_state(self, row, col):
      """ Returns True if the cell at the given location is alive, False otherwise."""

      return False if self.cells[(row+1) * (self.cols+2) + (col+1)] == 0 else True

    def set_cell(self, row, col):
      """Set a cell as alive."""

      self.cells[(row+1) * (self.cols+2) + (col+1)] = 1

    def clear_cell(self, row, col):
      """Set a cell as dead."""

      self.cells[(row+1) * (self.cols+2) + (col+1)] = 0

    def to_string(self):
      """
        Return the state of the board in the form of a string which uses:
        - 'X' as a live cell
        - '-' as a dead cell
        - '\\n' (newline) as the end of a row
      """

      board_string = ""
      for row in range(0, self.rows):
        for col in range(0, self.cols):
          board_string += "X" if self.cell_state(row, col) else "-"
        if row < self.rows - 1:
          board_string += "\n" 
      return board_string


class BoardStateTests():
  """
    BoardState unit tests.

    Intended for objects that define a strategy for upating the board.  The
    strategy object should create a unit test class that inherits this object
    and unittest.TestCase, and then specifies the strategy to test, e.g.:

      class SomeUpdateStrategyTests(BoardStateTests, unittest.TestCase):

        def setUp(self):
          self.strategy=SomeUpdateStrategy()

    These tests will then be run using that update strategy.
  """

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
