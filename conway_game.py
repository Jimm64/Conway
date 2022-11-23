from boardstate import BoardState
import argparse
import sys
import time

NANOS_PER_SECOND = 1000000000

arg_parser = argparse.ArgumentParser("Conway's Game of Life")

arg_parser.add_argument("--cell-dimensions", dest="cell_dimensions", nargs=2, required=False, type=int, default=[100,100], help="Number of cell columns and rows")
arg_parser.add_argument("--screen-dimensions", dest="screen_dimensions", nargs=2, required=False, type=int, default=[400,400], help="Screen width and height")
arg_parser.add_argument("--cuda", action="store_true", dest="use_cuda_strategy", required=False, default=False, help="Use CUDA to update board state.")
arg_parser.add_argument("--display-as-text", action="store_true", dest="use_text_display", required=False, default=False, help="Display board as text instead of using OpenGL.")
args = arg_parser.parse_args()

boardState = BoardState(*args.cell_dimensions)
boardState.randomizeState()

if args.use_text_display:
  from textscreen import TextScreen
  screen = TextScreen(boardState, *args.screen_dimensions)
else:
  from glscreen import OpenGLScreen
  screen = OpenGLScreen(boardState, *args.screen_dimensions)

boardState.addObserver(screen)

if args.use_cuda_strategy:
  from cudaboardstrategy import CudaUpdateStrategy
  update_strategy = CudaUpdateStrategy()
else:
  from pythonboardstrategy import StraightPythonUpdateStrategy
  update_strategy = StraightPythonUpdateStrategy()

startTime = time.time_ns()
nextTickTime = startTime + NANOS_PER_SECOND

updateCountAtLastPrint = 0
updateCount = 0

while True:
  boardState.update(update_strategy)

  updateCount += 1

  currentTime = time.time_ns()

  if currentTime >= nextTickTime:
      print("Update rate:", (updateCount - updateCountAtLastPrint) 
        / ((currentTime - startTime)/NANOS_PER_SECOND), "f/s")
      nextTickTime += NANOS_PER_SECOND
      startTime = currentTime
      updateCountAtLastPrint = updateCount
