import pygame
import json
import os
import tkinter as tk
from tkinter import filedialog
from pygame.locals import *
from GlobalVariable import *
from GameOfLife import GameOfLife

root = tk.Tk()
root.withdraw()


def load_image(filename, size):
    image_path = os.path.join(IMAGE_REP, filename)
    image = pygame.image.load(image_path)
    image = pygame.transform.scale(image, size)
    return image


def draw_button_with_icon(surface, icon, rect, color=(28, 40, 51, 0)):
    pygame.draw.rect(surface, color, rect)
    surface.blit(icon, (rect.x + (rect.width - icon.get_width()) // 2,
                        rect.y + (rect.height - icon.get_height()) // 2))


def draw_coordinates(surface, x, y, font, color=(255, 255, 255)):
    coord_text = f"X: {int(x)}, Y: {int(y)}"
    text_surface = font.render(coord_text, True, color)
    surface.blit(text_surface, (WINDOW_WIDTH - text_surface.get_width() - 10, 10))


def draw_slider(surface, x, y, width, value, min_val, max_val, font, color=(255, 255, 255)):
    track_rect = pygame.Rect(x, y + 12, width, 4)
    pygame.draw.rect(surface, (100, 100, 100), track_rect)
    ratio = (value - min_val) / (max_val - min_val)
    handle_x = int(x + ratio * width)
    pygame.draw.circle(surface, color, (handle_x, y + 14), 7)
    label = font.render(f"{value} gen/s", True, color)
    surface.blit(label, (x + width + 8, y + 5))


def rotate_cw(cells):
    if not cells:
        return cells
    rotated = [(dc, -dr) for (dr, dc) in cells]
    min_r = min(r for r, c in rotated)
    min_c = min(c for r, c in rotated)
    return [(r - min_r, c - min_c) for r, c in rotated]


def rotate_ccw(cells):
    if not cells:
        return cells
    rotated = [(-dc, dr) for (dr, dc) in cells]
    min_r = min(r for r, c in rotated)
    min_c = min(c for r, c in rotated)
    return [(r - min_r, c - min_c) for r, c in rotated]


def flip_vertical(cells):
    if not cells:
        return cells
    max_r = max(r for r, c in cells)
    return [(max_r - r, c) for r, c in cells]


def flip_horizontal(cells):
    if not cells:
        return cells
    max_c = max(c for r, c in cells)
    return [(r, max_c - c) for r, c in cells]


def place_pattern(grid, ghost_cells, mouse_row, mouse_col):
    for (dr, dc) in ghost_cells:
        grid.add((mouse_row + dr, mouse_col + dc))


def copy_selection(grid, sel_start, sel_end):
    col_start = min(sel_start[0], sel_end[0])
    col_end   = max(sel_start[0], sel_end[0])
    row_start = min(sel_start[1], sel_end[1])
    row_end   = max(sel_start[1], sel_end[1])
    cells = []
    for (row, col) in grid:
        if row_start <= row <= row_end and col_start <= col <= col_end:
            cells.append((row - row_start, col - col_start))
    return cells if cells else None


def remove_selection(grid, sel_start, sel_end):
    col_start = min(sel_start[0], sel_end[0])
    col_end   = max(sel_start[0], sel_end[0])
    row_start = min(sel_start[1], sel_end[1])
    row_end   = max(sel_start[1], sel_end[1])
    to_remove = {(row, col) for (row, col) in grid
                 if row_start <= row <= row_end and col_start <= col <= col_end}
    grid -= to_remove


def save_pattern(grid, sel_start, sel_end, last_dir):
    col_start = min(sel_start[0], sel_end[0])
    col_end   = max(sel_start[0], sel_end[0])
    row_start = min(sel_start[1], sel_end[1])
    row_end   = max(sel_start[1], sel_end[1])
    cells = []
    for (row, col) in grid:
        if row_start <= row <= row_end and col_start <= col <= col_end:
            cells.append([col - col_start, row - row_start])
    if not cells:
        return last_dir
    filepath = filedialog.asksaveasfilename(
        initialdir=last_dir if last_dir else os.getcwd(),
        defaultextension=".cgol",
        filetypes=[("Conway Game of Life pattern", "*.cgol")],
        title="Sauvegarder le pattern"
    )
    if not filepath:
        return last_dir
    pattern = {
        "version": GAME_VERSION,
        "width":   col_end - col_start + 1,
        "height":  row_end - row_start + 1,
        "cells":   cells
    }
    with open(filepath, "w") as f:
        json.dump(pattern, f, indent=2)
    return os.path.dirname(filepath)


def load_pattern(last_dir):
    filepath = filedialog.askopenfilename(
        initialdir=last_dir if last_dir else os.getcwd(),
        filetypes=[("Conway Game of Life pattern", "*.cgol")],
        title="Charger un pattern"
    )
    if not filepath:
        return None, last_dir
    with open(filepath, "r") as f:
        pattern = json.load(f)
    cells = [(c[1], c[0]) for c in pattern["cells"]]
    return cells, os.path.dirname(filepath)


def commit_selection(edit_tool, game, sel_start, sel_end, last_dir, clipboard):
    ghost_cells = None
    if sel_start and sel_end:
        if edit_tool == 'save':
            last_dir = save_pattern(game.grid, sel_start, sel_end, last_dir)
            edit_tool = None
        elif edit_tool == 'copy':
            clipboard = copy_selection(game.grid, sel_start, sel_end)
            ghost_cells = list(clipboard) if clipboard else None
            edit_tool = 'paste' if ghost_cells else None
        elif edit_tool == 'remove':
            remove_selection(game.grid, sel_start, sel_end)
            edit_tool = None
    return last_dir, clipboard, ghost_cells, edit_tool


def main():
    pygame.init()

    # Plein écran fenêtré — prend toute la résolution du bureau
    info = pygame.display.Info()
    win_w, win_h = 1280, 720
    screen = pygame.display.set_mode((win_w, win_h), pygame.RESIZABLE)
    pygame.display.set_caption(GAME_TITLE)
    font = pygame.font.Font(None, 28)

    game = GameOfLife()
    game.offset_x = 0.0
    game.offset_y = 0.0
    clock = pygame.time.Clock()

    toolbar_height = 40
    toolbar_rect = pygame.Rect(0, 0, win_w, toolbar_height)

    # --- Icônes ---
    play_icon   = load_image(PLAY_BTN,    (30, 30))
    pause_icon  = load_image(PAUSE_BTN,   (30, 30))
    reset_icon  = load_image(RESET_BTN,   (30, 30))
    edit_icon   = load_image("edit.svg",  (24, 24))
    save_icon   = load_image("save.svg",  (24, 24))
    load_icon   = load_image("load.svg",  (24, 24))
    copy_icon   = load_image("copy.svg",  (24, 24))
    paste_icon  = load_image("paste.svg", (24, 24))
    cancel_icon = load_image("cancel.svg",(24, 24))

    remove_surf = pygame.Surface((24, 24), pygame.SRCALPHA)
    remove_surf.blit(cancel_icon, (0, 0))

    # --- Boutons mode normal ---
    button_w, button_h = 50, 37
    toggle_button_rect = pygame.Rect(10,  5, button_w, button_h)
    reset_button_rect  = pygame.Rect(75,  5, button_w, button_h)
    edit_button_rect   = pygame.Rect(140, 5, button_w, button_h)

    # --- Boutons mode edit (5 boutons — plus de cancel) ---
    edit_btn_w = 44
    save_button_rect   = pygame.Rect(5,                      5, edit_btn_w, button_h)
    load_button_rect   = pygame.Rect(5 +  (edit_btn_w + 2),  5, edit_btn_w, button_h)
    copy_button_rect   = pygame.Rect(5 + 2*(edit_btn_w + 2), 5, edit_btn_w, button_h)
    paste_button_rect  = pygame.Rect(5 + 3*(edit_btn_w + 2), 5, edit_btn_w, button_h)
    remove_button_rect = pygame.Rect(5 + 4*(edit_btn_w + 2), 5, edit_btn_w, button_h)

    # --- Slider ---
    slider_x     = 205
    slider_width = 120
    gen_per_sec  = DEFAULT_GEN_PER_SEC
    sliding      = False

    generation  = 0
    last_update = 0
    last_dir    = None
    clipboard   = None

    running      = True
    game_running = False
    paused       = False

    edit_mode   = False
    was_running = False
    edit_tool   = None

    selecting = False
    sel_start = None
    sel_end   = None
    ghost_cells = None

    move_left = move_right = move_up = move_down = False

    dragging            = False
    drag_start_x        = 0
    drag_start_y        = 0
    drag_offset_start_x = 0.0
    drag_offset_start_y = 0.0

    def enter_edit_mode():
        nonlocal edit_mode, was_running, game_running, edit_tool, ghost_cells, sel_start, sel_end
        edit_mode    = True
        was_running  = game_running and not paused
        game_running = False
        edit_tool    = None
        ghost_cells  = None
        sel_start = sel_end = None
        pygame.display.set_caption(f"{GAME_TITLE} (edit)")

    def exit_edit_mode():
        nonlocal edit_mode, edit_tool, ghost_cells, sel_start, sel_end, selecting, game_running, paused
        edit_mode   = False
        edit_tool   = None
        ghost_cells = None
        sel_start = sel_end = None
        selecting   = False
        if was_running:
            game_running = True
            paused = False
        pygame.display.set_caption(f"{GAME_TITLE} (running)" if game_running else GAME_TITLE)

    while running:
        current_time      = pygame.time.get_ticks()
        cell_size_zoomed  = CELL_SIZE * game.zoom_level
        mouse_x, mouse_y  = pygame.mouse.get_pos()

        mouse_col = int((mouse_x + game.offset_x) // cell_size_zoomed)
        mouse_row = int((mouse_y - toolbar_height + game.offset_y) // cell_size_zoomed)

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == VIDEORESIZE:
                win_w, win_h = event.w, event.h
                screen = pygame.display.set_mode((win_w, win_h), pygame.RESIZABLE)
                toolbar_rect = pygame.Rect(0, 0, win_w, toolbar_height)

            elif event.type == KEYDOWN:
                if edit_mode and ghost_cells is not None:
                    if event.key == K_RIGHT:
                        ghost_cells = rotate_cw(ghost_cells)
                    elif event.key == K_LEFT:
                        ghost_cells = rotate_ccw(ghost_cells)
                    elif event.key == K_UP:
                        ghost_cells = flip_vertical(ghost_cells)
                    elif event.key == K_DOWN:
                        ghost_cells = flip_horizontal(ghost_cells)
                    elif event.key == K_RETURN:
                        place_pattern(game.grid, ghost_cells, mouse_row, mouse_col)
                    elif event.key == K_ESCAPE:
                        ghost_cells = None
                        edit_tool   = None

                elif edit_mode and selecting and sel_start and sel_end:
                    if event.key == K_RETURN:
                        selecting = False
                        last_dir, clipboard, ghost_cells, edit_tool = commit_selection(
                            edit_tool, game, sel_start, sel_end, last_dir, clipboard)
                        sel_start = sel_end = None
                    elif event.key == K_ESCAPE:
                        selecting = False
                        sel_start = sel_end = None
                        edit_tool = None

                elif edit_mode:
                    if event.key == K_ESCAPE:
                        exit_edit_mode()
                    elif event.key == K_LEFT:
                        move_left = True
                    elif event.key == K_RIGHT:
                        move_right = True
                    elif event.key == K_UP:
                        move_up = True
                    elif event.key == K_DOWN:
                        move_down = True

                else:
                    if event.key == K_e:
                        enter_edit_mode()
                    elif event.key == K_ESCAPE:
                        running = False  # Echap en mode normal = quitter
                    elif event.key == K_SPACE:
                        if not game_running:
                            game_running = True
                            paused = False
                            pygame.display.set_caption(f"{GAME_TITLE} (running)")
                        else:
                            paused = not paused
                            pygame.display.set_caption(f"{GAME_TITLE} (paused)" if paused else f"{GAME_TITLE} (running)")
                    elif event.key == K_DELETE:
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
                x, y = event.pos

                if event.button == 1:
                    if y <= toolbar_height:
                        if not edit_mode:
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
                                generation = 0
                                pygame.display.set_caption(GAME_TITLE)
                            elif edit_button_rect.collidepoint(x, y):
                                enter_edit_mode()
                            else:
                                slider_rect = pygame.Rect(slider_x, 6, slider_width, 28)
                                if slider_rect.collidepoint(x, y):
                                    sliding = True
                                    ratio = max(0.0, min(1.0, (x - slider_x) / slider_width))
                                    gen_per_sec = max(MIN_GEN_PER_SEC, round(MIN_GEN_PER_SEC + ratio * (MAX_GEN_PER_SEC - MIN_GEN_PER_SEC)))
                        else:
                            if save_button_rect.collidepoint(x, y):
                                edit_tool = 'save'
                                ghost_cells = None
                                sel_start = sel_end = None
                                selecting = False
                            elif load_button_rect.collidepoint(x, y):
                                edit_tool = 'load'
                                sel_start = sel_end = None
                                selecting = False
                                cells, last_dir = load_pattern(last_dir)
                                ghost_cells = cells
                            elif copy_button_rect.collidepoint(x, y):
                                edit_tool = 'copy'
                                ghost_cells = None
                                sel_start = sel_end = None
                                selecting = False
                            elif paste_button_rect.collidepoint(x, y):
                                if clipboard:
                                    edit_tool   = 'paste'
                                    ghost_cells = list(clipboard)
                            elif remove_button_rect.collidepoint(x, y):
                                edit_tool = 'remove'
                                ghost_cells = None
                                sel_start = sel_end = None
                                selecting = False

                    elif y > toolbar_height:
                        if edit_mode:
                            if edit_tool in ('save', 'copy', 'remove'):
                                selecting = True
                                sel_start = (mouse_col, mouse_row)
                                sel_end   = (mouse_col, mouse_row)
                            elif edit_tool in ('load', 'paste') and ghost_cells is not None:
                                place_pattern(game.grid, ghost_cells, mouse_row, mouse_col)
                        else:
                            row = int((y - toolbar_height + game.offset_y) // cell_size_zoomed)
                            col = int((x + game.offset_x) // cell_size_zoomed)
                            game.toggle_cell(row, col)

                elif event.button == 3:
                    dragging = True
                    drag_start_x, drag_start_y = event.pos
                    drag_offset_start_x = game.offset_x
                    drag_offset_start_y = game.offset_y

                elif event.button == 4:
                    game.zoom_level = min(game.zoom_level + 1, 10)
                elif event.button == 5:
                    game.zoom_level = max(game.zoom_level - 1, 1)

            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    sliding = False
                    if selecting and sel_start and sel_end:
                        selecting = False
                        last_dir, clipboard, ghost_cells, edit_tool = commit_selection(
                            edit_tool, game, sel_start, sel_end, last_dir, clipboard)
                        sel_start = sel_end = None
                elif event.button == 3:
                    dragging = False

            elif event.type == MOUSEMOTION:
                if dragging:
                    dx = event.pos[0] - drag_start_x
                    dy = event.pos[1] - drag_start_y
                    game.offset_x = drag_offset_start_x - dx
                    game.offset_y = drag_offset_start_y - dy
                if sliding:
                    ratio = max(0.0, min(1.0, (event.pos[0] - slider_x) / slider_width))
                    gen_per_sec = max(MIN_GEN_PER_SEC, round(MIN_GEN_PER_SEC + ratio * (MAX_GEN_PER_SEC - MIN_GEN_PER_SEC)))
                if selecting and sel_start:
                    sel_end = (mouse_col, mouse_row)

        # --- Déplacement caméra ---
        if ghost_cells is None:
            if move_left:
                game.offset_x -= MOVE_SPEED
            if move_right:
                game.offset_x += MOVE_SPEED
            if move_up:
                game.offset_y -= MOVE_SPEED
            if move_down:
                game.offset_y += MOVE_SPEED

        # --- Simulation ---
        if game_running and not paused:
            if current_time - last_update >= 1000 // gen_per_sec:
                game.update_grid()
                generation += 1
                last_update = current_time

        # --- Curseur ---
        if edit_mode and edit_tool in ('save', 'copy', 'remove', 'load', 'paste'):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        # =================== RENDU ===================
        screen.fill(BLACK)

        cell_size_zoomed = CELL_SIZE * game.zoom_level
        start_row = int(game.offset_y // cell_size_zoomed) - 1
        end_row   = int((win_h - toolbar_height + game.offset_y) // cell_size_zoomed) + 1
        start_col = int(game.offset_x // cell_size_zoomed) - 1
        end_col   = int((win_w + game.offset_x) // cell_size_zoomed) + 1

        # Cellules vivantes
        for (row, col) in game.grid:
            if start_row <= row <= end_row and start_col <= col <= end_col:
                cx = col * cell_size_zoomed - game.offset_x
                cy = row * cell_size_zoomed - game.offset_y + toolbar_height
                pygame.draw.rect(screen, WHITE, (cx, cy, cell_size_zoomed - 1, cell_size_zoomed - 1))

        # Lignes de grille
        if cell_size_zoomed >= 4:
            for col in range(start_col, end_col + 1):
                lx = col * cell_size_zoomed - game.offset_x
                pygame.draw.line(screen, GRID_COLOR, (lx, toolbar_height), (lx, win_h))
            for row in range(start_row, end_row + 1):
                ly = row * cell_size_zoomed - game.offset_y + toolbar_height
                pygame.draw.line(screen, GRID_COLOR, (0, ly), (win_w, ly))

        # Rectangle de sélection
        if selecting and sel_start and sel_end:
            c0 = min(sel_start[0], sel_end[0])
            c1 = max(sel_start[0], sel_end[0])
            r0 = min(sel_start[1], sel_end[1])
            r1 = max(sel_start[1], sel_end[1])
            rx = c0 * cell_size_zoomed - game.offset_x
            ry = r0 * cell_size_zoomed - game.offset_y + toolbar_height
            rw = (c1 - c0 + 1) * cell_size_zoomed
            rh = (r1 - r0 + 1) * cell_size_zoomed
            if edit_tool == 'remove':
                sel_color, border_color = (255, 80, 80, 60), (255, 80, 80)
            elif edit_tool == 'copy':
                sel_color, border_color = (80, 255, 120, 60), (80, 255, 120)
            else:
                sel_color, border_color = (100, 180, 255, 60), (100, 180, 255)
            sel_surface = pygame.Surface((rw, rh), pygame.SRCALPHA)
            sel_surface.fill(sel_color)
            screen.blit(sel_surface, (rx, ry))
            pygame.draw.rect(screen, border_color, (rx, ry, rw, rh), 1)

        # Fantôme
        if ghost_cells is not None and edit_tool in ('load', 'paste'):
            for (dr, dc) in ghost_cells:
                gx = (mouse_col + dc) * cell_size_zoomed - game.offset_x
                gy = (mouse_row + dr) * cell_size_zoomed - game.offset_y + toolbar_height
                ghost_surf = pygame.Surface((cell_size_zoomed - 1, cell_size_zoomed - 1), pygame.SRCALPHA)
                ghost_surf.fill((255, 255, 255, 100))
                screen.blit(ghost_surf, (gx, gy))

        # ---- Toolbar ----
        pygame.draw.rect(screen, BLACK, toolbar_rect)

        if not edit_mode:
            toggle_icon_display = pause_icon if game_running and not paused else play_icon
            draw_button_with_icon(screen, toggle_icon_display, toggle_button_rect)
            draw_button_with_icon(screen, reset_icon, reset_button_rect)
            draw_button_with_icon(screen, edit_icon,  edit_button_rect)
            draw_slider(screen, slider_x, 6, slider_width, gen_per_sec, MIN_GEN_PER_SEC, MAX_GEN_PER_SEC, font)
            gen_text = font.render(f"Gen: {generation}", True, (255, 255, 255))
            screen.blit(gen_text, (slider_x + slider_width + 90, 10))
        else:
            draw_button_with_icon(screen, save_icon,   save_button_rect)
            draw_button_with_icon(screen, load_icon,   load_button_rect)
            draw_button_with_icon(screen, copy_icon,   copy_button_rect)
            draw_button_with_icon(screen, paste_icon,  paste_button_rect)
            draw_button_with_icon(screen, remove_surf, remove_button_rect)

            if ghost_cells is not None:
                hint = "< > rot  |  ^ v flip  |  Clic/Entree: poser  |  Echap: annuler"
            elif selecting:
                hint = "Glisser pour selectionner  |  Entree: valider  |  Echap: annuler"
            elif edit_tool == 'remove':
                hint = "Selectionner la zone a supprimer  |  Echap: annuler"
            elif edit_tool == 'copy':
                hint = "Selectionner la zone a copier  |  Echap: annuler"
            elif edit_tool == 'save':
                hint = "Selectionner la zone a sauvegarder  |  Echap: annuler"
            elif edit_tool == 'paste':
                hint = "Clic pour coller  |  < > rot  |  ^ v flip  |  Echap: annuler"
            else:
                hint = "Save  Load  Copy  Paste  Remove  |  Echap: quitter edit"
            hint_text = font.render(hint, True, (180, 220, 255))
            hint_x = 5 + 5 * (edit_btn_w + 2) + 8
            screen.blit(hint_text, (hint_x, 10))

        # Coordonnées centre écran
        center_col = int((game.offset_x + win_w / 2) / cell_size_zoomed)
        center_row = int((game.offset_y + (win_h - toolbar_height) / 2) / cell_size_zoomed)
        draw_coordinates(screen, center_col, center_row, font)

        pygame.display.flip()
        clock.tick(RENDER_FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
