from boardstate import UpdateStrategy
from boardstate import BoardStateTests
import unittest

class StraightPythonUpdateStrategy(UpdateStrategy):

  def __init__(self, opengl_draw_state=None):
    self.opengl_draw_state = opengl_draw_state

  def update(self, board_state):

    if self.opengl_draw_state:
      self.opengl_draw_state.set_cell_dimensions(board_state.rows, board_state.cols)
    self.update_cells(board_state.new_cells, board_state.cells, 
        board_state.rows, board_state.cols)

  def update_cells(self, new_cells, cells, max_rows, max_cols):

    size_of_row = max_cols + 2

    for x in range (max_cols * max_rows):

        cell_array_index = (x // max_cols + 1) * (max_cols + 2) + (x % max_cols + 1)

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
        if cell_neighbor_count < 2 or cell_neighbor_count > 3:
            new_cells[cell_array_index] = 0
        elif cell_neighbor_count == 3:
            new_cells[cell_array_index] = 1
        else:
            new_cells[cell_array_index] = cells[cell_array_index]

        if self.opengl_draw_state:
            # Likewise set what color the cell should now be.
            cell_color_index = 3 * 4 * x
            for corner in range(0, 4):
              self.opengl_draw_state.get_opengl_cell_vertex_colors()[
                  cell_color_index + corner * 3 + 2] = new_cells[cell_array_index]


class StraightPythonStrategyUpdateTests(BoardStateTests, unittest.TestCase):

    def setUp(self):
        self.strategy=StraightPythonUpdateStrategy()

if __name__ == '__main__':
    unittest.main()
