import BoardState
import Screen

boardState = BoardState.BoardState(400, 400)
boardState.randomizeState()

screen = Screen.GlScreen(boardState, 800, 800)

screen.loop()

