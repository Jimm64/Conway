from abc import ABC, abstractmethod
import numpy
import time

import BoardState

class GameScreen(ABC):

  @abstractmethod
  def __init__(self, boardState, width, height):
    pass

