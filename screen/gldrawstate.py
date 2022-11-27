import numpy

class OpenGLDrawState():
  """
    Holds the cell vertex/color arrays used when drawing the cells via OpenGL.

    Board update strategies can update these arrays - in particular, we can use
    the same CUDA kernel that updates the board state to update these.  But
    this object helps decouple knowledge of OpenGL from the board state, so
    that OpenGL does not have to be installed in order to run the game with
    text-based displays.
  """

  def __init__(self):

    self.rows = 0
    self.cols = 0

    # Start with empty arrays. The set_cell_dimensions function will
    # allocate appropriately-sized ones for a given board.
    self.opengl_cell_colors = numpy.zeros(0, dtype=numpy.uint8)
    self.opengl_cell_corners = numpy.zeros(0, dtype=numpy.float32)

  def get_opengl_cell_vertex_colors(self):
    """
      Returns the array of cell colors. 
      Each cell gets four three-byte RGB color values, one for each corner of
      the rectangle drawn for the given cell.

      Array is one-dimensional, but represents the two-dimensional board of cells.
    """

    return self.opengl_cell_colors
  
  def get_opengl_cell_corner_vertices(self):
    """
      Returns the array of cell vertices.
      Array is grouped into four vertices for each cell, where each vertex is one
      corner of a rectangle drawn for the given cell.

      Cell locations are based on a two-dimensional display ranging from location
      (0.0, 0.0) to (1.0, 1.0).

      Array is one-dimensional, but represents the two-dimensional board of cells.
    """

    return self.opengl_cell_corners
  
  def set_cell_dimensions(self, rows, cols):
    """Set board dimensions and allocate arrays accordingly."""

    # Check if array needs to grow
    if rows * cols * 3 * 4 > len(self.opengl_cell_colors):
      self.opengl_cell_colors = numpy.zeros(3 * 4 * cols * rows, dtype=numpy.uint8)
      self.opengl_cell_corners = numpy.zeros(2 * 4 * cols * rows, dtype=numpy.float32)

    if rows != self.rows or cols != self.cols:
      self.rows = rows
      self.cols = cols

      # Set locations of each cell's corner vertices.
      width = 1.0 / self.cols
      height = 1.0 / self.rows

      for row in range(0, self.rows):
        for col in range(0, self.cols):
          x = row * width
          y = col * height
          cell = (row * self.cols + col) * 8

          self.opengl_cell_corners[cell + 0] = x
          self.opengl_cell_corners[cell + 1] = y
          self.opengl_cell_corners[cell + 2] = x
          self.opengl_cell_corners[cell + 3] = y + height
          self.opengl_cell_corners[cell + 4] = x + width
          self.opengl_cell_corners[cell + 5] = y + height
          self.opengl_cell_corners[cell + 6] = x + width
          self.opengl_cell_corners[cell + 7] = y
