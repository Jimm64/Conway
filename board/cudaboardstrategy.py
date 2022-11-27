from numba import jit, cuda
from board.boardstate import UpdateStrategy
from board.boardstate import BoardStateTests
import numpy
import unittest

class CudaUpdateStrategy(UpdateStrategy):

  def __init__(self, opengl_draw_state=None):
    self.opengl_draw_state = opengl_draw_state

    # CUDA seems to want us to pass in something for the colors array
    # even if we aren't using a display that has them.
    self.empty_cell_color_array = numpy.zeros(0, dtype=numpy.uint8)

  def update(self, board_state):
    if self.opengl_draw_state:
      self.opengl_draw_state.set_cell_dimensions(board_state.rows, board_state.cols)

    blocks_per_grid = 1024
    cells_per_thread = 8

    # Need enough threads to operate on the whole board
    threads_needed = 1 + int(board_state.rows * board_state.cols / cells_per_thread)

    # Round up thread count to a multiple of block count
    if (threads_needed % blocks_per_grid) :
        threads_needed += blocks_per_grid - threads_needed % blocks_per_grid

    threads_per_block = threads_needed // blocks_per_grid

    cuda_stream = cuda.stream()

    new_cells_gpu = cuda.device_array_like(board_state.new_cells, stream=cuda_stream)
    cells_gpu = cuda.to_device(board_state.cells, stream=cuda_stream)

    if self.opengl_draw_state:
      cell_colors = self.opengl_draw_state.get_opengl_cell_vertex_colors()
    else:
      cell_colors = self.empty_cell_color_array

    cell_colors_gpu = cuda.device_array_like(cell_colors, stream=cuda_stream)

    self.update_cell[threads_per_block, blocks_per_grid, cuda_stream](
      new_cells_gpu, cells_gpu, 
      cell_colors_gpu, board_state.rows, 
      board_state.cols, cells_per_thread)

    new_cells_gpu.copy_to_host(board_state.new_cells, stream=cuda_stream)
    cells_gpu.copy_to_host(board_state.cells, stream=cuda_stream)
    cell_colors_gpu.copy_to_host(cell_colors, stream=cuda_stream)
    cuda_stream.synchronize()

  @cuda.jit
  def update_cell(new_cells, cells, cell_colors, num_rows, num_cols, loops_per_thread):

    # Keep any live cell with 2 or 3 neighbors.
    keep_cell_on_neighbor_counts = (0, 0, 1, 1, 0, 0, 0, 0, 0)

    # Add a ell on any space with three live neighbors.
    add_cell_on_neighbor_counts =  (0, 0, 0, 1, 0, 0, 0, 0, 0)

    # The cells reprsent a two-dimensional board, but are passed in as
    # a one-dimensional array. Determine which cells this thread
    # is responsible for updating.
    grid_index = cuda.grid(1)
    max_index = grid_index * loops_per_thread + loops_per_thread
    if max_index >= num_rows * num_cols:
      max_index = num_rows * num_cols

    # Each row also includes two border cells. Account for them
    # when determining a given cell's index.
    size_of_row = num_cols + 2

    for x in range(grid_index * loops_per_thread, max_index):

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

      if len(cell_colors) > 0:
        # Likewise set what color the cell should now be.
        cell_color_index = 3 * 4 * x
        for corner in range(0, 4):
          cell_colors[cell_color_index + corner * 3 + 2] = 127 * new_cells[cell_array_index] 

class CudaStrategyUpdateTests(BoardStateTests, unittest.TestCase):

  def setUp(self):
    self.strategy=CudaUpdateStrategy()

if __name__ == '__main__':
  unittest.main()
