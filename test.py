import pygame
from pygame.locals import *
from GlobalVariable import *
from GameOfLife import GameOfLife
import os


def load_image(filename, size):
    """
    Load an image file from the 'res' directory and scale it to the specified size.
    """
    image_path = os.path.join(IMAGE_REP, filename)
    image = pygame.image.load(image_path)
    image = pygame.transform.scale(image, size)
    return image


def draw_button_with_icon(surface, icon, rect, color=(28, 40, 51, 0)):
    """
    Draws a button with an icon.
    """
    mouse_pos = pygame.mouse.get_pos()
    pygame.draw.rect(surface, color, rect)
    surface.blit(icon, (rect.x + (rect.width - icon.get_width()) // 2,
                        rect.y + (rect.height - icon.get_height()) // 2))


def main():
    # Initialisation de Pygame
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Conway's Game of Life")

    # Création du jeu
    game = GameOfLife()
    clock = pygame.time.Clock()

    # Dimensions de la barre d'outils
    toolbar_height = 40
    toolbar_rect = pygame.Rect(0, 0, WINDOW_WIDTH, toolbar_height)

    # Charger les icônes depuis le répertoire 'res'
    play_icon = load_image(PLAY_BTN, (30, 30))
    pause_icon = load_image(PAUSE_BTN, (30, 30))
    reset_icon = load_image(RESET_BTN, (30, 30))

    play_icon_hover = load_image(PLAY_BTN_HOVER, (30, 30))
    pause_icon_hover = load_image(PAUSE_BTN_HOVER, (30, 30))
    reset_icon_hover = load_image(RESET_BTN_HOVER, (30, 30))

    # Création des boutons de la barre d'outils
    button_width = 100
    button_height = 30
    toggle_button_rect = pygame.Rect(10, 5, button_width, button_height)
    reset_button_rect = pygame.Rect(120, 5, button_width, button_height)

    running = True
    game_running = False  # Variable pour suivre si le jeu est en cours
    paused = False  # Variable pour suivre si le jeu est en pause

    while running:
        mouse_pos = pygame.mouse.get_pos()  # Récupérer la position de la souris
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
                    if toggle_button_rect.collidepoint(x, y):
                        if not game_running:
                            game_running = True
                            paused = False
                        else:
                            paused = not paused
                    elif reset_button_rect.collidepoint(x, y):
                        game.grid.clear()
                    else:
                        row = (y - toolbar_height + game.offset_y) // (CELL_SIZE * game.zoom_level)
                        col = (x + game.offset_x) // (CELL_SIZE * game.zoom_level)
                        game.toggle_cell(row, col)  # Toggle the cell at the mouse position
                elif event.button == 4:  # Scroll up
                    game.zoom_level = min(game.zoom_level + 1, 10)  # Increase zoom level, max 10
                elif event.button == 5:  # Scroll down
                    game.zoom_level = max(game.zoom_level - 1, 1)  # Decrease zoom level, min 1

        if game_running and not paused:
            game.update_grid()  # Update the grid if the game is running and not paused

        # Dessiner la barre d'outils
        screen.fill(BACKGROUND_COLOR)
        pygame.draw.rect(screen, BLACK, toolbar_rect)

        # Dessiner les boutons avec gestion du survol
        if toggle_button_rect.collidepoint(mouse_pos):
            toggle_icon = pause_icon_hover if game_running and not paused else play_icon_hover
        else:
            toggle_icon = pause_icon if game_running and not paused else play_icon

        if reset_button_rect.collidepoint(mouse_pos):
            reset_icon = reset_icon_hover
        else:
            reset_icon = reset_icon

        draw_button_with_icon(screen, toggle_icon, toggle_button_rect)
        draw_button_with_icon(screen, reset_icon, reset_button_rect)

        # Dessiner la grille
        cell_size_zoomed = CELL_SIZE * game.zoom_level
        start_row = max(0, (0 - game.offset_y) // cell_size_zoomed)
        end_row = (WINDOW_HEIGHT - toolbar_height - game.offset_y) // cell_size_zoomed + 1
        start_col = max(0, (0 - game.offset_x) // cell_size_zoomed)
        end_col = (WINDOW_WIDTH - game.offset_x) // cell_size_zoomed + 1

        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                cell_x = col * cell_size_zoomed - game.offset_x
                cell_y = row * cell_size_zoomed - game.offset_y + toolbar_height
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
