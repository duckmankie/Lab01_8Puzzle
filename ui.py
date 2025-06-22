

import pygame
from constants import *

from puzzle import pixel_to_grid

def draw_ui(screen, solve_btn, next_btn, reset_btn, dropdown, checkbox, puzzle, is_solving, solve_btn_color_progress, tween_color, solve_btn_disabled=False):
    # Draw solve_btn với tween color chỉ khi đang solve, còn lại để None để dùng COLOR_BUTTON mặc định
    solve_btn.draw(screen, disabled_hover=False, disabled=False, color_override=(tween_color if solve_btn.color_override is not None else None))
    if solve_btn_disabled:
        s = pygame.Surface((solve_btn.rect.width, solve_btn.rect.height), pygame.SRCALPHA)
        s.fill((0,0,0,80))
        screen.blit(s, solve_btn.rect.topleft)
    # Next/Reset buttons
    next_btn.draw(screen, disabled_hover=False)
    reset_btn.draw(screen, disabled_hover=False)
    # Vẽ chữ nhỏ "choose algorithm" phía trên, bên trái dropdown
    font_label = pygame.font.Font("assets/fonts/HelveticaNeueRoman.otf", 18)
    label_surface = font_label.render("Choose Algorithm", True, COLOR_TEXT)
    label_x = dropdown.header_rect.x
    label_y = dropdown.header_rect.y - label_surface.get_height() - 8
    screen.blit(label_surface, (label_x, label_y))
    dropdown.draw(screen)
    checkbox.draw(screen)
    # Draw thumbnails
    thumb_y = 20
    thumb_x = RIGHT_PANEL_X + 20
    for i in range(THUMBS_PER_ROW):
        idx = i
        if idx >= len(puzzle.templates):
            break
        rect = pygame.Rect(
            thumb_x + i * (IMAGE_THUMB_SIZE + THUMBS_SPACING),
            thumb_y,
            IMAGE_THUMB_SIZE,
            IMAGE_THUMB_SIZE
        )
        screen.blit(puzzle.thumb_surfaces[idx], rect.topleft)
        if idx == puzzle.selected_index:
            pygame.draw.rect(screen, COLOR_HIGHLIGHT, rect, 3)


def handle_ui_event(event, puzzle, solve_btn, next_btn, reset_btn, dropdown, checkbox, is_solving):
    action = None
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        mx, my = pygame.mouse.get_pos()
        # Dropdown click handling
        if not is_solving:
            dd_choice = dropdown.is_clicked(mx, my)
            if dd_choice is not None:
                puzzle.selected_algorithm = ALGORITHMS[dd_choice]
                action = 'algorithm_changed'
                return is_solving, action
        # Dropdown close if click outside
        if dropdown.is_open and not is_solving:
            dropdown_rect = dropdown.header_rect.copy()
            dropdown_rect.height += dropdown.header_rect.height * (len(dropdown.options))
            if not dropdown_rect.collidepoint(mx, my):
                dropdown.is_open = False
            else:
                return is_solving, action
        # Puzzle grid click
        if (not is_solving and PUZZLE_OFFSET_X <= mx < PUZZLE_OFFSET_X + PUZZLE_SIZE and
            PUZZLE_OFFSET_Y <= my < PUZZLE_OFFSET_Y + PUZZLE_SIZE and
            not puzzle.in_reset and not puzzle.in_fade):
            gr, gc = pixel_to_grid(mx, my)
            if gr is not None:
                puzzle.start_move(gr, gc)
                action = 'board_changed'
                return is_solving, action
        # Checkbox click
        if checkbox.is_clicked(mx, my):
            puzzle.toggle_numbers()
            return is_solving, action
        # Buttons click
        if solve_btn.is_clicked(mx, my):
            if not is_solving:
                is_solving = True
                solve_btn.label = "Stop"
                solve_btn.color_override = (237,85,85)
                action = 'solve'
            else:
                is_solving = False
                solve_btn.label = "Solve"
                solve_btn.color_override = None
                action = 'stop_solve'
            return is_solving, action
        if next_btn.is_clicked(mx, my) and not is_solving:
            action = 'next_step'
            return is_solving, action
        if reset_btn.is_clicked(mx, my) and not is_solving:
            puzzle.shuffle()
            action = 'reset'
            return is_solving, action
        # Thumbnail click
        if not is_solving:
            thumb_y = 20
            thumb_x = RIGHT_PANEL_X + 20
            for i in range(THUMBS_PER_ROW):
                idx = i
                if idx >= len(puzzle.templates):
                    break
                rect = pygame.Rect(
                    thumb_x + i * (IMAGE_THUMB_SIZE + THUMBS_SPACING),
                    thumb_y,
                    IMAGE_THUMB_SIZE,
                    IMAGE_THUMB_SIZE
                )
                if rect.collidepoint(mx, my):
                    puzzle.prepare_fade(idx)
                    action = 'board_changed'
                    return is_solving, action
    return is_solving, action

class GameUI:
    def __init__(self, screen, puzzle):
        self.screen = screen
        self.puzzle = puzzle
        self.solve_btn = Button(RIGHT_PANEL_X + 20, 210, RIGHT_PANEL_WIDTH - 310, 50, "Solve")
        self.next_btn = Button(RIGHT_PANEL_X + 280, 210, RIGHT_PANEL_WIDTH - 310, 50, "Next Step")
        self.reset_btn = Button(RIGHT_PANEL_X + 20, 270, RIGHT_PANEL_WIDTH - 50, 50, "Reset")
        self.dropdown = Dropdown(RIGHT_PANEL_X + 20, 150, RIGHT_PANEL_WIDTH - 50, 50, ALGORITHMS)
        self.checkbox = Checkbox(CHECKBOX_X, CHECKBOX_Y, CHECKBOX_SIZE, "Show Numbers")
        self.is_solving = False
        self.solve_btn_color_progress = 0.0
        self.SOLVE_BTN_TWEEN_SPEED = 0.08

    def draw(self):
        # Xử lý trạng thái nút Solve khi completed
        if self.puzzle.completed:
            self.solve_btn.label = "Solved"
            self.solve_btn.color_override = COLOR_BG
            solve_disabled = True
            self.is_solving = False
        else:
            if not self.is_solving:
                self.solve_btn.label = "Solve"
                self.solve_btn.color_override = None
            solve_disabled = False
        # Tween màu solve_btn
        solve_btn_base = COLOR_BG
        solve_btn_red = (234, 69, 69)
        if self.is_solving:
            self.solve_btn_color_progress = min(1.0, self.solve_btn_color_progress + self.SOLVE_BTN_TWEEN_SPEED)
        else:
            self.solve_btn_color_progress = max(0.0, self.solve_btn_color_progress - self.SOLVE_BTN_TWEEN_SPEED)
        tween_color = tuple(
            int(solve_btn_base[i] + (solve_btn_red[i] - solve_btn_base[i]) * self.solve_btn_color_progress)
            for i in range(3)
        )
        # Vẽ UI, truyền trạng thái disable cho solve_btn
        draw_ui(self.screen, self.solve_btn, self.next_btn, self.reset_btn, self.dropdown, self.checkbox, self.puzzle, self.is_solving, self.solve_btn_color_progress, tween_color, solve_btn_disabled=solve_disabled)

    def handle_click(self, mx, my):
        # Dropdown click
        if not self.is_solving:
            dd_choice = self.dropdown.is_clicked(mx, my)
            if dd_choice is not None:
                self.puzzle.selected_algorithm = ALGORITHMS[dd_choice]
                return
        # Dropdown close if click outside
        if self.dropdown.is_open and not self.is_solving:
            dropdown_rect = self.dropdown.header_rect.copy()
            dropdown_rect.height += self.dropdown.header_rect.height * (len(self.dropdown.options))
            if not dropdown_rect.collidepoint(mx, my):
                self.dropdown.is_open = False
            else:
                return
        # Puzzle grid click
        if (not self.is_solving and PUZZLE_OFFSET_X <= mx < PUZZLE_OFFSET_X + PUZZLE_SIZE and
            PUZZLE_OFFSET_Y <= my < PUZZLE_OFFSET_Y + PUZZLE_SIZE and
            not self.puzzle.in_reset and not self.puzzle.in_fade):
            gr, gc = pixel_to_grid(mx, my)
            if gr is not None:
                self.puzzle.start_move(gr, gc)
                return
        # Checkbox click
        if self.checkbox.is_clicked(mx, my):
            self.puzzle.toggle_numbers()
            return
        # Buttons click
        if self.solve_btn.is_clicked(mx, my):
            if self.puzzle.completed:
                return  # Đã solved thì không cho bấm nữa
            if not self.is_solving:
                self.is_solving = True
                self.solve_btn.label = "Stop"
                self.solve_btn.color_override = (237,85,85)
                self.puzzle.solve()
            else:
                self.is_solving = False
                self.solve_btn.label = "Solve"
                self.solve_btn.color_override = None
                if hasattr(self.puzzle, 'stop_solve'):
                    self.puzzle.stop_solve()
            return
        if self.next_btn.is_clicked(mx, my):
            self.puzzle.next_step()
            return
        if self.reset_btn.is_clicked(mx, my) and not self.is_solving:
            self.puzzle.shuffle()
            # Enable lại solve_btn
            self.solve_btn.label = "Solve"
            self.solve_btn.color_override = None
            self.is_solving = False
            return
        # Thumbnail click
        if not self.is_solving:
            thumb_y = 20
            thumb_x = RIGHT_PANEL_X + 20
            for i in range(THUMBS_PER_ROW):
                idx = i
                if idx >= len(self.puzzle.templates):
                    break
                rect = pygame.Rect(
                    thumb_x + i * (IMAGE_THUMB_SIZE + THUMBS_SPACING),
                    thumb_y,
                    IMAGE_THUMB_SIZE,
                    IMAGE_THUMB_SIZE
                )
                if rect.collidepoint(mx, my):
                    self.puzzle.prepare_fade(idx)
                    # Enable lại solve_btn khi đổi puzzle
                    self.solve_btn.label = "Solve"
                    self.solve_btn.color_override = None
                    self.is_solving = False
                    return

class Button:
    def __init__(self, x, y, w, h, label, color_override=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.font = pygame.font.Font("assets/fonts/HelveticaNeueRoman.otf", 22)
        self.hover_amount = 0  # For tween effect
        self.color_override = color_override

    def draw(self, screen, disabled_hover=False, disabled=False, color_override=None):
        mx, my = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mx, my) and not disabled_hover and not disabled
        from constants import lighten_color
        # Chọn màu nền
        base_color = self.color_override if self.color_override is not None else COLOR_BUTTON
        if color_override is not None:
            base_color = color_override
        from constants import darken_color
        # Nếu disabled thì làm tối màu (dùng darken_color)
        if disabled:
            base_color = darken_color(base_color, 40)
        # Tween hover effect
        if hovered:
            self.hover_amount = min(self.hover_amount + FADE_HOVER_SPEED, 40)
        else:
            self.hover_amount = max(self.hover_amount - FADE_HOVER_SPEED, 0)
        color = lighten_color(base_color, int(self.hover_amount) if not disabled else 0)
        pygame.draw.rect(screen, color, self.rect, border_radius=BUTTON_RADIUS)
        pygame.draw.rect(screen, BUTTON_OUTLINE_COLOR, self.rect, BUTTON_OUTLINE_THICKNESS, border_radius=BUTTON_RADIUS)
        txt = self.font.render(self.label, True, COLOR_TEXT)
        # Padding cho text
        PADDING_X = 12
        PADDING_Y = 6
        txt_rect = txt.get_rect()
        txt_rect.centerx = self.rect.centerx
        txt_rect.centery = self.rect.centery
        # Đảm bảo text không sát viền button
        if txt_rect.width > self.rect.width - 2 * PADDING_X:
            txt_rect.width = self.rect.width - 2 * PADDING_X
        if txt_rect.height > self.rect.height - 2 * PADDING_Y:
            txt_rect.height = self.rect.height - 2 * PADDING_Y
        screen.blit(txt, txt_rect)

    def is_clicked(self, mx, my):
        return self.rect.collidepoint(mx, my)


class Checkbox:
    def __init__(self, x, y, size, label):
        self.rect = pygame.Rect(x, y, size, size)
        self.label = label
        self.font = pygame.font.Font("assets/fonts/HelveticaNeueRoman.otf", 24)
        self.is_checked = False

    def draw(self, screen):
        mx, my = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mx, my)
        from constants import lighten_color
        color = lighten_color(COLOR_BUTTON, 40) if hovered else COLOR_BUTTON
        pygame.draw.rect(screen, color, self.rect)  # Không bo góc
        if self.is_checked:
            
            pygame.draw.line(screen, COLOR_TEXT,
                             (self.rect.x + 4, self.rect.y + self.rect.height // 2),
                             (self.rect.x + self.rect.width // 2, self.rect.y + self.rect.height - 4), 3)
            pygame.draw.line(screen, COLOR_TEXT,
                             (self.rect.x + self.rect.width // 2, self.rect.y + self.rect.height - 4),
                             (self.rect.x + self.rect.width - 4, self.rect.y + 4), 3)
        # Căn label ngang hàng với tick box
        lbl = self.font.render(self.label, True, COLOR_TEXT)
        label_y = self.rect.y + (self.rect.height - lbl.get_height()) // 2
        screen.blit(lbl, (self.rect.x + self.rect.width + 8, label_y))

    def is_clicked(self, mx, my):
        if self.rect.collidepoint(mx, my):
            self.is_checked = not self.is_checked
            return True
        return False


class Dropdown:
    def __init__(self, x, y, w, h, options):
        self.header_rect = pygame.Rect(x, y, w, h)
        self.options = options
        self.current = 0
        self.is_open = False
        self.font = pygame.font.Font("assets/fonts/HelveticaNeueRoman.otf", 20)
        self.hover_amount = 0  # For tween effect

    def draw(self, screen):
        mx, my = pygame.mouse.get_pos()
        from constants import lighten_color

        # --- Draw dropdown header (button) ---
        hovered = self.header_rect.collidepoint(mx, my)
        if hovered:
            self.hover_amount = min(self.hover_amount + FADE_HOVER_SPEED, 40)
        else:
            self.hover_amount = max(self.hover_amount - FADE_HOVER_SPEED, 0)
        color = lighten_color(COLOR_DROPDOWN_BUTTON, int(self.hover_amount))
        pygame.draw.rect(screen, color, self.header_rect, border_radius=DROPDOWN_RADIUS)

        # Draw text in header
        PADDING_X = 12
        PADDING_Y = 6
        ARROW_PADDING = 35
        txt = self.font.render(self.options[self.current], True, COLOR_TEXT)
        txt_rect = txt.get_rect()
        txt_rect.left = self.header_rect.left + PADDING_X
        txt_rect.centery = self.header_rect.centery
        if txt_rect.width > self.header_rect.width - 2 * PADDING_X:
            txt_rect.width = self.header_rect.width - 2 * PADDING_X
        if txt_rect.height > self.header_rect.height - 2 * PADDING_Y:
            txt_rect.height = self.header_rect.height - 2 * PADDING_Y
        screen.blit(txt, txt_rect)

        # Draw arrow
        arrow_x = self.header_rect.right - ARROW_PADDING
        arrow_y = self.header_rect.centery
        v_width = 14
        v_height = 8
        pygame.draw.lines(screen, COLOR_TEXT, False, [
            (arrow_x, arrow_y - v_height // 2),
            (arrow_x + v_width // 2, arrow_y + v_height // 2),
            (arrow_x + v_width, arrow_y - v_height // 2)
        ], 3)

        # Draw outline for header
        #pygame.draw.rect(screen, BUTTON_OUTLINE_COLOR, self.header_rect, BUTTON_OUTLINE_THICKNESS, border_radius=DROPDOWN_RADIUS)

        # --- Draw dropdown menu if open ---
        if self.is_open:
            menu_rect = pygame.Rect(
                self.header_rect.x,
                self.header_rect.y + self.header_rect.height,
                self.header_rect.width,
                self.header_rect.height * len(self.options)
            )
            w, h = menu_rect.size

            # Surface để vẽ các item (không bo góc)
            content_surf = pygame.Surface((w, h), pygame.SRCALPHA)

            # Mask bo góc
            mask_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(mask_surf, (255,255,255,255),
                             mask_surf.get_rect(),
                             border_radius=DROPDOWN_RADIUS)

            # Tween hover cho từng option
            if not hasattr(self, 'option_hover_amount'):
                self.option_hover_amount = [0] * len(self.options)

            for i, opt in enumerate(self.options):
                item_rect = pygame.Rect(
                    0,
                    i * self.header_rect.height,
                    w,
                    self.header_rect.height
                )
                hovered_item = item_rect.move(menu_rect.topleft).collidepoint(mx, my)
                if hovered_item:
                    self.option_hover_amount[i] = min(self.option_hover_amount[i] + FADE_HOVER_SPEED, 40)
                else:
                    self.option_hover_amount[i] = max(self.option_hover_amount[i] - FADE_HOVER_SPEED, 0)
                bg = lighten_color(COLOR_DROPDOWN_MENU, int(self.option_hover_amount[i]))
                pygame.draw.rect(content_surf, bg, item_rect)

                # Text cho option
                txt2 = self.font.render(opt, True, COLOR_TEXT)
                txt2_rect = txt2.get_rect()
                txt2_rect.left = item_rect.left + PADDING_X
                txt2_rect.centery = item_rect.centery
                content_surf.blit(txt2, txt2_rect)

            # Áp mask bo góc
            content_surf.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            # Tạo final_surf với nền và viền bo góc
            final_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(final_surf, COLOR_DROPDOWN_MENU,
                             final_surf.get_rect(),
                             border_radius=DROPDOWN_RADIUS)
            pygame.draw.rect(final_surf, BUTTON_OUTLINE_COLOR,
                             final_surf.get_rect(),
                             BUTTON_OUTLINE_THICKNESS,
                             border_radius=DROPDOWN_RADIUS)

            # Blit content lên final_surf rồi ra màn hình
            final_surf.blit(content_surf, (0, 0))
            screen.blit(final_surf, menu_rect.topleft)

    def is_clicked(self, mx, my):
        
        if self.header_rect.collidepoint(mx, my):
            self.is_open = not self.is_open
            return None  
        
        if self.is_open:
            for i, _ in enumerate(self.options):
                item_rect = pygame.Rect(
                    self.header_rect.x,
                    self.header_rect.y + (i + 1) * self.header_rect.height,
                    self.header_rect.width,
                    self.header_rect.height
                )
                if item_rect.collidepoint(mx, my):
                    self.current = i
                    self.is_open = False
                    return i
        return None
