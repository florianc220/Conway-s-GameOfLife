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
    pygame.draw.rect(surface, color, rect)
    surface.blit(icon, (rect.x + (rect.width - icon.get_width()) // 2,
                        rect.y + (rect.height - icon.get_height()) // 2))


def draw_coordinates(surface, x, y, font, color=(255, 255, 255)):
    """
    Draw the coordinates on the toolbar.
    """
    coord_text = f"X: {x}, Y: {y}"
    text_surface = font.render(coord_text, True, color)
    surface.blit(text_surface, (WINDOW_WIDTH - text_surface.get_width() - 10, 10))


def main():
    # Initialisation de Pygame
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(GAME_TITLE)
    font = pygame.font.Font(None, 36)

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

    # Création des boutons de la barre d'outils
    button_width = 50
    button_height = 37
    toggle_button_rect = pygame.Rect(10, 5, button_width, button_height)
    reset_button_rect = pygame.Rect(75, 5, button_width, button_height)

    running = True
    game_running = False  # Variable pour suivre si le jeu est en cours
    paused = False  # Variable pour suivre si le jeu est en pause

    # Variables pour suivre l'état des touches directionnelles
    move_left = move_right = move_up = move_down = False

    while running:
        mouse_pos = pygame.mouse.get_pos()  # Récupérer la position de la souris
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    if game_running:
                        paused = not paused  # Toggle pause state
                        pygame.display.set_caption(f"{GAME_TITLE} (paused)" if paused else f"{GAME_TITLE} (running)")
                    else:
                        game_running = True  # Start the game
                        pygame.display.set_caption(f"{GAME_TITLE} (running)")
                elif event.key == K_LEFT:
                    move_left = True
                elif event.key == K_RIGHT:
                    move_right = True
                elif event.key == K_UP:
                    move_up = True
                elif event.key == K_DOWN:
                    move_down = True
            elif event.type == KEYUP:
                if event.key == K_LEFT:
                    move_left = False
                elif event.key == K_RIGHT:
                    move_right = False
                elif event.key == K_UP:
                    move_up = False
                elif event.key == K_DOWN:
                    move_down = False
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    x, y = pygame.mouse.get_pos()
                    if toggle_button_rect.collidepoint(x, y):
                        if not game_running:
                            game_running = True
                            paused = False
                            pygame.display.set_caption(f"{GAME_TITLE} (running)")
                        else:
                            paused = not paused
                            pygame.display.set_caption(f"{GAME_TITLE} (paused)" if paused else f"{GAME_TITLE} (running)")
                    elif reset_button_rect.collidepoint(x, y):
                        game.grid.clear()
                        game_running = False
                        paused = False
                        pygame.display.set_caption(GAME_TITLE)
                    else:
                        row = (y - toolbar_height + game.offset_y) // (CELL_SIZE * game.zoom_level)
                        col = (x + game.offset_x) // (CELL_SIZE * game.zoom_level)
                        game.toggle_cell(row, col)  # Toggle the cell at the mouse position
                elif event.button == 4:  # Scroll up
                    game.zoom_level = min(game.zoom_level + 1, 10)  # Increase zoom level, max 10
                elif event.button == 5:  # Scroll down
                    game.zoom_level = max(game.zoom_level - 1, 1)  # Decrease zoom level, min 1

        # Mettre à jour les coordonnées en fonction de l'état des touches
        if move_left:
            game.offset_x -= CELL_SIZE * game.zoom_level
        if move_right:
            game.offset_x += CELL_SIZE * game.zoom_level
        if move_up:
            game.offset_y -= CELL_SIZE * game.zoom_level
        if move_down:
            game.offset_y += CELL_SIZE * game.zoom_level

        if game_running and not paused:
            game.update_grid()  # Update the grid if the game is running and not paused

        # Dessiner la barre d'outils
        screen.fill(BACKGROUND_COLOR)
        pygame.draw.rect(screen, BLACK, toolbar_rect)

        toggle_icon = pause_icon if game_running and not paused else play_icon
        reset_icon = reset_icon

        draw_button_with_icon(screen, toggle_icon, toggle_button_rect)
        draw_button_with_icon(screen, reset_icon, reset_button_rect)

        # Dessiner les coordonnées
        draw_coordinates(screen, game.offset_x, game.offset_y, font)

        # Dessiner la grille
        cell_size_zoomed = CELL_SIZE * game.zoom_level
        start_row = (0 - game.offset_y) // cell_size_zoomed
        end_row = (WINDOW_HEIGHT - toolbar_height - game.offset_y) // cell_size_zoomed + 1
        start_col = (0 - game.offset_x) // cell_size_zoomed
        end_col = (WINDOW_WIDTH - game.offset_x) // cell_size_zoomed + 1

        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                cell_x = col * cell_size_zoomed - game.offset_x
                cell_y = row * cell_size_zoomed - game.offset_y + toolbar_height
                cell_rect = pygame.Rect(cell_x, cell_y, cell_size_zoomed, cell_size_zoomed)

                # Dessiner la cellule
                color = WHITE if game.grid.get((row, col), False) else BLACK
                pygame.draw.rect(screen, color, cell_rect)

                # Dessiner les lignes de la grille
                pygame.draw.rect(screen, GRID_COLOR, cell_rect, 1)  # 1 pixel wide line

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()