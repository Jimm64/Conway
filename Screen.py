from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

import BoardState

class GlScreen:

    def loop(self):
        glutMainLoop()

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

    def drawScreen(self):
        self.boardState.update()

        width = self.displayWidth / self.boardState.cols
        height = self.displayHeight / self.boardState.rows

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glColor3f(0, 0, 1)
        glBegin(GL_QUADS)
        for row in range(0, self.boardState.rows):
            for col in range(0, self.boardState.cols):
                if self.boardState.cellState(row, col):
                    x = row * width
                    y = col * height
                    glVertex2f(x, y)
                    glVertex2f(x, y + height)
                    glVertex2f(x + width, y + height)
                    glVertex2f(x + width, y)
        glEnd()

        glutSwapBuffers()

