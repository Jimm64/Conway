from boardstate import UpdateStrategy
from boardstate import BoardStateTests
import unittest

class StraightPythonUpdateStrategy(UpdateStrategy):

  def update(self, board_state):

    self.update_cells(board_state.new_cells, board_state.cells, 
        board_state.get_opengl_cell_vertex_colors(),
        board_state.rows, board_state.cols)

  def update_cells(self, new_cells, cells, cell_colors, max_rows, max_cols):

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
        cell_color = 0.0
        if cell_neighbor_count < 2 or cell_neighbor_count > 3:
            new_cells[cell_array_index] = 0
        elif cell_neighbor_count == 3:
            new_cells[cell_array_index] = 1
            cell_color = 1.0
        else:
            new_cells[cell_array_index] = cells[cell_array_index]
            if new_cells[cell_array_index] == 1:
              cell_color = 1.0

        # Likewise set what color the cell should now be.
        cell_color_index = 3 * 4 * x
        for corner in range(0, 4):
          cell_colors[cell_color_index + corner * 3 + 2] = cell_color


class StraightPythonStrategyUpdateTests(BoardStateTests, unittest.TestCase):

    def setUp(self):
        self.strategy=StraightPythonUpdateStrategy()

if __name__ == '__main__':
    unittest.main()
