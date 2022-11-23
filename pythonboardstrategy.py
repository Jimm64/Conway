from BoardState import UpdateStrategy
from BoardState import BoardStateTests
import unittest

class StraightPythonUpdateStrategy(UpdateStrategy):

  def update(self, boardState):

    self.updateCells(boardState.newCells, boardState.cells, boardState.cellColors,
        boardState.rows, boardState.cols)

  def updateCells(self, newCells, cells, cellColors, maxRows, maxCols):

    realNumCols = maxCols + 2

    for x in range (maxCols * maxRows):

        cellArrayPos = (x // maxCols + 1) * (maxCols + 2) + (x % maxCols + 1)

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


class StraightPythonStrategyUpdateTests(BoardStateTests, unittest.TestCase):

    def setUp(self):
        self.strategy=StraightPythonUpdateStrategy()

if __name__ == '__main__':
    unittest.main()
