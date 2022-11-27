from abc import ABC, abstractmethod
import numpy
import time

class GameScreen(ABC):
  """ Base class for different ways to display the game's board state."""

  @abstractmethod
  def __init__(self, board_state, width, height):
    pass

