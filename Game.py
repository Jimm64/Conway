import argparse
import BoardState
import Screen
import sys

arg_parser = argparse.ArgumentParser("Conway's Game of Life")

arg_parser.add_argument("--cell-dimensions", dest="cell_dimensions", nargs=2, required=False, type=int, default=[100,100], help="Number of cell columns and rows")
arg_parser.add_argument("--screen-dimensions", dest="screen_dimensions", nargs=2, required=False, type=int, default=[400,400], help="Screen width and height")
args = arg_parser.parse_args()

boardState = BoardState.BoardState(*args.cell_dimensions)
boardState.randomizeState()

screen = Screen.GlScreen(boardState, *args.screen_dimensions)

screen.loop()

