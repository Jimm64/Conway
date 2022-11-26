from boardstate import BoardObserver
from gldrawstate import OpenGLDrawState
from OpenGL.GL import *
from OpenGL.GLU import *
from screen import GameScreen
from pygame.locals import *
import numpy
import pygame


class OpenGLScreen(GameScreen, BoardObserver):

    def on_update(self, board_state):

      glColorPointer(3, GL_BYTE, 0, self.opengl_draw_state.get_opengl_cell_vertex_colors())
      glVertexPointer(2, GL_FLOAT, 0, self.opengl_draw_state.get_opengl_cell_corner_vertices())
      glDrawArrays(GL_QUADS, 0, len(self.opengl_draw_state.get_opengl_cell_corner_vertices()) // 2)

      pygame.display.flip()

      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          pygame.quit()
          quit()
    
    def get_opengl_draw_state(self):
        return self.opengl_draw_state

    def __init__(self, width, height):
        self.opengl_draw_state = OpenGLDrawState()
        self.screen_width = width
        self.screen_height = height

        pygame.init()
        pygame.display.set_mode((width, height), DOUBLEBUF|OPENGL)


        glLoadIdentity()
        glViewport(0, 0, self.screen_width, self.screen_height)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, 1.0, 0, 1.0, 0, 1.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glEnableClientState(GL_COLOR_ARRAY)

        glEnableClientState(GL_VERTEX_ARRAY)
    

    def do_nothing(self):
        pass


