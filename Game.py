import argparse
import BoardState
import Screen
import sys

arg_parser = argparse.ArgumentParser("Conway's Game of Life")

arg_parser.add_argument("--cell-dimensions", dest="cell_dimensions", nargs=2, required=False, type=int, default=[100,100], help="Number of cell columns and rows")
arg_parser.add_argument("--screen-dimensions", dest="screen_dimensions", nargs=2, required=False, type=int, default=[400,400], help="Screen width and height")
arg_parser.add_argument("--cuda", action="store_true", dest="use_cuda_strategy", required=False, default=False, help="Use CUDA to update board state.")
arg_parser.add_argument("--display-as-text", action="store_true", dest="use_text_display", required=False, default=False, help="Display board as text instead of using OpenGL.")
args = arg_parser.parse_args()

boardState = BoardState.BoardState(*args.cell_dimensions)
boardState.randomizeState()

if args.use_text_display:
  screen = Screen.TextScreen(boardState, *args.screen_dimensions)
else:
  screen = Screen.OpenGLScreen(boardState, *args.screen_dimensions)

if args.use_cuda_strategy:
  update_strategy = BoardState.CudaUpdateStrategy()
else:
  update_strategy = BoardState.StraightPythonUpdateStrategy()

screen.loop(update_strategy)

