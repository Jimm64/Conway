from numba import jit, cuda
import random
import unittest
import numpy

wordWidth = 32

class BoardState:

    # Return array position and bit position
    def cellIndex(self, row, col):

        index = int((row + 1) * (self.wordsPerRow + 2) + col / wordWidth + 1)
        bit = int(col % wordWidth)
        return (index, bit)

    @cuda.jit('void(int32[:],int32[:],int32,int32,int32,int32)')
    def updateCell(newCells, cells, numRows, numCols, wordsPerRow, wordWidth):

        gridId = cuda.grid(1)

        wordsPerRow += 2

        # [x][x][x][x][x]
        # [x][W][W][W][x]
        # [x][W][W][W][x]
        # [x][W][W][W][x]
        # [x][x][x][x][x]

        # GridId 0 should work on index 6, which is wordsPerRow + 1
        # GridId 2 should work on index 8, which is wordsPerRow  + 1 + 2
        # GridId 3 should work on index 11, which is wordsPerRow * 2 + 1

        row = int(1 + gridId / wordsPerRow)
        col = int(1 + gridId % wordsPerRow)

        index = row * wordsPerRow + col

        if row >= numRows + 1 or col >= wordsPerRow - 1:
            return

        numBits = numCols if col == wordsPerRow - 2 else wordWidth

        for bit in range(0, numBits):

            # Count neighbors

            if bit < wordWidth - 1:
                rightNeighborIndex = index
                rightNeighborBit = bit + 1
            else:
                rightNeighborIndex = index + 1
                rightNeighborBit = 0

            if bit > 0:
                leftNeighborIndex = index
                leftNeighborBit = bit - 1
            else:
                leftNeighborIndex = index - 1
                leftNeighborBit = wordWidth - 1

            neighborCount = 0

            # above and below
            neighborCount  = (cells[index - wordsPerRow] & (1 << bit)) >> bit
            neighborCount += (cells[index + wordsPerRow] & (1 << bit)) >> bit

            # Up-left, down-left, left
            neighborCount += (cells[leftNeighborIndex - wordsPerRow] & (1 << leftNeighborBit)) >> leftNeighborBit
            neighborCount += (cells[leftNeighborIndex + wordsPerRow] & (1 << leftNeighborBit)) >> leftNeighborBit
            neighborCount += (cells[leftNeighborIndex              ] & (1 << leftNeighborBit)) >> leftNeighborBit

            # Up-right, down-right, right
            neighborCount += (cells[rightNeighborIndex - wordsPerRow] & (1 << rightNeighborBit)) >> rightNeighborBit
            neighborCount += (cells[rightNeighborIndex + wordsPerRow] & (1 << rightNeighborBit)) >> rightNeighborBit
            neighborCount += (cells[rightNeighborIndex              ] & (1 << rightNeighborBit)) >> rightNeighborBit

            if neighborCount < 2 or neighborCount > 3:
                newCells[index] &= ~(1 << bit)
            elif neighborCount == 3:
                newCells[index] |= (1 << bit)
            elif cells[index] & (1 << bit):
                newCells[index] |= (1 << bit)
            else:
                newCells[index] &= ~(1 << bit)

    def update(self):

        BoardState.updateCell[self.threadsPerBlock, self.blocksPerGrid](self.newCells, self.cells, self.rows, self.cols, self.wordsPerRow, self.wordWidth)
        cuda.synchronize()

        cells = self.cells
        self.cells = self.newCells
        self.newCells = cells

    def __init__(self, rows, cols):

        self.rows = rows
        self.cols = cols
        self.wordWidth = wordWidth

        self.wordsPerRow = int(cols / wordWidth)
        if (cols % wordWidth):
            self.wordsPerRow += 1

        self.cells = numpy.zeros((self.rows+2) * (self.wordsPerRow + 2), dtype=numpy.uint32)
        self.newCells = numpy.zeros((self.rows+2) * (self.wordsPerRow + 2), dtype=numpy.uint32)

        self.blocksPerGrid = int(1024)

        # Need enough threads to operate on the whole board
        threadsNeeded = 1 + int(self.rows * self.wordsPerRow)

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
        (index, bit) = self.cellIndex(row, col)
        return False if (self.cells[index] & (1 << bit)) == 0 else True

    def addCell(self, row, col):
        (index, bit) = self.cellIndex(row, col)
        self.cells[index] |= (1 << bit)

    def killCell(self, row, col):
        (index, bit) = self.cellIndex(row, col)
        self.cells[index] &= ~(1 << bit)

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

    def testAddCellAddsACell(self):
        rows = 3
        cols = 4
        boardState = BoardState(rows=rows, cols=cols)

        self.assertEqual(boardState.toString(),
                "----\n" +
                "----\n" +
                "----")

        boardState.addCell(0,0)

        self.assertEqual(boardState.toString(),
                "X---\n" +
                "----\n" +
                "----")

        boardState.addCell(1,1)

        self.assertEqual(boardState.toString(),
                "X---\n" +
                "-X--\n" +
                "----")

    def testKillCellKillsACell(self):

        boardState = BoardState.fromString(
                "XX-\n" +
                "XX-\n" +
                "---")

        boardState.killCell(1,1)

        self.assertEqual(boardState.toString(),
                "XX-\n" +
                "X--\n" +
                "---")


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

    def testCellIndexReturnsCorrectValues(self):

        boardState = BoardState.fromString(
                "XXX\n" +
                "---\n" +
                "---")

        self.assertEqual(boardState.cellIndex(0,0), (4,0))
        self.assertEqual(boardState.cellIndex(1,0), (7,0))
        self.assertEqual(boardState.cellIndex(2,0), (10,0))
        self.assertEqual(boardState.cellIndex(0,1), (4,1))
        self.assertEqual(boardState.cellIndex(0,2), (4,2))
        self.assertEqual(boardState.cellIndex(0,3), (4,3))


if __name__ == '__main__':
    unittest.main()
