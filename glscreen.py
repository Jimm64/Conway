from boardstate import BoardObserver
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from screen import GameScreen
import numpy

class OpenGLScreen(GameScreen, BoardObserver):

    def on_update(self, boardState):

      glColorPointer(3, GL_FLOAT, 0, boardState.get_opengl_cell_vertex_colors())
      glVertexPointer(2, GL_FLOAT, 0, boardState.get_opengl_cell_corner_vertices())
      glDrawArrays(GL_QUADS, 0, len(boardState.get_opengl_cell_corner_vertices()) // 2)
      glutSwapBuffers()

      glutMainLoopEvent()

    def __init__(self, boardState, width, height):
        self.screen_width = width
        self.screen_height = height

        glutInit()
        glutInitDisplayMode(GLUT_RGBA)
        glutInitWindowSize(self.screen_width, self.screen_height)
        glutInitWindowPosition(0, 0)
        self.window = glutCreateWindow("Wrath of Conway")
        glutDisplayFunc(self.do_nothing)
        glutIdleFunc(self.do_nothing)

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


