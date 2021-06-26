from numba import jit, cuda
import random
import unittest
import numpy

def updateCells(newCells, cells, maxRows, maxCols):

    threadsPerBlock = 2
    blocksPerGrid = maxRows * maxCols + (threadsPerBlock - 1)

    #updateCellsInt[blocksPerGrid, threadsPerBlock](newCells, cells, maxRows, maxCols)
    updateCellsInt(newCells, cells, maxRows, maxCols)


@jit
def updateCellsInt(newCells, cells, maxRows, maxCols):

    for row in range(0, maxRows):
        for col in range(0, maxCols):

            # Count neighbors, minus current cell
            neighbors = -cells[row * maxRows + col]

            minRow = row - 1 if row > 0 else 0
            maxRow = row + 1 if row + 1 < maxRows else row
            minCol = col - 1 if col > 0 else 0
            maxCol = col + 1 if col + 1 < maxCols else col

            for nRow in range(minRow, maxRow+1):
                for nCol in range(minCol, maxCol+1):
                    neighbors += cells[nRow * maxRows + nCol]

            if neighbors == 3:
                newCells[row * maxRows + col] = 1
            elif neighbors < 2 or neighbors > 3:
                newCells[row * maxRows + col] = 0
            else:
                newCells[row * maxRows + col] = cells[row * maxRows + col]

class BoardState:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.cells = numpy.zeros(rows * cols)
        self.newCells = numpy.zeros(rows * cols)

    def fromString(string):

        rowStrings = string.split("\n")
        rows = len(rowStrings)
        cols = len(rowStrings[0])

        for row in range(1, rows):
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
        return False if self.cells[row * self.rows + col] == 0 else True

    def update(self):

        updateCells(self.newCells, self.cells, self.rows, self.cols)

        newCells = self.newCells
        self.newCells = self.cells
        self.cells = newCells
        return

    def addCell(self, row, col):
        self.cells[row * self.rows + col] = 1
        return

    def killCell(self, row, col):
        self.cells[row * self.rows + col] = 0
        return

    def toString(self):
        boardString = ""
        for row in range(0, self.rows):
            for col in range(0, self.cols):
                boardString += "X" if self.cells[row * self.rows + col] else "-"
            if row < self.rows - 1:
                boardString += "\n" 
        return boardString


    def printCells(self):
        print("Rows:", len(self.cells), " Cols:", len(self.cells[0]))
        print(self.cells)
        return


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
