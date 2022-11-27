import numpy

class OpenGLDrawState():

    def __init__(self):

      self.rows = 0
      self.cols = 0
      self.opengl_cell_colors = numpy.zeros(0, dtype=numpy.uint8)
      self.opengl_cell_corners = numpy.zeros(0, dtype=numpy.float32)

    def get_opengl_cell_vertex_colors(self):

      return self.opengl_cell_colors
    
    def get_opengl_cell_corner_vertices(self):

      return self.opengl_cell_corners
    
    def set_cell_dimensions(self, rows, cols):

      # Check if array needs to grow
      if rows * cols * 3 * 4 > len(self.opengl_cell_colors):
        self.opengl_cell_colors = numpy.zeros(3 * 4 * cols * rows, dtype=numpy.uint8)
        self.opengl_cell_corners = numpy.zeros(2 * 4 * cols * rows, dtype=numpy.float32)


      if rows != self.rows or cols != self.cols:
        self.rows = rows
        self.cols = cols

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
