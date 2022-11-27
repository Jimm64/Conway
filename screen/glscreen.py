from board.boardstate import BoardObserver
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *
from screen.gldrawstate import OpenGLDrawState
from screen.screen import GameScreen
import numpy
import pygame


class OpenGLScreen(GameScreen, BoardObserver):
  """Displays the board state via a Pygame window and OpenGL."""

  def on_update(self, board_state):
    """Display the current board state."""

    # The draw state should already have the correct vertices and the board strategy
    # should have updated the colors to reflect alive/dead cells, so all we have
    # to do is tell OpenGL to draw the results.
    #
    # Drawing via arrays has shown itself to be faster than loops to draw each cell.
    glColorPointer(3, GL_BYTE, 0, self.opengl_draw_state.get_opengl_cell_vertex_colors())
    glVertexPointer(2, GL_FLOAT, 0, self.opengl_draw_state.get_opengl_cell_corner_vertices())
    glDrawArrays(GL_QUADS, 0, len(self.opengl_draw_state.get_opengl_cell_corner_vertices()) // 2)

    # Drawing done, so swap the buffer.
    pygame.display.flip()

    # Check for events.
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        quit()
  
  def get_opengl_draw_state(self):
    """ Returns this object's draw state."""

    return self.opengl_draw_state

  def __init__(self, width, height):

    self.opengl_draw_state = OpenGLDrawState()
    self.screen_width = width
    self.screen_height = height

    pygame.init()
    pygame.display.set_mode((width, height), DOUBLEBUF|OPENGL)

    # Set our projected view to range from (0.0, 0.0) to (1.0, 1.0).
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, 1.0, 0, 1.0, 0, 1.0)

    # Set transform for objects to be drawn (but we don't do anything special
    # here, we're just drawing rectangles in a two-dimensional view)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Enable use of arrays to specify vertices and their colors, since this is
    # how we draw the cells.
    glEnableClientState(GL_COLOR_ARRAY)
    glEnableClientState(GL_VERTEX_ARRAY)

