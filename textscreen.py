from BoardState import BoardObserver
from Screen import GameScreen
import time

class TextScreen(GameScreen, BoardObserver):

    def __init__(self, boardState, width, height):
      pass

    def onUpdate(self, boardState):
      print(boardState.toString() + "\n")
