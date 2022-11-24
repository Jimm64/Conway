from boardstate import BoardObserver
from screen import GameScreen
import time

class TextScreen(GameScreen, BoardObserver):

    def __init__(self, board_state, width, height):
      pass

    def on_update(self, board_state):
      print(board_state.to_string() + "\n")
