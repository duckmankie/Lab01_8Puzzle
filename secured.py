import pygame
import random
import sys
import math
import os

# ----------------------------
# Constants
# ----------------------------

WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
BOARD_REGION_WIDTH = 720
BOARD_REGION_HEIGHT = 720
RIGHT_PANEL_X = BOARD_REGION_WIDTH
RIGHT_PANEL_WIDTH = WINDOW_WIDTH - BOARD_REGION_WIDTH
RIGHT_PANEL_HEIGHT = WINDOW_HEIGHT

PUZZLE_PADDING = 20
PUZZLE_SIZE = BOARD_REGION_WIDTH - 2 * PUZZLE_PADDING  # 680
TILE_SIZE = PUZZLE_SIZE // 3                            # ~226

PUZZLE_OFFSET_X = PUZZLE_PADDING
PUZZLE_OFFSET_Y = PUZZLE_PADDING

FPS = 90
ANIM_DURATION_MS = 300    # Time for tile tween (ms)
FADE_SPEED = 15           # Alpha change per frame during fade or number fade

COLOR_BG = (30, 30, 30)
COLOR_PANEL = (40, 40, 40)
COLOR_HIGHLIGHT = (70, 70, 70)
COLOR_TEXT = (220, 220, 220)
COLOR_BUTTON = (60, 60, 60)
COLOR_BUTTON_HOVER = (100, 100, 100)

TEMPLATE_DIR = "assets/templates"
TEMPLATE_PATHS = [
    os.path.join(TEMPLATE_DIR, fname)
    for fname in os.listdir(TEMPLATE_DIR)
    if fname.lower().endswith((".png", ".jpg", ".jpeg"))
]

ALGORITHMS = ["BFS", "DFS", "A*", "Dijkstra"]

IMAGE_THUMB_SIZE = 100
THUMBS_VISIBLE = 4

# Checkbox for showing numbers
CHECKBOX_SIZE = 20
CHECKBOX_X = RIGHT_PANEL_X + 20
CHECKBOX_Y = WINDOW_HEIGHT - 60
LABEL_X = CHECKBOX_X + CHECKBOX_SIZE + 10
LABEL_Y = CHECKBOX_Y - 2

def load_and_slice_image(path):
    full_img = pygame.image.load(path).convert_alpha()
    full_img = pygame.transform.smoothscale(full_img, (PUZZLE_SIZE, PUZZLE_SIZE))
    pieces = []
    for row in range(3):
        for col in range(3):
            rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            piece_surf = full_img.subsurface(rect).copy()
            pieces.append(piece_surf)
    return pieces, full_img

def is_solvable(flat_list):
    inv_count = 0
    for i in range(8):
        for j in range(i + 1, 9):
            if flat_list[i] != 8 and flat_list[j] != 8 and flat_list[i] > flat_list[j]:
                inv_count += 1
    return (inv_count % 2) == 0

def generate_solvable_board():
    arr = list(range(9))
    while True:
        random.shuffle(arr)
        if is_solvable(arr):
            return [arr[0:3], arr[3:6], arr[6:9]]

def find_blank(board):
    for r in range(3):
        for c in range(3):
            if board[r][c] == 8:
                return r, c
    return None, None

def grid_to_pixel(r, c):
    x = PUZZLE_OFFSET_X + c * TILE_SIZE
    y = PUZZLE_OFFSET_Y + r * TILE_SIZE
    return x, y

def pixel_to_grid(x, y):
    if (PUZZLE_OFFSET_X <= x < PUZZLE_OFFSET_X + PUZZLE_SIZE and
        PUZZLE_OFFSET_Y <= y < PUZZLE_OFFSET_Y + PUZZLE_SIZE):
        local_x = x - PUZZLE_OFFSET_X
        local_y = y - PUZZLE_OFFSET_Y
        return local_y // TILE_SIZE, local_x // TILE_SIZE
    return None, None

def ease_out_quint(t):
    return 1 - (1 - t) ** 5

class EightPuzzle:
    def __init__(self, screen):
        self.screen = screen

        # Load template thumbnails
        self.templates = TEMPLATE_PATHS[:]
        self.thumb_surfaces = []
        for path in self.templates:
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.smoothscale(img, (IMAGE_THUMB_SIZE, IMAGE_THUMB_SIZE))
            self.thumb_surfaces.append(img)
        self.thumb_offset = 0
        self.selected_template_index = 0

        # Load initial puzzle
        self.pieces, self.full_image = load_and_slice_image(
            self.templates[self.selected_template_index]
        )
        self.board = generate_solvable_board()

        # Move animation state
        self.moving = False
        self.start_time = 0
        self.duration = ANIM_DURATION_MS
        self.src_pos = None
        self.dst_pos = None
        self.moving_tile = None

        # Reset (shuffle) animation state
        self.in_reset = False
        self.reset_start_time = 0
        self.reset_old_board = None
        self.reset_new_board = None
        self.reset_animations = []

        # Fade transition state (switching template)
        self.in_fade = False
        self.fade_alpha = 255
        self.fade_old_surface = None
        self.fade_new_surface = None
        self.next_pieces = None
        self.next_full = None
        self.next_board = None

        # Fade for showing numbers
        self.show_numbers = False
        self.number_alpha = 0  # 0 = invisible, 255 = fully visible

        # Dark overlay for puzzle
        self.dark_overlay = pygame.Surface((PUZZLE_SIZE, PUZZLE_SIZE), flags=pygame.SRCALPHA)
        self.dark_overlay.fill((0, 0, 0, 200))

        # UI elements
        self.selected_algorithm = ALGORITHMS[0]
        self.dropdown_open = False
        self.dropdown_rect = pygame.Rect(RIGHT_PANEL_X + 20, 140, RIGHT_PANEL_WIDTH - 40, 40)

        self.solve_button = pygame.Rect(RIGHT_PANEL_X + 20, 200, RIGHT_PANEL_WIDTH - 40, 50)
        self.next_button = pygame.Rect(RIGHT_PANEL_X + 20, 270, RIGHT_PANEL_WIDTH - 40, 50)
        self.reset_button = pygame.Rect(RIGHT_PANEL_X + 20, 340, RIGHT_PANEL_WIDTH - 40, 50)

    def capture_puzzle_surface(self, pieces, board, full_image):
        """
        Render puzzle (full image, overlay, and tiles and numbers if on) onto a surface.
        """
        surf = pygame.Surface((PUZZLE_SIZE, PUZZLE_SIZE), flags=pygame.SRCALPHA)
        # Draw full image
        surf.blit(full_image, (0, 0))
        # Draw dark overlay
        surf.blit(self.dark_overlay, (0, 0))
        # Draw tiles
        for r in range(3):
            for c in range(3):
                val = board[r][c]
                if val == 8:
                    continue
                tile_surf = pieces[val]
                x = c * TILE_SIZE
                y = r * TILE_SIZE
                surf.blit(tile_surf, (x, y))
        # Draw numbers if show_numbers==True (use full alpha here)
        if self.show_numbers:
            font = pygame.font.SysFont("arial", TILE_SIZE // 2, bold=False)
            for r in range(3):
                for c in range(3):
                    val = board[r][c]
                    if val == 8:
                        continue
                    num = str(val + 1)
                    text_surf = font.render(num, True, COLOR_TEXT)
                    tx = c * TILE_SIZE + TILE_SIZE // 2 - text_surf.get_width() // 2
                    ty = r * TILE_SIZE + TILE_SIZE // 2 - text_surf.get_height() // 2
                    surf.blit(text_surf, (tx, ty))
        return surf

    def draw_background(self):
        self.screen.fill(COLOR_BG)
        if self.in_fade:
            # Draw old puzzle faded out and new puzzle fading in
            old = self.fade_old_surface.copy()
            old.set_alpha(self.fade_alpha)
            new = self.fade_new_surface.copy()
            new.set_alpha(255 - self.fade_alpha)
            self.screen.blit(old, (PUZZLE_OFFSET_X, PUZZLE_OFFSET_Y))
            self.screen.blit(new, (PUZZLE_OFFSET_X, PUZZLE_OFFSET_Y))
        else:
            self.screen.blit(self.full_image, (PUZZLE_OFFSET_X, PUZZLE_OFFSET_Y))
            self.screen.blit(self.dark_overlay, (PUZZLE_OFFSET_X, PUZZLE_OFFSET_Y))

    def draw_puzzle(self):
        # Skip tile-by-tile draw during fade
        if self.in_fade:
            return

        # Draw moving/reset animations or static tiles
        if self.in_reset:
            now = pygame.time.get_ticks()
            elapsed = now - self.reset_start_time
            raw_t = elapsed / self.duration
            t = max(0.0, min(raw_t, 1.0))
            progress = ease_out_quint(t)
            for anim in self.reset_animations:
                val = anim['val']
                sx, sy = anim['start']
                ex, ey = anim['end']
                cx = sx + (ex - sx) * progress
                cy = sy + (ey - sy) * progress
                self.screen.blit(self.pieces[val], (cx, cy))
                # Draw number on moving tile (with same alpha as number_alpha)
                if self.number_alpha > 0:
                    font = pygame.font.SysFont("arial", TILE_SIZE // 2, bold=False)
                    num = str(val + 1)
                    text_surf = font.render(num, True, COLOR_TEXT)
                    text_surf.set_alpha(self.number_alpha)
                    tx = cx + TILE_SIZE // 2 - text_surf.get_width() // 2
                    ty = cy + TILE_SIZE // 2 - text_surf.get_height() // 2
                    self.screen.blit(text_surf, (tx, ty))
            if elapsed >= self.duration:
                self.board = self.reset_new_board
                self.in_reset = False
        else:
            # Draw static tiles (skipping the one being tweened)
            for r in range(3):
                for c in range(3):
                    val = self.board[r][c]
                    if val == 8:
                        continue
                    if self.moving and (r, c) == self.src_pos:
                        continue
                    tile_x, tile_y = grid_to_pixel(r, c)
                    self.screen.blit(self.pieces[val], (tile_x, tile_y))
                    # Draw number if toggled on
                    if self.number_alpha > 0:
                        font = pygame.font.SysFont("arial", TILE_SIZE // 2, bold=False)
                        num = str(val + 1)
                        text_surf = font.render(num, True, COLOR_TEXT)
                        text_surf.set_alpha(self.number_alpha)
                        tx = tile_x + TILE_SIZE // 2 - text_surf.get_width() // 2
                        ty = tile_y + TILE_SIZE // 2 - text_surf.get_height() // 2
                        self.screen.blit(text_surf, (tx, ty))
            # Draw tweened tile if moving
            if self.moving:
                now = pygame.time.get_ticks()
                elapsed = now - self.start_time
                raw_t = elapsed / self.duration
                t = max(0.0, min(raw_t, 1.0))
                progress = ease_out_quint(t)
                sr, sc = self.src_pos
                dr, dc = self.dst_pos
                start_x, start_y = grid_to_pixel(sr, sc)
                end_x, end_y = grid_to_pixel(dr, dc)
                cur_x = start_x + (end_x - start_x) * progress
                cur_y = start_y + (end_y - start_y) * progress
                self.screen.blit(self.pieces[self.moving_tile], (cur_x, cur_y))
                # Draw number on tweened tile
                if self.number_alpha > 0:
                    font = pygame.font.SysFont("arial", TILE_SIZE // 2, bold=False)
                    num = str(self.moving_tile + 1)
                    text_surf = font.render(num, True, COLOR_TEXT)
                    text_surf.set_alpha(self.number_alpha)
                    tx = cur_x + TILE_SIZE // 2 - text_surf.get_width() // 2
                    ty = cur_y + TILE_SIZE // 2 - text_surf.get_height() // 2
                    self.screen.blit(text_surf, (tx, ty))
                if elapsed >= self.duration:
                    self.board[dr][dc], self.board[sr][sc] = (
                        self.board[sr][sc], self.board[dr][dc]
                    )
                    self.moving = False
                    self.src_pos = None
                    self.dst_pos = None
                    self.moving_tile = None

    def draw_ui(self):
        panel_rect = pygame.Rect(RIGHT_PANEL_X, 0, RIGHT_PANEL_WIDTH, RIGHT_PANEL_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_PANEL, panel_rect)

        thumb_y = 20
        thumb_x = RIGHT_PANEL_X + 20
        for i in range(THUMBS_VISIBLE):
            idx = self.thumb_offset + i
            if idx >= len(self.thumb_surfaces):
                break
            rect = pygame.Rect(
                thumb_x + i * (IMAGE_THUMB_SIZE + 10),
                thumb_y,
                IMAGE_THUMB_SIZE,
                IMAGE_THUMB_SIZE
            )
            self.screen.blit(self.thumb_surfaces[idx], rect.topleft)
            if idx == self.selected_template_index:
                pygame.draw.rect(self.screen, COLOR_HIGHLIGHT, rect, 3)

        arrow_rect = pygame.Rect(
            RIGHT_PANEL_X + RIGHT_PANEL_WIDTH - 40,
            thumb_y,
            30,
            IMAGE_THUMB_SIZE
        )
        pygame.draw.rect(self.screen, COLOR_BUTTON, arrow_rect)
        pygame.draw.polygon(self.screen, COLOR_TEXT, [
            (arrow_rect.centerx - 5, arrow_rect.centery - 10),
            (arrow_rect.centerx - 5, arrow_rect.centery + 10),
            (arrow_rect.centerx + 5, arrow_rect.centery)
        ])

        pygame.draw.rect(self.screen, COLOR_BUTTON, self.dropdown_rect)
        font = pygame.font.SysFont(None, 30)
        txt = font.render(self.selected_algorithm, True, COLOR_TEXT)
        self.screen.blit(txt, (self.dropdown_rect.x + 10, self.dropdown_rect.y + 8))
        pygame.draw.polygon(self.screen, COLOR_TEXT, [
            (self.dropdown_rect.right - 20, self.dropdown_rect.y + 15),
            (self.dropdown_rect.right - 10, self.dropdown_rect.y + 15),
            (self.dropdown_rect.right - 15, self.dropdown_rect.y + 25)
        ])
        if self.dropdown_open:
            for i, algo in enumerate(ALGORITHMS):
                item_rect = pygame.Rect(
                    self.dropdown_rect.x,
                    self.dropdown_rect.y + 40 + i * 40,
                    self.dropdown_rect.width,
                    40
                )
                pygame.draw.rect(self.screen, COLOR_BUTTON, item_rect)
                txt2 = font.render(algo, True, COLOR_TEXT)
                self.screen.blit(txt2, (item_rect.x + 10, item_rect.y + 8))

        # Buttons
        self._draw_button(self.solve_button, "Solve/Stop")
        self._draw_button(self.next_button, "Next Step")
        self._draw_button(self.reset_button, "Reset")

        # Checkbox for Show Numbers
        mouse_x, mouse_y = pygame.mouse.get_pos()
        check_rect = pygame.Rect(CHECKBOX_X, CHECKBOX_Y, CHECKBOX_SIZE, CHECKBOX_SIZE)
        hovered = check_rect.collidepoint(mouse_x, mouse_y)
        color = COLOR_BUTTON_HOVER if hovered else COLOR_BUTTON
        pygame.draw.rect(self.screen, color, check_rect)
        if self.show_numbers:
            # Draw check mark
            pygame.draw.line(self.screen, COLOR_TEXT,
                             (CHECKBOX_X + 4, CHECKBOX_Y + CHECKBOX_SIZE // 2),
                             (CHECKBOX_X + CHECKBOX_SIZE // 2, CHECKBOX_Y + CHECKBOX_SIZE - 4), 3)
            pygame.draw.line(self.screen, COLOR_TEXT,
                             (CHECKBOX_X + CHECKBOX_SIZE // 2, CHECKBOX_Y + CHECKBOX_SIZE - 4),
                             (CHECKBOX_X + CHECKBOX_SIZE - 4, CHECKBOX_Y + 4), 3)
        label_surf = pygame.font.SysFont(None, 24).render("Show Numbers", True, COLOR_TEXT)
        self.screen.blit(label_surf, (LABEL_X, LABEL_Y))

    def _draw_button(self, rect, label):
        mx, my = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mx, my)
        color = COLOR_BUTTON_HOVER if hovered else COLOR_BUTTON
        pygame.draw.rect(self.screen, color, rect)
        font = pygame.font.SysFont(None, 30)
        txt = font.render(label, True, COLOR_TEXT)
        txt_pos = (
            rect.x + (rect.width - txt.get_width()) // 2,
            rect.y + (rect.height - txt.get_height()) // 2
        )
        self.screen.blit(txt, txt_pos)

    def start_move(self, r, c):
        if self.in_reset or self.in_fade:
            return
        br, bc = find_blank(self.board)
        if r is None or c is None:
            return
        if self.moving:
            # Finalize current tween immediately
            sr, sc = self.src_pos
            dr, dc = self.dst_pos
            self.board[dr][dc], self.board[sr][sc] = (self.board[sr][sc], self.board[dr][dc])
            self.moving = False
            self.src_pos = None
            self.dst_pos = None
            self.moving_tile = None
            br, bc = find_blank(self.board)
        if abs(br - r) + abs(bc - c) == 1:
            self.moving = True
            self.start_time = pygame.time.get_ticks()
            self.src_pos = (r, c)
            self.dst_pos = (br, bc)
            self.moving_tile = self.board[r][c]

    def prepare_reset_animation(self):
        self.reset_old_board = [row[:] for row in self.board]
        self.reset_new_board = generate_solvable_board()
        self.reset_animations = []
        for r in range(3):
            for c in range(3):
                val = self.reset_old_board[r][c]
                if val == 8:
                    continue
                for nr in range(3):
                    for nc in range(3):
                        if self.reset_new_board[nr][nc] == val:
                            sx, sy = grid_to_pixel(r, c)
                            ex, ey = grid_to_pixel(nr, nc)
                            self.reset_animations.append({
                                'val': val,
                                'start': (sx, sy),
                                'end': (ex, ey)
                            })
                            break
        self.in_reset = True
        self.reset_start_time = pygame.time.get_ticks()

    def prepare_fade(self, new_index):
        # Do not allow fade during solving/moving/reset
        if self.moving or self.in_reset or self.in_fade:
            return
        # Capture old puzzle into surface
        self.fade_old_surface = self.capture_puzzle_surface(
            self.pieces, self.board, self.full_image
        )
        # Load new template pieces & full image, but do not apply to active yet
        new_pieces, new_full = load_and_slice_image(self.templates[new_index])
        new_board = generate_solvable_board()
        # Capture new puzzle surface
        # Temporarily set show_numbers to False so capture doesn't draw numbers on new
        old_show = self.show_numbers
        self.show_numbers = False
        self.fade_new_surface = self.capture_puzzle_surface(new_pieces, new_board, new_full)
        self.show_numbers = old_show
        # Set fade state
        self.in_fade = True
        self.fade_alpha = 255
        # After fade finishes, swap active puzzle
        self.next_pieces = new_pieces
        self.next_full = new_full
        self.next_board = new_board
        self.selected_template_index = new_index

    def toggle_numbers(self):
        if self.in_fade:
            return
        self.show_numbers = not self.show_numbers

    def update(self):
        # Fade transition
        if self.in_fade:
            self.fade_alpha = max(0, self.fade_alpha - FADE_SPEED)
            if self.fade_alpha <= 0:
                # Finish fade: apply new puzzle
                self.pieces = self.next_pieces
                self.full_image = self.next_full
                self.board = self.next_board
                self.fade_old_surface = None
                self.fade_new_surface = None
                self.in_fade = False
        # Reset shuffle animation
        elif self.in_reset:
            now = pygame.time.get_ticks()
            elapsed = now - self.reset_start_time
            if elapsed >= self.duration:
                self.board = self.reset_new_board
                self.in_reset = False
        # Tile move animation
        elif self.moving:
            now = pygame.time.get_ticks()
            elapsed = now - self.start_time
            if elapsed >= self.duration:
                sr, sc = self.src_pos
                dr, dc = self.dst_pos
                self.board[dr][dc], self.board[sr][sc] = (
                    self.board[sr][sc], self.board[dr][dc]
                )
                self.moving = False
                self.src_pos = None
                self.dst_pos = None
                self.moving_tile = None
        # Number fade
        if self.show_numbers and self.number_alpha < 255:
            self.number_alpha = min(255, self.number_alpha + FADE_SPEED)
        elif not self.show_numbers and self.number_alpha > 0:
            self.number_alpha = max(0, self.number_alpha - FADE_SPEED)

    def handle_ui_event(self, mx, my):
        thumb_y = 20
        thumb_x = RIGHT_PANEL_X + 20
        # Thumbnails
        for i in range(THUMBS_VISIBLE):
            idx = self.thumb_offset + i
            if idx >= len(self.thumb_surfaces):
                break
            rect = pygame.Rect(
                thumb_x + i * (IMAGE_THUMB_SIZE + 10),
                thumb_y,
                IMAGE_THUMB_SIZE,
                IMAGE_THUMB_SIZE
            )
            if rect.collidepoint(mx, my):
                self.prepare_fade(idx)
                return

        # Arrow for more thumbnails
        arrow_rect = pygame.Rect(
            RIGHT_PANEL_X + RIGHT_PANEL_WIDTH - 40,
            thumb_y,
            30,
            IMAGE_THUMB_SIZE
        )
        if arrow_rect.collidepoint(mx, my):
            if self.thumb_offset + THUMBS_VISIBLE < len(self.thumb_surfaces):
                self.thumb_offset += 1
            return

        # Dropdown
        if self.dropdown_rect.collidepoint(mx, my):
            self.dropdown_open = not self.dropdown_open
            return
        if self.dropdown_open:
            for i, algo in enumerate(ALGORITHMS):
                item_rect = pygame.Rect(
                    self.dropdown_rect.x,
                    self.dropdown_rect.y + 40 + i * 40,
                    self.dropdown_rect.width,
                    40
                )
                if item_rect.collidepoint(mx, my):
                    self.selected_algorithm = algo
                    self.dropdown_open = False
                    return

        # Buttons
        if self.solve_button.collidepoint(mx, my):
            return
        if self.next_button.collidepoint(mx, my):
            return
        if self.reset_button.collidepoint(mx, my):
            self.prepare_reset_animation()
            return

        # Checkbox for Show Numbers
        check_rect = pygame.Rect(CHECKBOX_X, CHECKBOX_Y, CHECKBOX_SIZE, CHECKBOX_SIZE)
        if check_rect.collidepoint(mx, my) and not self.in_fade:
            self.toggle_numbers()
            return

def main():
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("8-Puzzle with Number Toggle & Fade")

    puzzle = EightPuzzle(screen)
    running = True

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                # Puzzle clicks interrupt move/fade/reset
                if (PUZZLE_OFFSET_X <= mx < PUZZLE_OFFSET_X + PUZZLE_SIZE and
                    PUZZLE_OFFSET_Y <= my < PUZZLE_OFFSET_Y + PUZZLE_SIZE and
                    not puzzle.in_reset and not puzzle.in_fade):
                    gr, gc = pixel_to_grid(mx, my)
                    if gr is not None:
                        puzzle.start_move(gr, gc)
                else:
                    puzzle.handle_ui_event(mx, my)

        puzzle.update()
        puzzle.draw_background()
        puzzle.draw_puzzle()
        puzzle.draw_ui()
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
