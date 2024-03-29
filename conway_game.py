from board.boardstate import BoardState
import argparse
import sys
import time

# Play Conway's game of life.

NANOS_PER_SECOND = 1000000000

arg_parser = argparse.ArgumentParser("Conway's Game of Life")

arg_parser.add_argument("--cell-dimensions", dest="cell_dimensions", nargs=2, required=False, type=int, default=[100,100], help="Number of cell columns and rows")
arg_parser.add_argument("--screen-dimensions", dest="screen_dimensions", nargs=2, required=False, type=int, default=[400,400], help="Screen width and height")
arg_parser.add_argument("--cuda", action="store_true", dest="use_cuda_strategy", required=False, default=False, help="Use CUDA to update board state.")
arg_parser.add_argument("--display-as-text", action="store_true", dest="use_text_display", required=False, default=False, help="Display board as text instead of using OpenGL.")
arg_parser.add_argument("--display-as-ansi-text", action="store_true", dest="use_ansi_text_display", required=False, default=False, help="Display board as text, using ANSI control characters.")
arg_parser.add_argument("--runtime", dest="run_time", nargs=1, required=False, type=int, default=None, help="Stop after the given number of seconds")
args = arg_parser.parse_args()

print_stats = False

board_state = BoardState(*args.cell_dimensions)
board_state.randomize_state()

opengl_draw_state = None

# Set desired method of displaying the board state based on commandline options.
# (framerate stats not displayed for text displays, since both print to the console)
if args.use_ansi_text_display:
  from screen.textscreen import AnsiTextScreen
  screen = AnsiTextScreen(*args.screen_dimensions)
elif args.use_text_display:
  from screen.textscreen import TextScreen
  screen = TextScreen(*args.screen_dimensions)
else:
  from screen.glscreen import OpenGLScreen
  print_stats = True
  screen = OpenGLScreen(*args.screen_dimensions)
  opengl_draw_state = screen.get_opengl_draw_state()

# Ensure our method of display is notified as the board state changes.
board_state.add_observer(screen)

# Run CUDA kernels to update the board and/or display, if indicated to do so.
if args.use_cuda_strategy:
  from board.cudaboardstrategy import CudaUpdateStrategy
  update_strategy = CudaUpdateStrategy(opengl_draw_state=opengl_draw_state)
else:
  from board.pythonboardstrategy import StraightPythonUpdateStrategy
  update_strategy = StraightPythonUpdateStrategy(opengl_draw_state=opengl_draw_state)

original_start_time = start_time = time.time_ns()
next_report_time = start_time + NANOS_PER_SECOND

update_count_at_last_report = 0
update_count = 0

while True:
  board_state.update(update_strategy)

  update_count += 1

  current_time = time.time_ns()

  # Periodically provide update rate statistics, if specified.
  if print_stats and current_time >= next_report_time:

    print("Update rate:", (update_count - update_count_at_last_report) 
      / ((current_time - start_time)/NANOS_PER_SECOND), "f/s")
    next_report_time += NANOS_PER_SECOND
    start_time = current_time
    update_count_at_last_report = update_count

  # Stop if a runtime was specified and it has elapsed.
  if args.run_time is not None and current_time >= original_start_time + args.run_time[0] * NANOS_PER_SECOND:
    sys.exit(0)
