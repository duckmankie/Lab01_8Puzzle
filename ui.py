

import pygame
from constants import *
from puzzle import pixel_to_grid

def draw_ui(screen, solve_btn, next_btn, reset_btn, combo, checkbox, puzzle, is_solving, solve_btn_color_progress, tween_color, solve_btn_disabled=False):
    # Draw border around button group
    BUTTON_GROUP_PADDING = 10
    group_left = solve_btn.rect.x - BUTTON_GROUP_PADDING
    group_top = solve_btn.rect.y - BUTTON_GROUP_PADDING
    group_width = solve_btn.rect.width + 2 * BUTTON_GROUP_PADDING
    group_height = (reset_btn.rect.bottom - solve_btn.rect.y) + 2 * BUTTON_GROUP_PADDING
    pygame.draw.rect(screen, (120, 120, 120), (group_left, group_top, group_width, group_height), 2)
    # Draw solve_btn with tween color
    solve_btn.draw(screen, disabled_hover=False, disabled=False, color_override=tween_color)
    if solve_btn_disabled:
        s = pygame.Surface((solve_btn.rect.width, solve_btn.rect.height), pygame.SRCALPHA)
        s.fill((0,0,0,80))
        screen.blit(s, solve_btn.rect.topleft)
    # Next/Reset buttons
    next_btn.draw(screen, disabled_hover=False)
    reset_btn.draw(screen, disabled_hover=False)
    combo.draw(screen)
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


def handle_ui_event(event, puzzle, solve_btn, next_btn, reset_btn, combo, checkbox, is_solving):
    action = None
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        mx, my = pygame.mouse.get_pos()
        # Dropdown click handling
        if not is_solving:
            dd_choice = combo.is_clicked(mx, my)
            if dd_choice is not None:
                puzzle.selected_algorithm = ALGORITHMS[dd_choice]
                action = 'algorithm_changed'
                return is_solving, action
        # Dropdown close if click outside
        if combo.is_open and not is_solving:
            dropdown_rect = combo.header_rect.copy()
            dropdown_rect.height += combo.header_rect.height * (len(combo.options))
            if not dropdown_rect.collidepoint(mx, my):
                combo.is_open = False
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
        self.solve_btn = Button(RIGHT_PANEL_X + 30, 215, RIGHT_PANEL_WIDTH - 60, 50, "Solve")
        self.next_btn = Button(RIGHT_PANEL_X + 30, 275, RIGHT_PANEL_WIDTH - 60, 50, "Next Step")
        self.reset_btn = Button(RIGHT_PANEL_X + 30, 335, RIGHT_PANEL_WIDTH - 60, 50, "Reset")
        self.combo = Dropdown(RIGHT_PANEL_X + 20, 140, RIGHT_PANEL_WIDTH - 40, 50, ALGORITHMS)
        self.checkbox = Checkbox(CHECKBOX_X, CHECKBOX_Y, CHECKBOX_SIZE, "Show Numbers")
        self.is_solving = False
        self.solve_btn_color_progress = 0.0
        self.SOLVE_BTN_TWEEN_SPEED = 0.08

    def draw(self):
        # Xử lý trạng thái nút Solve khi completed
        if self.puzzle.completed:
            self.solve_btn.label = "Solved"
            self.solve_btn.color_override = (60, 180, 60)
            solve_disabled = True
            self.is_solving = False
        else:
            if not self.is_solving:
                self.solve_btn.label = "Solve"
                self.solve_btn.color_override = None
            solve_disabled = False
        # Tween màu solve_btn
        solve_btn_base = (60, 60, 60)
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
        draw_ui(self.screen, self.solve_btn, self.next_btn, self.reset_btn, self.combo, self.checkbox, self.puzzle, self.is_solving, self.solve_btn_color_progress, tween_color, solve_btn_disabled=solve_disabled)

    def handle_click(self, mx, my):
        # Dropdown click
        if not self.is_solving:
            dd_choice = self.combo.is_clicked(mx, my)
            if dd_choice is not None:
                self.puzzle.selected_algorithm = ALGORITHMS[dd_choice]
                return
        # Dropdown close if click outside
        if self.combo.is_open and not self.is_solving:
            dropdown_rect = self.combo.header_rect.copy()
            dropdown_rect.height += self.combo.header_rect.height * (len(self.combo.options))
            if not dropdown_rect.collidepoint(mx, my):
                self.combo.is_open = False
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
        self.font = pygame.font.SysFont(None, 30)
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
            self.hover_amount = min(self.hover_amount + 8, 40)
        else:
            self.hover_amount = max(self.hover_amount - 8, 0)
        color = lighten_color(base_color, int(self.hover_amount) if not disabled else 0)
        pygame.draw.rect(screen, color, self.rect)
        txt = self.font.render(self.label, True, COLOR_TEXT)
        txt_rect = txt.get_rect(center=self.rect.center)
        screen.blit(txt, txt_rect)

    def is_clicked(self, mx, my):
        return self.rect.collidepoint(mx, my)


class Checkbox:
    def __init__(self, x, y, size, label):
        self.rect = pygame.Rect(x, y, size, size)
        self.label = label
        self.font = pygame.font.SysFont(None, 24)
        self.is_checked = False

    def draw(self, screen):
        mx, my = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mx, my)
        color = COLOR_BUTTON_HOVER if hovered else COLOR_BUTTON
        pygame.draw.rect(screen, color, self.rect, border_radius=6)
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
        self.font = pygame.font.SysFont(None, 30)
        self.hover_amount = 0  # For tween effect

    def draw(self, screen):
        mx, my = pygame.mouse.get_pos()
        hovered = self.header_rect.collidepoint(mx, my)
        from constants import COLOR_DROPDOWN, lighten_color
        # Tween hover effect for dropdown
        if hovered:
            self.hover_amount = min(self.hover_amount + 8, 40)
        else:
            self.hover_amount = max(self.hover_amount - 8, 0)
        color = lighten_color(COLOR_DROPDOWN, int(self.hover_amount))
        pygame.draw.rect(screen, color, self.header_rect)
        # Padding for arrow
        ARROW_PADDING = 35
        ARROW_WIDTH = 10
        ARROW_HEIGHT = 8
        # Adjust text rect to not overlap arrow
        text_area = pygame.Rect(
            self.header_rect.x + 8,
            self.header_rect.y,
            self.header_rect.width - ARROW_PADDING - 8,
            self.header_rect.height
        )
        txt = self.font.render(self.options[self.current], True, COLOR_TEXT)
        txt_rect = txt.get_rect(center=text_area.center)
        screen.blit(txt, txt_rect)
        # Draw arrow at right with padding
        arrow_x = self.header_rect.right - ARROW_PADDING
        arrow_y = self.header_rect.centery
        pygame.draw.polygon(screen, COLOR_TEXT, [
            (arrow_x, arrow_y - ARROW_HEIGHT // 2),
            (arrow_x + ARROW_WIDTH, arrow_y - ARROW_HEIGHT // 2),
            (arrow_x + ARROW_WIDTH // 2, arrow_y + ARROW_HEIGHT // 2)
        ])

        if self.is_open:
            for i, opt in enumerate(self.options):
                item_rect = pygame.Rect(
                    self.header_rect.x,
                    self.header_rect.y + (i + 1) * self.header_rect.height,
                    self.header_rect.width,
                    self.header_rect.height
                )
                from constants import COLOR_DROPDOWN, lighten_color
                if not hasattr(self, 'option_hover_amount'):
                    self.option_hover_amount = [0 for _ in self.options]
                hovered_item = item_rect.collidepoint(mx, my)
                # Tween for each option
                if hovered_item:
                    self.option_hover_amount[i] = min(self.option_hover_amount[i] + 8, 40)
                else:
                    self.option_hover_amount[i] = max(self.option_hover_amount[i] - 8, 0)
                color = lighten_color(COLOR_DROPDOWN, int(self.option_hover_amount[i]))
                pygame.draw.rect(screen, color, item_rect)
                # Padding for option text
                OPTION_PADDING = 12
                option_area = pygame.Rect(
                    item_rect.x + OPTION_PADDING,
                    item_rect.y,
                    item_rect.width - 2 * OPTION_PADDING,
                    item_rect.height
                )
                txt2 = self.font.render(opt, True, COLOR_TEXT)
                txt2_rect = txt2.get_rect(center=option_area.center)
                screen.blit(txt2, txt2_rect)

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
