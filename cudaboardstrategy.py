from numba import jit, cuda
from BoardState import UpdateStrategy
from BoardState import BoardStateTests
import unittest

class CudaUpdateStrategy(UpdateStrategy):

  def update(self, boardState):

    blocksPerGrid = int(1024)
    loopsPerThread = 8

    # Need enough threads to operate on the whole board
    threadsNeeded = 1 + int(boardState.rows * boardState.cols / loopsPerThread)

    # Round up thread count to a multiple of block count
    if (threadsNeeded % blocksPerGrid) :
        threadsNeeded += int(blocksPerGrid - threadsNeeded % blocksPerGrid)

    threadsPerBlock = int(threadsNeeded / blocksPerGrid)

    self.updateCell[threadsPerBlock, blocksPerGrid](
        boardState.newCells, boardState.cells, boardState.cellColors, boardState.rows, 
        boardState.cols, loopsPerThread)

    cuda.synchronize()

  @cuda.jit('void(int32[:],int32[:],float32[:],int32,int32,int32)')
  def updateCell(newCells, cells, cellColors, numRows, numCols, loopsPerThread):

      # The cells reprsent a two-dimensional board, but are passed in as
      # a one-dimensional array. Determine which cells this thread
      # is responsible for updating.
      index = cuda.grid(1)
      maxIndex = index * loopsPerThread + loopsPerThread
      if maxIndex >= numRows * numCols:
          maxIndex = numRows * numCols
      realNumCols = numCols + 2

      for x in range (index * loopsPerThread, maxIndex):

          cellArrayPos = (x // numCols + 1) * (numCols + 2) + (x % numCols + 1)

          # Count neighbors.
          neighborCount  = cells[cellArrayPos - realNumCols - 1]
          neighborCount += cells[cellArrayPos - realNumCols + 0]
          neighborCount += cells[cellArrayPos - realNumCols + 1]

          neighborCount += cells[cellArrayPos - 1]
          neighborCount += cells[cellArrayPos + 1]

          neighborCount += cells[cellArrayPos + realNumCols - 1]
          neighborCount += cells[cellArrayPos + realNumCols + 0]
          neighborCount += cells[cellArrayPos + realNumCols + 1]

          # Set whether the cell is alive or dead based on
          # neighbor count and current state.
          cellColor = 0.0
          if neighborCount < 2 or neighborCount > 3:
              newCells[cellArrayPos] = 0
          elif neighborCount == 3:
              newCells[cellArrayPos] = 1
              cellColor = 1.0
          else:
              newCells[cellArrayPos] = cells[cellArrayPos]
              if newCells[cellArrayPos] == 1:
                cellColor = 1.0

          # Likewise set what color the cell should now be.
          cellColorPos = 3 * 4 * x
          for corner in range(0, 4):
            cellColors[cellColorPos + corner * 3 + 2] = cellColor

class CudaStrategyUpdateTests(BoardStateTests, unittest.TestCase):

    def setUp(self):
        self.strategy=CudaUpdateStrategy()

if __name__ == '__main__':
    unittest.main()
