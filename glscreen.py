from BoardState import BoardObserver
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from Screen import GameScreen
import numpy

class OpenGLScreen(GameScreen, BoardObserver):

    def onUpdate(self, boardState):

      if boardState is not self.boardState:
        raise ValueError("Called to update a board other than the one we were created with.")

      glutMainLoopEvent()
      self.drawScreen()

    def __init__(self, boardState, width, height):
        self.displayWidth = width
        self.displayHeight = height
        self.boardState = boardState

        glutInit()
        glutInitDisplayMode(GLUT_RGBA)
        glutInitWindowSize(self.displayWidth, self.displayHeight)
        glutInitWindowPosition(0, 0)
        self.window = glutCreateWindow("Wrath of Conway")
        glutDisplayFunc(self.drawScreen)
        glutIdleFunc(self.drawScreen)

        glLoadIdentity()
        glViewport(0, 0, self.displayWidth, self.displayHeight)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.displayWidth, 0, self.displayHeight, 0, 1)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glEnableClientState(GL_COLOR_ARRAY)
        self.colors = boardState.cellColors
        glColorPointer(3, GL_FLOAT, 0, self.colors)

        glEnableClientState(GL_VERTEX_ARRAY)
        self.corners = numpy.zeros(8 * self.boardState.cols * self.boardState.rows, dtype=numpy.float32)
        glVertexPointer(2, GL_FLOAT, 0, self.corners)

        width = self.displayWidth / self.boardState.cols
        height = self.displayHeight / self.boardState.rows

        for row in range(0, self.boardState.rows):
            for col in range(0, self.boardState.cols):
                x = row * width
                y = col * height
                cell = (row * self.boardState.cols + col) * 8

                self.corners[cell + 0] = x
                self.corners[cell + 1] = y
                self.corners[cell + 2] = x
                self.corners[cell + 3] = y + height
                self.corners[cell + 4] = x + width
                self.corners[cell + 5] = y + height
                self.corners[cell + 6] = x + width
                self.corners[cell + 7] = y
    

    def drawScreen(self):

        glDrawArrays(GL_QUADS, 0, self.boardState.rows * self.boardState.cols * 4)

        glutSwapBuffers()

