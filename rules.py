# rules.py

def apply_rules_for_alive_cell(alive_neighbors):
    """
    Applies the rules for a living cell.
    Returns True if the cell should stay alive, False if it should die.

    Rules for a living cell:
    - A living cell with fewer than 2 living neighbors dies (underpopulation).
    - A living cell with more than 3 living neighbors dies (overpopulation).
    - A living cell with 2 or 3 living neighbors survives (normal conditions).
    """
    if alive_neighbors < 2 or alive_neighbors > 3:
        return False  # The cell dies due to underpopulation or overpopulation
    return True  # The cell survives


def apply_rules_for_dead_cell(alive_neighbors):
    """
    Applies the rules for a dead cell.
    Returns True if the cell should become alive, False if it should remain dead.

    Rule for a dead cell:
    - A dead cell with exactly 3 living neighbors becomes alive (reproduction).
    """
    if alive_neighbors == 3:
        return True  # The cell becomes alive due to reproduction
    return False  # The cell remains dead
