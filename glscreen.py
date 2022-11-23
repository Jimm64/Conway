from boardstate import BoardObserver
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from screen import GameScreen
import numpy

class OpenGLScreen(GameScreen, BoardObserver):

    def onUpdate(self, boardState):

      glColorPointer(3, GL_FLOAT, 0, boardState.glCellCornerVertexColors())
      glVertexPointer(2, GL_FLOAT, 0, boardState.glCellCornerVertices())
      glDrawArrays(GL_QUADS, 0, len(boardState.glCellCornerVertices()) // 2)
      glutSwapBuffers()

      glutMainLoopEvent()

    def __init__(self, boardState, width, height):
        self.displayWidth = width
        self.displayHeight = height

        glutInit()
        glutInitDisplayMode(GLUT_RGBA)
        glutInitWindowSize(self.displayWidth, self.displayHeight)
        glutInitWindowPosition(0, 0)
        self.window = glutCreateWindow("Wrath of Conway")
        glutDisplayFunc(self.doNothing)
        glutIdleFunc(self.doNothing)

        glLoadIdentity()
        glViewport(0, 0, self.displayWidth, self.displayHeight)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, 1.0, 0, 1.0, 0, 1.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glEnableClientState(GL_COLOR_ARRAY)

        glEnableClientState(GL_VERTEX_ARRAY)
    

    def doNothing(self):
        pass


