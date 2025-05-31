import pygame
import random
import sys
import math
from constants import *

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

        
        self.templates = ALL_TEMPLATE_FILES[:]
        self.selected_index = 0

        self.thumb_surfaces = []
        for path in self.templates:
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.smoothscale(img, (IMAGE_THUMB_SIZE, IMAGE_THUMB_SIZE))
            self.thumb_surfaces.append(img)

        
        self.pieces, self.full_image = self.load_and_slice_image(self.templates[self.selected_index])
        self.board = generate_solvable_board()

        
        self.moving = False
        self.start_time = 0
        self.duration = ANIM_DURATION_MS
        self.src_pos = None
        self.dst_pos = None
        self.moving_tile = None

        
        self.in_reset = False
        self.reset_start_time = 0
        self.reset_old_board = None
        self.reset_new_board = None
        self.reset_animations = []

        
        self.in_fade = False
        self.fade_alpha = 255
        self.fade_old_surface = None
        self.fade_new_surface = None
        self.next_pieces = None
        self.next_full = None
        self.next_board = None

        
        self.show_numbers = False
        self.number_alpha = 0  

        
        self.dark_overlay = pygame.Surface((PUZZLE_SIZE, PUZZLE_SIZE), flags=pygame.SRCALPHA)
        self.dark_overlay.fill((0, 0, 0, 200))

    def load_and_slice_image(self, path):
        full_img = pygame.image.load(path).convert_alpha()
        full_img = pygame.transform.smoothscale(full_img, (PUZZLE_SIZE, PUZZLE_SIZE))

        pieces = []
        for row in range(3):
            for col in range(3):
                rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                piece_surf = full_img.subsurface(rect).copy()
                pieces.append(piece_surf)
        return pieces, full_img

    def capture_puzzle_surface(self, pieces, board, full_image, show_numbers_flag):
        surf = pygame.Surface((PUZZLE_SIZE, PUZZLE_SIZE), flags=pygame.SRCALPHA)
        
        surf.blit(full_image, (0, 0))
        
        surf.blit(self.dark_overlay, (0, 0))
        
        font = pygame.font.SysFont("consolas", TILE_SIZE // 2, bold=False)  
        for r in range(3):
            for c in range(3):
                val = board[r][c]
                if val == 8:
                    continue
                x = c * TILE_SIZE
                y = r * TILE_SIZE
                surf.blit(pieces[val], (x, y))
                if show_numbers_flag:
                    num = str(val + 1)
                    text_surf = font.render(num, True, COLOR_TEXT)
                    
                    tx = x + TILE_SIZE//2 - text_surf.get_width()//2
                    ty = y + TILE_SIZE//2 - text_surf.get_height()//2
                    surf.blit(text_surf, (tx, ty))
        return surf

    def start_move(self, r, c):
        if self.in_reset or self.in_fade:
            return
        br, bc = find_blank(self.board)
        if r is None or c is None:
            return
        
        if self.moving:
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

    def update(self):
        
        if self.in_fade:
            self.fade_alpha = max(0, self.fade_alpha - FADE_SPEED)
            if self.fade_alpha <= 0:
                
                self.pieces = self.next_pieces
                self.full_image = self.next_full
                self.board = self.next_board
                self.fade_old_surface = None
                self.fade_new_surface = None
                self.in_fade = False

        
        elif self.in_reset:
            now = pygame.time.get_ticks()
            elapsed = now - self.reset_start_time
            if elapsed >= self.duration:
                self.board = self.reset_new_board
                self.in_reset = False

        
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

        
        if self.show_numbers and self.number_alpha < 255:
            self.number_alpha = min(255, self.number_alpha + FADE_SPEED)
        elif not self.show_numbers and self.number_alpha > 0:
            self.number_alpha = max(0, self.number_alpha - FADE_SPEED)

    def draw_background(self):
        self.screen.fill(COLOR_BG)
        if self.in_fade:
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
        if self.in_fade:
            return

        
        if self.in_reset:
            now = pygame.time.get_ticks()
            elapsed = now - self.reset_start_time
            raw_t = elapsed / self.duration
            t = max(0.0, min(raw_t, 1.0))
            progress = ease_out_quint(t)
            font = pygame.font.SysFont("consolas", TILE_SIZE // 2, bold=False)
            for anim in self.reset_animations:
                val = anim['val']
                sx, sy = anim['start']
                ex, ey = anim['end']
                cx = sx + (ex - sx) * progress
                cy = sy + (ey - sy) * progress
                self.screen.blit(self.pieces[val], (cx, cy))
                
                if self.number_alpha > 0:
                    num = str(val + 1)
                    text_surf = font.render(num, True, COLOR_TEXT)
                    text_surf.set_alpha(self.number_alpha)
                    tx = cx + TILE_SIZE // 2 - text_surf.get_width() // 2
                    ty = cy + TILE_SIZE // 2 - text_surf.get_height() // 2
                    self.screen.blit(text_surf, (tx, ty))
            return

        
        font = pygame.font.SysFont("consolas", TILE_SIZE // 2, bold=False)
        for r in range(3):
            for c in range(3):
                val = self.board[r][c]
                if val == 8:
                    continue
                if self.moving and (r, c) == self.src_pos:
                    continue
                tile_x, tile_y = grid_to_pixel(r, c)
                self.screen.blit(self.pieces[val], (tile_x, tile_y))
                
                if self.number_alpha > 0:
                    num = str(val + 1)
                    text_surf = font.render(num, True, COLOR_TEXT)
                    text_surf.set_alpha(self.number_alpha)
                    tx = tile_x + TILE_SIZE // 2 - text_surf.get_width() // 2
                    ty = tile_y + TILE_SIZE // 2 - text_surf.get_height() // 2
                    self.screen.blit(text_surf, (tx, ty))

        
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
            
            if self.number_alpha > 0:
                num = str(self.moving_tile + 1)
                text_surf = font.render(num, True, COLOR_TEXT)
                text_surf.set_alpha(self.number_alpha)
                tx = cur_x + TILE_SIZE // 2 - text_surf.get_width() // 2
                ty = cur_y + TILE_SIZE // 2 - text_surf.get_height() // 2
                self.screen.blit(text_surf, (tx, ty))

    def shuffle(self):
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
                                "val": val,
                                "start": (sx, sy),
                                "end": (ex, ey)
                            })
                            break
        self.in_reset = True
        self.reset_start_time = pygame.time.get_ticks()

    def prepare_fade(self, new_index):
        if new_index == self.selected_index:
            return
        if self.moving or self.in_reset or self.in_fade:
            return
        
        self.fade_old_surface = self.capture_puzzle_surface(
            self.pieces, self.board, self.full_image, self.show_numbers
        )
        
        new_pieces, new_full = self.load_and_slice_image(self.templates[new_index])
        new_board = generate_solvable_board()
        
        old_show_flag = self.show_numbers
        self.show_numbers = False
        self.fade_new_surface = self.capture_puzzle_surface(
            new_pieces, new_board, new_full, False
        )
        self.show_numbers = old_show_flag
        
        self.in_fade = True
        self.fade_alpha = 255
        self.next_pieces = new_pieces
        self.next_full = new_full
        self.next_board = new_board
        self.selected_index = new_index

    def toggle_numbers(self):
        """
        Bật/tắt show_numbers (sẽ fade qua số hiển thị)
        """
        if self.in_fade:
            return
        self.show_numbers = not self.show_numbers

