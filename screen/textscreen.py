from board.boardstate import BoardObserver
from screen.screen import GameScreen
import time
import sys

class TextScreen(GameScreen, BoardObserver):

    def __init__(self, width, height):
      pass

    def on_update(self, board_state):
      print(board_state.to_string() + "\n")

class AnsiTextScreen(TextScreen):

    def __init__(self, width, height):
      self.is_first_update = True
      pass

    def on_update(self, board_state):
        if self.is_first_update:
            sys.stdout.write("\033[2J")
            self.is_first_update = False
        
        sys.stdout.write("\033[1;1H")
        TextScreen.on_update(self, board_state)
