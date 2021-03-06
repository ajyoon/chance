#!/usr/bin/env python
"""
Conway's Game Of Life using fuzzy values everywhere.

This is an example of some of the things ``blur.soft`` can do.
"""

# Python 2/3 agnostic tk import
try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk

from blur import soft


class SoftCell:
    """
    A cell with a bool value and a probability to accept
    changes according to the Rules of Life
    """
    def __init__(self, value, allow_change):
        """
        Args:
            value (bool): The starting value of this cell
            allow_change (SoftFloat): the probability to accept
                changes according to the Rules of Life
        """
        self.color_alive = soft.SoftColor(([(255, 5), (200, 0)],),
                                          ([(255, 5), (200, 0)],),
                                          ([(255, 5), (200, 0)],))
        self.color_dead = soft.SoftColor(0, 0, 0)
        self.value = value
        self.allow_change = allow_change


def update_state(world):
    """
    Increment the world state, determining which cells live, die, or appear.

    Args:
        world (list[list]): A square matrix of cells

    Returns: None
    """

    world_size = len(world)

    def wrap(index):
        """Wrap an index around the other end of the array"""
        return index % world_size

    for x in range(world_size):
        for y in range(world_size):
            # Decide if this node cares about the rules right now
            if not world[x][y].allow_change.get():
                continue
            live_neighbor_count = sum([
                world[wrap(x)][wrap(y + 1)].value,
                world[wrap(x + 1)][wrap(y + 1)].value,
                world[wrap(x + 1)][wrap(y)].value,
                world[wrap(x + 1)][wrap(y - 1)].value,
                world[wrap(x)][wrap(y-1)].value,
                world[wrap(x - 1)][wrap(y - 1)].value,
                world[wrap(x - 1)][wrap(y)].value,
                world[wrap(x - 1)][wrap(y + 1)].value
            ])
            if world[x][y].value:
                # Any live cell with fewer than two live neighbours dies
                # Any live cell with more than three live neighbours dies
                # Any live cell with two or three live neighbours lives
                if not (live_neighbor_count == 2 or live_neighbor_count == 3):
                    world[x][y].value = False
            else:
                # Any dead cell with exactly three live neighbours comes alive
                if live_neighbor_count == 3:
                    world[x][y].value = True


def click_event(event):
    """On click, bring the cell under the cursor to Life"""
    grid_x_coord = int(divmod(event.x, cell_size)[0])
    grid_y_coord = int(divmod(event.y, cell_size)[0])
    world[grid_x_coord][grid_y_coord].value = True
    color = world[x][y].color_alive.get_as_hex()
    canvas.itemconfig(canvas_grid[grid_x_coord][grid_y_coord], fill=color)


def draw_canvas():
    """Render the tkinter canvas based on the state of ``world``"""
    for x in range(len(world)):
        for y in range(len(world[x])):
            if world[x][y].value:
                color = world[x][y].color_alive.get_as_hex()
            else:
                color = world[x][y].color_dead.get_as_hex()
            canvas.itemconfig(canvas_grid[x][y], fill=color)


def refresh_canvas_and_state():
    """Callback for the main loop."""
    update_state(world)
    draw_canvas()
    # Refresh every 100 ms
    tk_host.after(100, refresh_canvas_and_state)


if __name__ == '__main__':
    # Initialize tk and canvas
    tk_host = tk.Tk()
    CANVAS_WIDTH = 640
    CANVAS_HEIGHT = 640
    canvas = tk.Canvas(tk_host,
                       width=CANVAS_WIDTH,
                       height=CANVAS_HEIGHT)
    canvas.pack()
    # Fill the world
    CELLS_PER_ROW = 80
    allow_change_weight = soft.SoftBool(0.4)
    starting_value = soft.SoftBool(0)
    world = [[None] * CELLS_PER_ROW for _ in range(CELLS_PER_ROW)]
    for x in range(CELLS_PER_ROW):
        for y in range(CELLS_PER_ROW):
            world[x][y] = SoftCell(starting_value.get(),
                                   allow_change_weight)
    # Create canvas grid
    cell_size = 640 / CELLS_PER_ROW
    canvas_grid = [[None] * CELLS_PER_ROW for _ in range(CELLS_PER_ROW)]
    for x in range(len(world)):
        for y in range(len(world[x])):
            canvas_grid[x][y] = canvas.create_rectangle(
                                    x * cell_size,
                                    y * cell_size,
                                    (x * cell_size) + cell_size,
                                    (y * cell_size) + cell_size,
                                    fill="#808080")
    # Lift off!
    tk_host.bind('<Button 1>', click_event)
    tk_host.bind('<B1-Motion>', click_event)
    refresh_canvas_and_state()
    print('Click anywhere on the window to create Life!')
    tk_host.mainloop()
