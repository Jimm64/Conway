from numba import jit, cuda
import random
import unittest
import numpy

class BoardState:

    def cellColors(self):
        return self.cellColors


    @cuda.jit('void(int32[:],int32[:],float32[:],int32,int32,int32)')
    def updateCell(newCells, cells, cellColors, numRows, numCols, loopsPerThread):

        index = cuda.grid(1)

        for x in range (index * loopsPerThread, index * loopsPerThread + loopsPerThread):

            if x >= numRows * numCols:
                return

            row = int(x / numCols)
            col = int(x % numCols)



            cellArrayPos = (row + 1) * (numCols + 2) + (col + 1)

            realNumCols = numCols + 2

            # Count neighbors
            neighborCount  = cells[cellArrayPos - realNumCols - 1] & 1
            neighborCount += cells[cellArrayPos - realNumCols + 0] & 1
            neighborCount += cells[cellArrayPos - realNumCols + 1] & 1

            neighborCount += cells[cellArrayPos - 1] & 1
            neighborCount += cells[cellArrayPos + 1] & 1

            neighborCount += cells[cellArrayPos + realNumCols - 1] & 1
            neighborCount += cells[cellArrayPos + realNumCols + 0] & 1
            neighborCount += cells[cellArrayPos + realNumCols + 1] & 1

            if neighborCount < 2 or neighborCount > 3:
                newCells[cellArrayPos] = 0
            elif neighborCount == 3:
                newCells[cellArrayPos] = 1
            else:
                newCells[cellArrayPos] = cells[cellArrayPos]

            cellColorPos = 3 * 4 * x

            if newCells[cellArrayPos]:
                for corner in range(0, 4):
                    cellColors[cellColorPos + corner * 3 + 2] = 1.0
            else:
                for corner in range(0, 4):
                    cellColors[cellColorPos + corner * 3 + 2] = 0.0

    def update(self):

        BoardState.updateCell[self.threadsPerBlock, self.blocksPerGrid](self.newCells, self.cells, self.cellColors, self.rows, self.cols, self.loopsPerThread)
        cuda.synchronize()

        cells = self.cells
        self.cells = self.newCells
        self.newCells = cells

    def __init__(self, rows, cols):

        self.rows = rows
        self.cols = cols
        self.cells = numpy.zeros((rows+2) * (cols+2),dtype=numpy.int32)
        self.newCells = numpy.zeros((rows+2) * (cols+2),dtype=numpy.int32)
        self.cellColors = numpy.zeros(3 * 4 * self.cols * self.rows, dtype=numpy.float32)

        self.blocksPerGrid = int(1024)
        self.loopsPerThread = 8

        # Need enough threads to operate on the whole board
        threadsNeeded = 1 + int(rows * cols / self.loopsPerThread)

        # Round up thread count to a multiple of block count
        if (threadsNeeded % self.blocksPerGrid) :
            threadsNeeded += int(self.blocksPerGrid - threadsNeeded % self.blocksPerGrid)

        self.threadsPerBlock = int(threadsNeeded / self.blocksPerGrid)


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
