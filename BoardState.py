from numba import jit, cuda
import random
import unittest
import numpy




class BoardState:

    @cuda.jit('void(int32[:],int32[:],int32)')
    def updateCell(newCells, cells, maxCols):
        index = cuda.grid(1)

        row = int(index / maxCols)
        col = int(index % maxCols)

        cellArrayPos = row * (maxCols + 2) + (col + 1)

        maxCols += 2

        # Count neighbors
        neighborCount  = cells[cellArrayPos - maxCols - 1] & 1
        neighborCount += cells[cellArrayPos - maxCols + 0] & 1
        neighborCount += cells[cellArrayPos - maxCols + 1] & 1

        neighborCount += cells[cellArrayPos - 1] & 1
        neighborCount += cells[cellArrayPos + 1] & 1

        neighborCount += cells[cellArrayPos + maxCols - 1] & 1
        neighborCount += cells[cellArrayPos + maxCols + 0] & 1
        neighborCount += cells[cellArrayPos + maxCols + 1] & 1

        if neighborCount < 2 or neighborCount > 3:
            newCells[cellArrayPos] = 0
        elif neighborCount == 3:
            newCells[cellArrayPos] = 1
        else:
            newCells[cellArrayPos] = cells[cellArrayPos]

    def update(self):

        BoardState.updateCell[self.threadsPerBlock, self.blocksPerGrid](self.newCells, self.cells, self.cols)
        cuda.synchronize()

        cells = self.cells
        self.cells = self.newCells
        self.newCells = cells

    def __init__(self, rows, cols):

        self.rows = rows
        self.cols = cols
        self.cells = numpy.zeros((rows+2) * (cols+2),dtype=numpy.int32)
        self.newCells = numpy.zeros((rows+2) * (cols+2),dtype=numpy.int32)

        self.blocksPerGrid = 1024
        self.threadsPerBlock = int(rows * cols / (self.blocksPerGrid)) + 1


    def fromString(string):

        rowStrings = string.split("\n")
        rows = len(rowStrings)
        cols = len(rowStrings[0])

        for row in range(0, rows):
            if len(rowStrings[row]) != cols:
                raise Exception("Row lengths are not equal")
        
        boardState = BoardState(rows, cols)

        for row in range(0, rows):
            for col in range (0, cols):
                if rowStrings[row][col] == "X":
                    boardState.addCell(row, col)
                elif rowStrings[row][col] != "-":
                    raise Exception("Unrecognized character in board string")

        return boardState


    def randomizeState(self):
        for row in range(0, self.rows):
            for col in range (0, self.cols):
                if random.randint(0,1):
                    self.addCell(row, col)
                else:
                    self.killCell(row, col)

        return

    def cellState(self, row, col):
        return False if self.cells[(row+1) * (self.cols+2) + (col+1)] == 0 else True

    def addCell(self, row, col):
        self.cells[(row+1) * (self.cols+2) + (col+1)] = 1
        return

    def killCell(self, row, col):
        self.cells[(row+1) * (self.cols+2) + (col+1)] = 0
        return

    def toString(self):
        boardString = ""
        for row in range(0, self.rows):
            for col in range(0, self.cols):
                boardString += "X" if self.cellState(row, col) else "-"
            if row < self.rows - 1:
                boardString += "\n" 
        return boardString


class BoardStateTests(unittest.TestCase):

    def testBoardCanInitFromString(self):
        boardState = BoardState.fromString(
                "X-X\n" +
                "-X-\n" +
                "X-X")

        self.assertEqual(boardState.toString(),
                "X-X\n" +
                "-X-\n" +
                "X-X")


    def testAllCellsAreFalseAtStart(self):
        rows = 3
        cols = 4
        boardState = BoardState(rows=rows, cols=cols)

        self.assertEqual(boardState.toString(),
                "----\n" +
                "----\n" +
                "----")

    def testUpdateKillsCellsWithNoNeighbors(self):
        boardState = BoardState(rows=3, cols=3)
        boardState.addCell(0, 0)

        self.assertEqual(boardState.toString(),
                "X--\n" +
                "---\n" +
                "---")

        boardState.update()

        self.assertEqual(boardState.toString(),
                "---\n" +
                "---\n" +
                "---")


    def testUpdateKeepsAliveCellsWithThreeNeighbors(self):

        boardState = BoardState.fromString(
                "XX-\n" +
                "XX-\n" +
                "---")

        boardState.update()

        self.assertEqual(boardState.toString(),
                "XX-\n" +
                "XX-\n" +
                "---")



    def testUpdateCreatesCellIfItHasThreeNeighbors(self):

        boardState = BoardState.fromString(
                "XXX\n" +
                "---\n" +
                "---")

        boardState.update()

        self.assertEqual(boardState.toString(),
                "-X-\n" +
                "-X-\n" +
                "---")

    def testUpdateKillsCellWithFourNeighbors(self):

        boardState = BoardState.fromString(
                "-X-\n" +
                "XXX\n" +
                "-X-")

        boardState.update()

        self.assertEqual(boardState.toString(),
                "XXX\n" +
                "X-X\n" +
                "XXX")


if __name__ == '__main__':
    unittest.main()
