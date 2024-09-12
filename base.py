import pygame
from pygame.locals import *
from GlobalVariable import *
from GameOfLife import GameOfLife
from rules import apply_rules_for_alive_cell, apply_rules_for_dead_cell


def main():
    # Initialisation de Pygame
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Conway's Game of Life")

    # Création du jeu
    game = GameOfLife()
    clock = pygame.time.Clock()

    running = True
    game_running = False  # Variable pour suivre si le jeu est en cours
    paused = False  # Variable pour suivre si le jeu est en pause

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    if game_running:
                        paused = not paused  # Toggle pause state
                    else:
                        game_running = True  # Start the game
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    x, y = pygame.mouse.get_pos()
                    row = (y + game.offset_y) // (CELL_SIZE * game.zoom_level)
                    col = (x + game.offset_x) // (CELL_SIZE * game.zoom_level)
                    game.toggle_cell(row, col)  # Toggle the cell at the mouse position
                elif event.button == 4:  # Scroll up
                    game.zoom_level = min(game.zoom_level + 1, 10)  # Increase zoom level, max 10
                elif event.button == 5:  # Scroll down
                    game.zoom_level = max(game.zoom_level - 1, 1)  # Decrease zoom level, min 1

        if game_running and not paused:
            game.update_grid()  # Update the grid if the game is running and not paused

        # Dessiner la grille
        screen.fill(BACKGROUND_COLOR)

        # Calculer les coordonnées de la région visible
        cell_size_zoomed = CELL_SIZE * game.zoom_level
        start_row = max(0, (0 - game.offset_y) // cell_size_zoomed)
        end_row = (WINDOW_HEIGHT - game.offset_y) // cell_size_zoomed + 1
        start_col = max(0, (0 - game.offset_x) // cell_size_zoomed)
        end_col = (WINDOW_WIDTH - game.offset_x) // cell_size_zoomed + 1

        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                cell_x = col * cell_size_zoomed - game.offset_x
                cell_y = row * cell_size_zoomed - game.offset_y
                cell_rect = pygame.Rect(cell_x, cell_y, cell_size_zoomed, cell_size_zoomed)

                # Dessiner la cellule
                color = WHITE if game.grid[(row, col)] else BLACK
                pygame.draw.rect(screen, color, cell_rect)

                # Dessiner les lignes de la grille
                pygame.draw.rect(screen, GRID_COLOR, cell_rect, 1)  # 1 pixel wide line

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
