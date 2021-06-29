from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy

import BoardState

class GlScreen:


    def loop(self):
        while True:
            glutMainLoopEvent()
            self.boardState.update()
            self.drawScreen()
            self.updateCount += 1

    def __init__(self, boardState, width, height):
        self.updateCount = 0
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

        glEnableClientState(GL_VERTEX_ARRAY)
        self.corners = numpy.zeros(8 * self.boardState.cols * self.boardState.rows, dtype=numpy.float32)
        glVertexPointer(2, GL_FLOAT, 0, self.corners)

    def drawScreen(self):

        width = self.displayWidth / self.boardState.cols
        height = self.displayHeight / self.boardState.rows

        glClear(GL_COLOR_BUFFER_BIT)

        glColor3f(0, 0, 1)

        activeCells = 0
        for row in range(0, self.boardState.rows):
            for col in range(0, self.boardState.cols):
                if self.boardState.cellState(row, col):
                    x = row * width
                    y = col * height
                    cell = activeCells * 8

                    self.corners[cell + 0] = x
                    self.corners[cell + 1] = y
                    self.corners[cell + 2] = x
                    self.corners[cell + 3] = y + height
                    self.corners[cell + 4] = x + width
                    self.corners[cell + 5] = y + height
                    self.corners[cell + 6] = x + width
                    self.corners[cell + 7] = y

                    activeCells += 1

        glDrawArrays(GL_QUADS, 0, activeCells * 4)

        glutSwapBuffers()

