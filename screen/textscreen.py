from board.boardstate import BoardObserver
from screen.screen import GameScreen
import time
import sys

class TextScreen(GameScreen, BoardObserver):
  """
    Display the current board state as text, simply printing it to the
    screen.
  """

  def __init__(self, width, height):

    pass

  def on_update(self, board_state):
    """ Display the board."""

    print(board_state.to_string() + "\n")

class AnsiTextScreen(TextScreen):
  """
    Display the current board state as text. Same as TextScreen but uses ANSI
    control characters to clear the screen and position the cursor.
  """

  def __init__(self, width, height):

    self.is_first_update = True

  def on_update(self, board_state):
    """ Display the board."""

    # Clear the screen when displaying the first board state.
    if self.is_first_update:
      sys.stdout.write("\033[2J")
      self.is_first_update = False
    
    # Move cursor to origin.
    sys.stdout.write("\033[1;1H")

    TextScreen.on_update(self, board_state)
