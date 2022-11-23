from Screen import GameScreen
import time

class TextScreen(GameScreen):

    def __init__(self, boardState, width, height):
      self.boardState = boardState
      pass

    def loop(self, strategy):
      while True:
        print(self.boardState.toString() + "\n")
        self.boardState.update(strategy)
        time.sleep(0.1)
