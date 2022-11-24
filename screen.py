from abc import ABC, abstractmethod
import numpy
import time

class GameScreen(ABC):

  @abstractmethod
  def __init__(self, board_state, width, height):
    pass

