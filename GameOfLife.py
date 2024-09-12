from collections import defaultdict
from GlobalVariable import *
from rules import apply_rules_for_alive_cell, apply_rules_for_dead_cell


class GameOfLife:
    def __init__(self):
        """
        Initialization of an infinite grid with default dictionary.
        """
        self.grid = defaultdict(bool)  # Only stores living cells
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
                    total_alive += self.grid[(row + i, col + j)]  # Directly access the dictionary

        return total_alive

    def update_grid(self):
        """
        Update the grid according to the rules defined in rules.py
        """
        new_grid = defaultdict(bool)
        cells_to_check = set(self.grid.keys())  # Start with all cells that are currently alive

        for (row, col) in self.grid:
            cells_to_check.update([(row + i, col + j) for i in range(-1, 2) for j in range(-1, 2)])

        for (row, col) in cells_to_check:
            alive_neighbors = self.count_alive_neighbors(row, col)

            if self.grid[(row, col)]:  # Living cell
                new_grid[(row, col)] = apply_rules_for_alive_cell(alive_neighbors)
            else:  # Dead cell
                new_grid[(row, col)] = apply_rules_for_dead_cell(alive_neighbors)

        self.grid = new_grid  # Update the grid with the new states

    def toggle_cell(self, row, col):
        """
        Allows toggling a cell (useful for mouse interaction).
        """
        self.grid[(row, col)] = not self.grid[(row, col)]  # Toggle the cell state (True <-> False)
