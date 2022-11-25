from numba import jit, cuda
from boardstate import UpdateStrategy
from boardstate import BoardStateTests
import numpy
import unittest

class CudaUpdateStrategy(UpdateStrategy):

  def __init__(self, opengl_draw_state=None):
    self.opengl_draw_state = opengl_draw_state

    # CUDA seems to want us to pass in something for the colors array
    # even if we aren't using a display that has them.
    self.empty_cell_color_array = numpy.zeros(0, dtype=numpy.float32)

  def update(self, board_state):
    if self.opengl_draw_state:
      self.opengl_draw_state.set_cell_dimensions(board_state.rows, board_state.cols)

    blocks_per_grid = int(1024)
    loops_per_thread = 8

    # Need enough threads to operate on the whole board
    threads_needed = 1 + int(board_state.rows * board_state.cols / loops_per_thread)

    # Round up thread count to a multiple of block count
    if (threads_needed % blocks_per_grid) :
        threads_needed += int(blocks_per_grid - threads_needed % blocks_per_grid)

    threads_per_block = int(threads_needed / blocks_per_grid)

    if self.opengl_draw_state:
        self.update_cell[threads_per_block, blocks_per_grid](
            board_state.new_cells, board_state.cells, 
            self.opengl_draw_state.get_opengl_cell_vertex_colors(), board_state.rows, 
            board_state.cols, loops_per_thread)
    else:
        self.update_cell[threads_per_block, blocks_per_grid](
            board_state.new_cells, board_state.cells, 
            self.empty_cell_color_array, board_state.rows, 
            board_state.cols, loops_per_thread)

    cuda.synchronize()

  @cuda.jit('void(int32[:],int32[:],float32[:],int32,int32,int32)')
  def update_cell(new_cells, cells, cell_colors, num_rows, num_cols, loops_per_thread):

      # The cells reprsent a two-dimensional board, but are passed in as
      # a one-dimensional array. Determine which cells this thread
      # is responsible for updating.
      index = cuda.grid(1)
      max_index = index * loops_per_thread + loops_per_thread
      if max_index >= num_rows * num_cols:
          max_index = num_rows * num_cols

      # Each row also includes two border cells. Account for them
      # when determining a given cell's index.
      size_of_row = num_cols + 2

      for x in range (index * loops_per_thread, max_index):

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
          if cell_neighbor_count < 2 or cell_neighbor_count > 3:
              new_cells[cell_array_index] = 0
          elif cell_neighbor_count == 3:
              new_cells[cell_array_index] = 1
          else:
              new_cells[cell_array_index] = cells[cell_array_index]

          if len(cell_colors) > 0:
            # Likewise set what color the cell should now be.
            cell_color_index = 3 * 4 * x
            for corner in range(0, 4):
              cell_colors[cell_color_index + corner * 3 + 2] = new_cells[cell_array_index] 

class CudaStrategyUpdateTests(BoardStateTests, unittest.TestCase):

    def setUp(self):
        self.strategy=CudaUpdateStrategy()

if __name__ == '__main__':
    unittest.main()
