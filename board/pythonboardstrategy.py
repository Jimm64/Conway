from board.boardstate import BoardState
from board.boardstate import UpdateStrategy
from board.boardstate import BoardStateTests
from screen.gldrawstate import OpenGLDrawState
import unittest

class StraightPythonUpdateStrategy(UpdateStrategy):
  """Strategy to update the board state using standard Python code."""

  def __init__(self, opengl_draw_state=None):

    self.opengl_draw_state = opengl_draw_state

  def update(self, board_state):
    """Update the board state."""

    if self.opengl_draw_state:
      self.opengl_draw_state.set_cell_dimensions(board_state.rows, board_state.cols)
    self.update_cells(board_state.new_cells, board_state.cells, board_state.rows, 
      board_state.cols)

  def update_cells(self, new_cells, cells, num_rows, num_cols):
    """Update the cells on the board."""

    # Keep any live cell with 2 or 3 neighbors.
    keep_cell_on_neighbor_counts = (0, 0, 1, 1, 0, 0, 0, 0, 0)

    # Add a ell on any space with three live neighbors.
    add_cell_on_neighbor_counts =  (0, 0, 0, 1, 0, 0, 0, 0, 0)

    size_of_row = num_cols + 2

    for x in range (num_cols * num_rows):

      # The board state is bordered by empty cells, so that we don't have
      # to account for neighbor locations being out of bounds.
      # But we do have to account for the empty cells when determining
      # which cell in our (one-dimensional) array is the current one.
      cell_array_index = (x // num_cols + 1) * (num_cols + 2) + (x % num_cols + 1)

      # Count neighbors.
      cell_neighbor_count  = cells[cell_array_index - size_of_row - 1]
      cell_neighbor_count += cells[cell_array_index - size_of_row + 0]
      cell_neighbor_count += cells[cell_array_index - size_of_row + 1]

      cell_neighbor_count += cells[cell_array_index - 1]
      cell_neighbor_count += cells[cell_array_index + 1]

      cell_neighbor_count += cells[cell_array_index + size_of_row - 1]
      cell_neighbor_count += cells[cell_array_index + size_of_row + 0]
      cell_neighbor_count += cells[cell_array_index + size_of_row + 1]

      # Set whether the cell is alive or dead based on
      # neighbor count and current state.
      new_cells[cell_array_index] = cells[cell_array_index]
      new_cells[cell_array_index] &= keep_cell_on_neighbor_counts[cell_neighbor_count]
      new_cells[cell_array_index] |= add_cell_on_neighbor_counts[cell_neighbor_count]

      if self.opengl_draw_state:
        # Likewise set what color the cell should now be.
        cell_color_index = 3 * 4 * x
        for corner in range(0, 4):
          self.opengl_draw_state.get_opengl_cell_vertex_colors()[
            cell_color_index + corner * 3 + 2] = 127 * new_cells[cell_array_index]


class StraightPythonStrategyUpdateTests(BoardStateTests, unittest.TestCase):
  """Run BoardStateTests for the straight Python update strategy."""

  def setUp(self):
    self.opengl_draw_state = OpenGLDrawState()
    self.strategy=StraightPythonUpdateStrategy(opengl_draw_state=self.opengl_draw_state)

if __name__ == '__main__':
    unittest.main()
