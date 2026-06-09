from GlobalVariable import *
from rules import apply_rules_for_alive_cell, apply_rules_for_dead_cell


class GameOfLife:
    def __init__(self):
        """
        Initialization of an infinite grid with a set.
        Only stores living cells as (row, col) tuples.
        """
        self.grid = set()  # Only stores living cells (as (row, col) tuples)
        self.offset_x = 0
        self.offset_y = 0
        self.zoom_level = 2  # Initial zoom level

    def count_alive_neighbors(self, row, col):
        """
        Counts the number of living neighbors around a given cell (row, col).
        """
        total_alive = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if not (i == 0 and j == 0):  # Ignore the cell itself
                    if (row + i, col + j) in self.grid:
                        total_alive += 1

        return total_alive

    def update_grid(self):
        """
        Update the grid according to the rules defined in rules.py
        """
        new_grid = set()
        cells_to_check = set(self.grid)  # Start with all cells that are currently alive

        for (row, col) in self.grid:
            cells_to_check.update([(row + i, col + j) for i in range(-1, 2) for j in range(-1, 2)])

        for (row, col) in cells_to_check:
            alive_neighbors = self.count_alive_neighbors(row, col)

            if (row, col) in self.grid:  # Living cell
                if apply_rules_for_alive_cell(alive_neighbors):
                    new_grid.add((row, col))
            else:  # Dead cell
                if apply_rules_for_dead_cell(alive_neighbors):
                    new_grid.add((row, col))

        self.grid = new_grid  # Update the grid with the new states

    def toggle_cell(self, row, col):
        """
        Allows toggling a cell (useful for mouse interaction).
        """
        if (row, col) in self.grid:
            self.grid.discard((row, col))
        else:
            self.grid.add((row, col))