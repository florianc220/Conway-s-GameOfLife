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
    Draw the coordinates on the toolbar (cellule au centre de l'écran).
    """
    coord_text = f"X: {int(x)}, Y: {int(y)}"
    text_surface = font.render(coord_text, True, color)
    surface.blit(text_surface, (WINDOW_WIDTH - text_surface.get_width() - 10, 10))


def draw_slider(surface, x, y, width, value, min_val, max_val, font, color=(255, 255, 255)):
    """
    Dessine un slider horizontal avec la valeur actuelle.
    """
    track_rect = pygame.Rect(x, y + 12, width, 4)
    pygame.draw.rect(surface, (100, 100, 100), track_rect)

    ratio = (value - min_val) / (max_val - min_val)
    handle_x = int(x + ratio * width)
    pygame.draw.circle(surface, color, (handle_x, y + 14), 7)

    label = font.render(f"{value} gen/s", True, color)
    surface.blit(label, (x + width + 8, y + 5))


def main():
    # Initialisation de Pygame
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(GAME_TITLE)
    font = pygame.font.Font(None, 28)

    # Création du jeu
    game = GameOfLife()
    game.offset_x = 0.0
    game.offset_y = 0.0
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

    # Slider de vitesse
    slider_x = 145
    slider_width = 120
    gen_per_sec = DEFAULT_GEN_PER_SEC
    sliding = False

    # Compteur de générations + accumulateur de temps simulation
    generation = 0
    last_update = 0  # timestamp de la dernière génération calculée (ms)

    running = True
    game_running = False
    paused = False

    # Flèches directionnelles
    move_left = move_right = move_up = move_down = False

    # Drag clic droit
    dragging = False
    drag_start_x = 0
    drag_start_y = 0
    drag_offset_start_x = 0.0
    drag_offset_start_y = 0.0

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    if not game_running:
                        game_running = True
                        paused = False
                        pygame.display.set_caption(f"{GAME_TITLE} (running)")
                    else:
                        paused = not paused
                        pygame.display.set_caption(f"{GAME_TITLE} (paused)" if paused else f"{GAME_TITLE} (running)")
                elif event.key == K_DELETE:  # Suppr = reset
                    game.grid.clear()
                    game_running = False
                    paused = False
                    generation = 0
                    pygame.display.set_caption(GAME_TITLE)
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
                if event.button == 1:
                    x, y = event.pos
                    slider_rect = pygame.Rect(slider_x, 6, slider_width, 28)
                    if slider_rect.collidepoint(x, y):
                        sliding = True
                        ratio = max(0.0, min(1.0, (x - slider_x) / slider_width))
                        gen_per_sec = max(MIN_GEN_PER_SEC, round(MIN_GEN_PER_SEC + ratio * (MAX_GEN_PER_SEC - MIN_GEN_PER_SEC)))
                    elif toggle_button_rect.collidepoint(x, y):
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
                        generation = 0
                        pygame.display.set_caption(GAME_TITLE)
                    elif y > toolbar_height:
                        cell_size_zoomed = CELL_SIZE * game.zoom_level
                        row = int((y - toolbar_height + game.offset_y) // cell_size_zoomed)
                        col = int((x + game.offset_x) // cell_size_zoomed)
                        game.toggle_cell(row, col)

                elif event.button == 3:  # Clic droit — début du drag caméra
                    dragging = True
                    drag_start_x, drag_start_y = event.pos
                    drag_offset_start_x = game.offset_x
                    drag_offset_start_y = game.offset_y

                elif event.button == 4:  # Scroll up — zoom in
                    game.zoom_level = min(game.zoom_level + 1, 10)

                elif event.button == 5:  # Scroll down — zoom out
                    game.zoom_level = max(game.zoom_level - 1, 1)

            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    sliding = False
                elif event.button == 3:
                    dragging = False

            elif event.type == MOUSEMOTION:
                if dragging:
                    dx = event.pos[0] - drag_start_x
                    dy = event.pos[1] - drag_start_y
                    game.offset_x = drag_offset_start_x - dx
                    game.offset_y = drag_offset_start_y - dy
                if sliding:
                    x = event.pos[0]
                    ratio = max(0.0, min(1.0, (x - slider_x) / slider_width))
                    gen_per_sec = max(MIN_GEN_PER_SEC, round(MIN_GEN_PER_SEC + ratio * (MAX_GEN_PER_SEC - MIN_GEN_PER_SEC)))

        # Déplacement fluide avec les flèches (indépendant de la vitesse de simulation)
        if move_left:
            game.offset_x -= MOVE_SPEED
        if move_right:
            game.offset_x += MOVE_SPEED
        if move_up:
            game.offset_y -= MOVE_SPEED
        if move_down:
            game.offset_y += MOVE_SPEED

        # Simulation cadencée indépendamment du rendu
        current_time = pygame.time.get_ticks()
        if game_running and not paused:
            if current_time - last_update >= 1000 // gen_per_sec:
                game.update_grid()
                generation += 1
                last_update = current_time

        # Fond noir
        screen.fill(BLACK)

        # Calcul de la zone visible
        cell_size_zoomed = CELL_SIZE * game.zoom_level
        start_row = int(game.offset_y // cell_size_zoomed) - 1
        end_row = int((WINDOW_HEIGHT - toolbar_height + game.offset_y) // cell_size_zoomed) + 1
        start_col = int(game.offset_x // cell_size_zoomed) - 1
        end_col = int((WINDOW_WIDTH + game.offset_x) // cell_size_zoomed) + 1

        # Dessiner uniquement les cellules vivantes visibles
        for (row, col) in game.grid:
            if start_row <= row <= end_row and start_col <= col <= end_col:
                cell_x = col * cell_size_zoomed - game.offset_x
                cell_y = row * cell_size_zoomed - game.offset_y + toolbar_height
                pygame.draw.rect(screen, WHITE, (cell_x, cell_y, cell_size_zoomed - 1, cell_size_zoomed - 1))

        # Lignes de grille (seulement si zoom suffisant)
        if cell_size_zoomed >= 4:
            for col in range(start_col, end_col + 1):
                x = col * cell_size_zoomed - game.offset_x
                pygame.draw.line(screen, GRID_COLOR, (x, toolbar_height), (x, WINDOW_HEIGHT))
            for row in range(start_row, end_row + 1):
                y = row * cell_size_zoomed - game.offset_y + toolbar_height
                pygame.draw.line(screen, GRID_COLOR, (0, y), (WINDOW_WIDTH, y))

        # Barre d'outils
        pygame.draw.rect(screen, BLACK, toolbar_rect)

        toggle_icon = pause_icon if game_running and not paused else play_icon
        draw_button_with_icon(screen, toggle_icon, toggle_button_rect)
        draw_button_with_icon(screen, reset_icon, reset_button_rect)

        # Slider de vitesse
        draw_slider(screen, slider_x, 6, slider_width, gen_per_sec, MIN_GEN_PER_SEC, MAX_GEN_PER_SEC, font)

        # Compteur de générations
        gen_text = font.render(f"Gen: {generation}", True, (255, 255, 255))
        screen.blit(gen_text, (slider_x + slider_width + 90, 10))

        # Coordonnées centre écran
        center_col = int((game.offset_x + WINDOW_WIDTH / 2) / cell_size_zoomed)
        center_row = int((game.offset_y + (WINDOW_HEIGHT - toolbar_height) / 2) / cell_size_zoomed)
        draw_coordinates(screen, center_col, center_row, font)

        pygame.display.flip()
        clock.tick(60)  # rendu toujours à 60 FPS, indépendant de la simulation

    pygame.quit()


if __name__ == "__main__":
    main()
