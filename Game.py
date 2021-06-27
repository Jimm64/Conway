import BoardState
import Screen
import sys

boardState = BoardState.BoardState(int(sys.argv[1]), int(sys.argv[2]))
boardState.randomizeState()

screen = Screen.GlScreen(boardState, int(sys.argv[3]), int(sys.argv[4]))

screen.loop()

