import pygame
from constants import *
from puzzle import pixel_to_grid

def draw_ui(screen, solve_btn, next_btn, reset_btn, dropdown, checkbox, puzzle, is_solving, solve_btn_color_progress, tween_color, solve_btn_disabled=False):
    solve_btn.draw(screen, disabled_hover=False, disabled=False, color_override=solve_btn.color_override)
    next_btn.draw(screen, disabled_hover=False)
    reset_btn.draw(screen, disabled_hover=False)
    font_label = pygame.font.Font("assets/fonts/HelveticaNeueRoman.otf", 18)
    label_surface = font_label.render("Choose Algorithm", True, COLOR_TEXT)
    label_x = dropdown.header_rect.x
    label_y = dropdown.header_rect.y - label_surface.get_height() - 8
    screen.blit(label_surface, (label_x, label_y))
    dropdown.draw(screen)
    checkbox.draw(screen)
    thumb_y = 20
    thumb_x = RIGHT_PANEL_X + 50
    puzzle._thumb_x = thumb_x
    puzzle._thumb_y = thumb_y
    if not hasattr(puzzle, 'thumb_scroll_offset'):
        puzzle.thumb_scroll_offset = 0
    if not hasattr(puzzle, 'thumb_scroll_anim'):
        puzzle.thumb_scroll_anim = 0.0
    max_offset = max(0, len(puzzle.templates) - THUMBS_PER_ROW)
    puzzle.thumb_scroll_offset = min(max(0, puzzle.thumb_scroll_offset), max_offset)
    SCROLL_ANIM_SPEED = 0.25
    if abs(puzzle.thumb_scroll_anim - puzzle.thumb_scroll_offset) > 0.01:
        puzzle.thumb_scroll_anim += (puzzle.thumb_scroll_offset - puzzle.thumb_scroll_anim) * SCROLL_ANIM_SPEED
    else:
        puzzle.thumb_scroll_anim = float(puzzle.thumb_scroll_offset)
    frame_width = THUMBS_PER_ROW * (IMAGE_THUMB_SIZE + THUMBS_SPACING) - THUMBS_SPACING
    frame_height = IMAGE_THUMB_SIZE
    frame_surf = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
    for i in range(len(puzzle.templates)):
        offset_x = (i - puzzle.thumb_scroll_anim) * (IMAGE_THUMB_SIZE + THUMBS_SPACING)
        rect = pygame.Rect(
            int(offset_x),
            0,
            IMAGE_THUMB_SIZE,
            IMAGE_THUMB_SIZE
        )
        if rect.right < 0 or rect.left > frame_width:
            continue
        frame_surf.blit(puzzle.thumb_surfaces[i], rect.topleft)
        if i == puzzle.selected_index:
            pygame.draw.rect(frame_surf, COLOR_HIGHLIGHT, rect, 3)
    screen.blit(frame_surf, (thumb_x, thumb_y))
    arrow_size = 18
    arrow_offset_y = thumb_y + IMAGE_THUMB_SIZE // 2 - arrow_size // 2
    arrow_center_y = thumb_y + IMAGE_THUMB_SIZE // 2
    if not hasattr(puzzle, 'arrow_hover_left'):
        puzzle.arrow_hover_left = 0
    if not hasattr(puzzle, 'arrow_hover_right'):
        puzzle.arrow_hover_right = 0
    if len(puzzle.templates) > THUMBS_PER_ROW:
        mx, my = pygame.mouse.get_pos()
        left_rect = pygame.Rect(thumb_x - arrow_size - 8, arrow_offset_y, arrow_size, arrow_size)
        left_hovered = left_rect.collidepoint(mx, my)
        if left_hovered:
            puzzle.arrow_hover_left = min(puzzle.arrow_hover_left + 8, 40)
        else:
            puzzle.arrow_hover_left = max(puzzle.arrow_hover_left - 8, 0)
        from constants import lighten_color
        left_color = lighten_color(COLOR_TEXT, puzzle.arrow_hover_left)
        pygame.draw.polygon(screen, left_color, [
            (left_rect.right, left_rect.top),
            (left_rect.left, left_rect.centery),
            (left_rect.right, left_rect.bottom)
        ])
        right_rect = pygame.Rect(thumb_x + THUMBS_PER_ROW * (IMAGE_THUMB_SIZE + THUMBS_SPACING) + 8, arrow_offset_y, arrow_size, arrow_size)
        right_hovered = right_rect.collidepoint(mx, my)
        if right_hovered:
            puzzle.arrow_hover_right = min(puzzle.arrow_hover_right + 8, 40)
        else:
            puzzle.arrow_hover_right = max(puzzle.arrow_hover_right - 8, 0)
        right_color = lighten_color(COLOR_TEXT, puzzle.arrow_hover_right)
        pygame.draw.polygon(screen, right_color, [
            (right_rect.left, right_rect.top),
            (right_rect.right, right_rect.centery),
            (right_rect.left, right_rect.bottom)
        ])


def handle_ui_event(event, puzzle, solve_btn, next_btn, reset_btn, dropdown, checkbox, is_solving):
    action = None
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        mx, my = pygame.mouse.get_pos()
        if not is_solving:
            dd_choice = dropdown.is_clicked(mx, my)
            if dd_choice is not None:
                puzzle.selected_algorithm = ALGORITHMS[dd_choice]
                action = 'algorithm_changed'
                return is_solving, action
        if dropdown.is_open and not is_solving:
            dropdown_rect = dropdown.header_rect.copy()
            dropdown_rect.height += dropdown.header_rect.height * (len(dropdown.options))
            if not dropdown_rect.collidepoint(mx, my):
                dropdown.is_open = False
            else:
                return is_solving, action
        if (not is_solving and PUZZLE_OFFSET_X <= mx < PUZZLE_OFFSET_X + PUZZLE_SIZE and
            PUZZLE_OFFSET_Y <= my < PUZZLE_OFFSET_Y + PUZZLE_SIZE and
            not puzzle.in_reset and not puzzle.in_fade):
            gr, gc = pixel_to_grid(mx, my)
            if gr is not None:
                puzzle.start_move(gr, gc)
                action = 'board_changed'
                return is_solving, action
        if checkbox.is_clicked(mx, my):
            puzzle.toggle_numbers()
            return is_solving, action
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
        if not is_solving:
            thumb_x = getattr(puzzle, '_thumb_x', RIGHT_PANEL_X + 50)
            thumb_y = getattr(puzzle, '_thumb_y', 20)
            if not hasattr(puzzle, 'thumb_scroll_offset'):
                puzzle.thumb_scroll_offset = 0
            arrow_size = 18
            arrow_offset_y = thumb_y + IMAGE_THUMB_SIZE // 2 - arrow_size // 2
            if len(puzzle.templates) > THUMBS_PER_ROW:
                left_rect = pygame.Rect(thumb_x - arrow_size - 8, arrow_offset_y, arrow_size, arrow_size)
                right_rect = pygame.Rect(thumb_x + THUMBS_PER_ROW * (IMAGE_THUMB_SIZE + THUMBS_SPACING) + 8, arrow_offset_y, arrow_size, arrow_size)
                if left_rect.collidepoint(mx, my) and puzzle.thumb_scroll_offset > 0:
                    puzzle.thumb_scroll_offset -= 1
                    return is_solving, action
                if right_rect.collidepoint(mx, my) and puzzle.thumb_scroll_offset < max(0, len(puzzle.templates) - THUMBS_PER_ROW):
                    puzzle.thumb_scroll_offset += 1
                    return is_solving, action
            frame_width = THUMBS_PER_ROW * (IMAGE_THUMB_SIZE + THUMBS_SPACING) - THUMBS_SPACING
            frame_height = IMAGE_THUMB_SIZE
            rel_mx = mx - thumb_x
            rel_my = my - thumb_y
            for i in range(len(puzzle.templates)):
                offset_x = (i - puzzle.thumb_scroll_anim) * (IMAGE_THUMB_SIZE + THUMBS_SPACING)
                rect = pygame.Rect(
                    int(offset_x),
                    0,
                    IMAGE_THUMB_SIZE,
                    IMAGE_THUMB_SIZE
                )
                if rect.right < 0 or rect.left > frame_width:
                    continue
                if rect.collidepoint(rel_mx, rel_my):
                    puzzle.prepare_fade(i)
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
        self.locked_interaction = False

    def draw(self):
        if not hasattr(self.solve_btn, 'prev_state'):
            self.solve_btn.prev_state = 'normal'
        if not hasattr(self, 'solve_btn_color_progress'):
            self.solve_btn_color_progress = 0.0
        if self.puzzle.completed:
            curr_state = 'solved'
        elif self.puzzle.is_calculating:
            curr_state = 'calculating'
        elif self.puzzle.auto_solving:
            curr_state = 'stop'
        elif self.solve_btn.disabled:
            curr_state = 'disabled'
        else:
            curr_state = 'normal'
        SOLVE_COLOR_NORMAL = COLOR_BUTTON
        SOLVE_COLOR_STOP = (244,60,68)
        SOLVE_COLOR_DISABLED = darken_color(COLOR_BUTTON, 40)
        if self.solve_btn.prev_state != curr_state:
            self.solve_btn_color_progress = 0.0
        if curr_state == 'stop':
            if self.solve_btn_color_progress < 1.0:
                self.solve_btn_color_progress = min(1.0, self.solve_btn_color_progress + self.SOLVE_BTN_TWEEN_SPEED)
            color_now = tuple(
                int(SOLVE_COLOR_NORMAL[i] + (SOLVE_COLOR_STOP[i] - SOLVE_COLOR_NORMAL[i]) * self.solve_btn_color_progress)
                for i in range(3)
            )
        elif curr_state == 'normal':
            if self.solve_btn_color_progress > 0.0:
                self.solve_btn_color_progress = max(0.0, self.solve_btn_color_progress - self.SOLVE_BTN_TWEEN_SPEED)
            color_now = tuple(
                int(SOLVE_COLOR_NORMAL[i] + (SOLVE_COLOR_STOP[i] - SOLVE_COLOR_NORMAL[i]) * self.solve_btn_color_progress)
                for i in range(3)
            )
        elif curr_state == 'disabled':
            if self.solve_btn_color_progress < 1.0:
                self.solve_btn_color_progress = min(1.0, self.solve_btn_color_progress + self.SOLVE_BTN_TWEEN_SPEED)
            color_now = tuple(
                int(SOLVE_COLOR_NORMAL[i] + (SOLVE_COLOR_DISABLED[i] - SOLVE_COLOR_NORMAL[i]) * self.solve_btn_color_progress)
                for i in range(3)
            )
        elif curr_state == 'calculating':
            color_now = SOLVE_COLOR_NORMAL
        elif curr_state == 'solved':
            color_now = COLOR_BG
        else:
            color_now = SOLVE_COLOR_NORMAL
        if curr_state == 'solved':
            self.solve_btn.label = "Solved"
            self.solve_btn.disabled = True
            self.solve_btn.outline_override = None
        elif curr_state == 'calculating':
            self.solve_btn.label = "Calculating..."
            self.solve_btn.disabled = True
            self.solve_btn.outline_override = None
        elif curr_state == 'stop':
            self.solve_btn.label = "Stop"
            self.solve_btn.disabled = False
            self.solve_btn.outline_override = (237,20,20)
        else:
            self.solve_btn.label = "Solve"
            self.solve_btn.disabled = False
            self.solve_btn.outline_override = None
        self.solve_btn.color_override = color_now
        self.solve_btn.prev_state = curr_state
        self.next_btn.disabled = (
            self.puzzle.is_calculating or
            not self.puzzle.solution_path or
            self.puzzle.completed or
            self.puzzle.auto_solving
        )
        self.reset_btn.disabled = (
            self.puzzle.is_calculating or
            self.puzzle.auto_solving
        )
        self.dropdown.disabled = self.puzzle.is_calculating or self.puzzle.auto_solving
        draw_ui(self.screen, self.solve_btn, self.next_btn, self.reset_btn, self.dropdown, self.checkbox, self.puzzle, self.is_solving, self.solve_btn_color_progress, self.solve_btn.color_override, solve_btn_disabled=self.solve_btn.disabled)
        font_result = pygame.font.Font("assets/fonts/HelveticaNeueRoman.otf", 20)
        x = RIGHT_PANEL_X + 20
        y = 390
        color = COLOR_TEXT
        line_spacing = 14
        if self.is_solving:
            steps_str = ""
            expanded_str = ""
            frontier_str = ""
            cost_str = ""
            time_str = ""
        else:
            steps_str = str(len(self.puzzle.solution_path)) if self.puzzle.solution_path else "0"
            expanded_str = str(self.puzzle.nodes_expanded) if self.puzzle.solution_path else "0"
            frontier_str = str(self.puzzle.frontier_nodes) if self.puzzle.solution_path else "0"
            cost_str = str(self.puzzle.total_cost) if self.puzzle.solution_path else "0"
            time_str = f"{self.puzzle.solve_time:.3f} s" if self.puzzle.solution_path else "0.000 s"
        lines = [
            f"Steps: {steps_str}",
            f"Expanded nodes: {expanded_str}",
            f"Frontier nodes: {frontier_str}",
            f"Total cost: {cost_str}",
            f"Processing time: {time_str}",
        ]
        for line in lines:
            surf = font_result.render(line, True, color)
            self.screen.blit(surf, (x, y))
            y += surf.get_height() + line_spacing
        self.dropdown.draw(self.screen)

    def handle_click(self, mx, my):
        if (self.dropdown.header_rect.collidepoint(mx, my) or self.dropdown.is_open) and not (self.puzzle.auto_solving or self.puzzle.is_calculating):
            was_open = self.dropdown.is_open
            dd_choice = self.dropdown.is_clicked(mx, my)
            if was_open and dd_choice is not None:
                new_algo = self.dropdown.options[dd_choice]
                if new_algo != self.puzzle.selected_algorithm:
                    self.puzzle.selected_algorithm = new_algo
                    self.puzzle.reset_solve_state()
                    self.solve_btn.label = "Solve"
                    self.solve_btn.color_override = None
                    self.solve_btn.disabled = False
                    self.is_solving = False
                    self.locked_interaction = False
                return
            if not was_open and self.dropdown.is_open:
                return
            if was_open and not self.dropdown.is_open:
                return
        if self.locked_interaction:
            if self.puzzle.auto_solving:
                if self.dropdown.header_rect.collidepoint(mx, my):
                    return
                thumb_x = getattr(self.puzzle, '_thumb_x', RIGHT_PANEL_X + 50)
                thumb_y = getattr(self.puzzle, '_thumb_y', 20)
                frame_width = THUMBS_PER_ROW * (IMAGE_THUMB_SIZE + THUMBS_SPACING) - THUMBS_SPACING
                frame_height = IMAGE_THUMB_SIZE
                rel_mx = mx - thumb_x
                rel_my = my - thumb_y
                for i in range(len(self.puzzle.templates)):
                    offset_x = (i - self.puzzle.thumb_scroll_anim) * (IMAGE_THUMB_SIZE + THUMBS_SPACING)
                    rect = pygame.Rect(
                        int(offset_x),
                        0,
                        IMAGE_THUMB_SIZE,
                        IMAGE_THUMB_SIZE
                    )
                    if rect.right < 0 or rect.left > frame_width:
                        continue
                    if rect.collidepoint(rel_mx, rel_my):
                        return
                if (PUZZLE_OFFSET_X <= mx < PUZZLE_OFFSET_X + PUZZLE_SIZE and
                    PUZZLE_OFFSET_Y <= my < PUZZLE_OFFSET_Y + PUZZLE_SIZE):
                    return
            else:
                if self.dropdown.header_rect.collidepoint(mx, my):
                    current_algo = self.dropdown.options[self.dropdown.current]
                    dd_choice = self.dropdown.is_clicked(mx, my)
                    if dd_choice is not None:
                        new_algo = ALGORITHMS[dd_choice]
                        self.puzzle.selected_algorithm = new_algo
                        if new_algo != current_algo:
                            self.puzzle.reset_solve_state()
                            self.solve_btn.label = "Solve"
                            self.solve_btn.color_override = None
                            self.is_solving = False
                            self.locked_interaction = False
                            self.dropdown.current = dd_choice
                    return
                thumb_x = getattr(self.puzzle, '_thumb_x', RIGHT_PANEL_X + 50)
                thumb_y = getattr(self.puzzle, '_thumb_y', 20)
                frame_width = THUMBS_PER_ROW * (IMAGE_THUMB_SIZE + THUMBS_SPACING) - THUMBS_SPACING
                frame_height = IMAGE_THUMB_SIZE
                rel_mx = mx - thumb_x
                rel_my = my - thumb_y
                for i in range(len(self.puzzle.templates)):
                    offset_x = (i - self.puzzle.thumb_scroll_anim) * (IMAGE_THUMB_SIZE + THUMBS_SPACING)
                    rect = pygame.Rect(
                        int(offset_x),
                        0,
                        IMAGE_THUMB_SIZE,
                        IMAGE_THUMB_SIZE
                    )
                    if rect.right < 0 or rect.left > frame_width:
                        continue
                    if rect.collidepoint(rel_mx, rel_my):
                        self.puzzle.prepare_fade(i)
                        self.solve_btn.label = "Solve"
                        self.solve_btn.color_override = None
                        self.is_solving = False
                        self.locked_interaction = False
                        return
                if (PUZZLE_OFFSET_X <= mx < PUZZLE_OFFSET_X + PUZZLE_SIZE and
                    PUZZLE_OFFSET_Y <= my < PUZZLE_OFFSET_Y + PUZZLE_SIZE):
                    return
        if self.puzzle.completed:
            self.locked_interaction = False
            if self.reset_btn.is_clicked(mx, my):
                self.puzzle.shuffle()
                self.solve_btn.label = "Solve"
                self.solve_btn.color_override = None
                self.is_solving = False
                self.locked_interaction = False
                return
            if self.checkbox.is_clicked(mx, my):
                self.puzzle.toggle_numbers()
                return
            return
        if not self.is_solving and not self.puzzle.is_calculating and not self.puzzle.auto_solving:
            dd_choice = self.dropdown.is_clicked(mx, my)
            if dd_choice is not None:
                self.puzzle.selected_algorithm = ALGORITHMS[dd_choice]
                return
        if self.dropdown.is_open and not self.is_solving and not self.puzzle.is_calculating and not self.puzzle.auto_solving:
            dropdown_rect = self.dropdown.header_rect.copy()
            dropdown_rect.height += self.dropdown.header_rect.height * (len(self.dropdown.options))
            if not dropdown_rect.collidepoint(mx, my):
                self.dropdown.is_open = False
            else:
                return
        if (not self.is_solving and PUZZLE_OFFSET_X <= mx < PUZZLE_OFFSET_X + PUZZLE_SIZE and
            PUZZLE_OFFSET_Y <= my < PUZZLE_OFFSET_Y + PUZZLE_SIZE and
            not self.puzzle.in_reset and not self.puzzle.in_fade):
            gr, gc = pixel_to_grid(mx, my)
            if gr is not None:
                self.puzzle.start_move(gr, gc)
                return
        if not self.puzzle.is_calculating and not self.puzzle.auto_solving and self.checkbox.is_clicked(mx, my):
            self.puzzle.toggle_numbers()
            return
        if self.solve_btn.is_clicked(mx, my):
            if self.puzzle.is_calculating or self.puzzle.completed:
                return
            if self.puzzle.auto_solving:
                self.puzzle.stop_solve()
                self.solve_btn.label = "Solve"
                self.solve_btn.color_override = None
            else:
                if not self.puzzle.solution_path:
                    self.puzzle.solve()
                    self.locked_interaction = True
                else:
                    self.puzzle.auto_solving = True
                    if self.puzzle.auto_solve_index >= len(self.puzzle.solution_path):
                        self.puzzle.auto_solve_index = 0
                    self.locked_interaction = True
            return
        if self.next_btn.is_clicked(mx, my):
            self.puzzle.next_step()
            return
        if self.reset_btn.is_clicked(mx, my) and not self.is_solving:
            self.puzzle.shuffle()
            self.solve_btn.label = "Solve"
            self.solve_btn.color_override = None
            self.is_solving = False
            self.locked_interaction = False
            return
        if not self.is_solving and not self.puzzle.is_calculating and not self.puzzle.auto_solving and not self.puzzle.completed:
            thumb_x = getattr(self.puzzle, '_thumb_x', RIGHT_PANEL_X + 50)
            thumb_y = getattr(self.puzzle, '_thumb_y', 20)
            if not hasattr(self.puzzle, 'thumb_scroll_offset'):
                self.puzzle.thumb_scroll_offset = 0
            arrow_size = 18
            arrow_offset_y = thumb_y + IMAGE_THUMB_SIZE // 2 - arrow_size // 2
            if len(self.puzzle.templates) > THUMBS_PER_ROW:
                left_rect = pygame.Rect(thumb_x - arrow_size - 8, arrow_offset_y, arrow_size, arrow_size)
                right_rect = pygame.Rect(thumb_x + THUMBS_PER_ROW * (IMAGE_THUMB_SIZE + THUMBS_SPACING) + 8, arrow_offset_y, arrow_size, arrow_size)
                if left_rect.collidepoint(mx, my) and self.puzzle.thumb_scroll_offset > 0:
                    self.puzzle.thumb_scroll_offset -= 1
                    return
                if right_rect.collidepoint(mx, my) and self.puzzle.thumb_scroll_offset < max(0, len(self.puzzle.templates) - THUMBS_PER_ROW):
                    self.puzzle.thumb_scroll_offset += 1
                    return
            frame_width = THUMBS_PER_ROW * (IMAGE_THUMB_SIZE + THUMBS_SPACING) - THUMBS_SPACING
            frame_height = IMAGE_THUMB_SIZE
            rel_mx = mx - thumb_x
            rel_my = my - thumb_y
            for i in range(len(self.puzzle.templates)):
                offset_x = (i - self.puzzle.thumb_scroll_anim) * (IMAGE_THUMB_SIZE + THUMBS_SPACING)
                rect = pygame.Rect(
                    int(offset_x),
                    0,
                    IMAGE_THUMB_SIZE,
                    IMAGE_THUMB_SIZE
                )
                if rect.right < 0 or rect.left > frame_width:
                    continue
                if rect.collidepoint(rel_mx, rel_my):
                    self.puzzle.prepare_fade(i)
                    self.solve_btn.label = "Solve"
                    self.solve_btn.color_override = None
                    self.is_solving = False
                    return

class Button:
    def __init__(self, x, y, w, h, label, color_override=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.font = pygame.font.Font("assets/fonts/HelveticaNeueRoman.otf", 22)
        self.hover_amount = 0
        self.color_override = color_override
        self.disabled = False

    def draw(self, screen, disabled_hover=False, disabled=False, color_override=None):
        mx, my = pygame.mouse.get_pos()
        is_disabled = getattr(self, 'disabled', False) or disabled
        hovered = self.rect.collidepoint(mx, my) and not disabled_hover and not is_disabled
        from constants import lighten_color
        base_color = self.color_override if self.color_override is not None else COLOR_BUTTON
        if color_override is not None:
            base_color = color_override
        from constants import darken_color
        if is_disabled:
            base_color = darken_color(base_color, 40)
        if hovered:
            self.hover_amount = min(self.hover_amount + FADE_HOVER_SPEED, 40)
        else:
            self.hover_amount = max(self.hover_amount - FADE_HOVER_SPEED, 0)
        color = lighten_color(base_color, int(self.hover_amount) if not is_disabled else 0)
        pygame.draw.rect(screen, color, self.rect, border_radius=BUTTON_RADIUS)
        outline_color = getattr(self, 'outline_override', None) or BUTTON_OUTLINE_COLOR
        pygame.draw.rect(screen, outline_color, self.rect, BUTTON_OUTLINE_THICKNESS, border_radius=BUTTON_RADIUS)
        txt_color = COLOR_TEXT if not is_disabled else darken_color(COLOR_TEXT, 100)
        txt = self.font.render(self.label, True, txt_color)
        PADDING_X = 12
        PADDING_Y = 6
        txt_rect = txt.get_rect()
        txt_rect.centerx = self.rect.centerx
        txt_rect.centery = self.rect.centery
        if txt_rect.width > self.rect.width - 2 * PADDING_X:
            txt_rect.width = self.rect.width - 2 * PADDING_X
        if txt_rect.height > self.rect.height - 2 * PADDING_Y:
            txt_rect.height = self.rect.height - 2 * PADDING_Y
        screen.blit(txt, txt_rect)

    def is_clicked(self, mx, my):
        if getattr(self, 'disabled', False):
            return False
        return self.rect.collidepoint(mx, my)


class Checkbox:
    def __init__(self, x, y, size, label):
        self.rect = pygame.Rect(x, y, size, size)
        self.label = label
        self.font = pygame.font.Font("assets/fonts/HelveticaNeueRoman.otf", 18)
        self.is_checked = False
        self.disabled = False

    def draw(self, screen):
        mx, my = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mx, my)
        from constants import lighten_color, darken_color
        color = lighten_color(CHECKBOX_BUTTON, 40) if hovered and not self.disabled else CHECKBOX_BUTTON
        if self.disabled:
            color = darken_color(color, 40)
        pygame.draw.rect(screen, color, self.rect)
        if self.is_checked:
            pygame.draw.line(screen, COLOR_TEXT,
                             (self.rect.x + 4, self.rect.y + self.rect.height // 2),
                             (self.rect.x + self.rect.width // 2, self.rect.y + self.rect.height - 4), 3)
            pygame.draw.line(screen, COLOR_TEXT,
                             (self.rect.x + self.rect.width // 2, self.rect.y + self.rect.height - 4),
                             (self.rect.x + self.rect.width - 4, self.rect.y + 4), 3)
        lbl_color = COLOR_TEXT if not self.disabled else darken_color(COLOR_TEXT, 100)
        lbl = self.font.render(self.label, True, lbl_color)
        label_y = self.rect.y + (self.rect.height - lbl.get_height()) // 2
        screen.blit(lbl, (self.rect.x + self.rect.width + 8, label_y))

    def is_clicked(self, mx, my):
        if self.disabled:
            return False
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
        self.hover_amount = 0
        self.disabled = False

    def draw(self, screen):
        mx, my = pygame.mouse.get_pos()
        from constants import lighten_color, darken_color
        hovered = self.header_rect.collidepoint(mx, my)
        color = lighten_color(COLOR_DROPDOWN_BUTTON, int(self.hover_amount))
        if self.disabled:
            color = darken_color(color, 40)
        if hovered and not self.disabled:
            self.hover_amount = min(self.hover_amount + FADE_HOVER_SPEED, 40)
        else:
            self.hover_amount = max(self.hover_amount - FADE_HOVER_SPEED, 0)
        pygame.draw.rect(screen, color, self.header_rect, border_radius=DROPDOWN_RADIUS)
        PADDING_X = 12
        PADDING_Y = 6
        ARROW_PADDING = 35
        txt_color = COLOR_TEXT if not self.disabled else darken_color(COLOR_TEXT, 100)
        txt = self.font.render(self.options[self.current], True, txt_color)
        txt_rect = txt.get_rect()
        txt_rect.left = self.header_rect.left + PADDING_X
        txt_rect.centery = self.header_rect.centery
        if txt_rect.width > self.header_rect.width - 2 * PADDING_X:
            txt_rect.width = self.header_rect.width - 2 * PADDING_X
        if txt_rect.height > self.header_rect.height - 2 * PADDING_Y:
            txt_rect.height = self.header_rect.height - 2 * PADDING_Y
        screen.blit(txt, txt_rect)
        arrow_x = self.header_rect.right - ARROW_PADDING
        arrow_y = self.header_rect.centery
        v_width = 14
        v_height = 8
        arrow_color = COLOR_TEXT if not self.disabled else darken_color(COLOR_TEXT, 100)
        pygame.draw.lines(screen, arrow_color, False, [
            (arrow_x, arrow_y - v_height // 2),
            (arrow_x + v_width // 2, arrow_y + v_height // 2),
            (arrow_x + v_width, arrow_y - v_height // 2)
        ], 3)
        if self.is_open and not self.disabled:
            menu_rect = pygame.Rect(
                self.header_rect.x,
                self.header_rect.y + self.header_rect.height,
                self.header_rect.width,
                self.header_rect.height * len(self.options)
            )
            w, h = menu_rect.size
            content_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            mask_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(mask_surf, (255,255,255,255),
                             mask_surf.get_rect(),
                             border_radius=DROPDOWN_RADIUS)
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
                txt2_color = COLOR_TEXT if not self.disabled else darken_color(COLOR_TEXT, 100)
                txt2 = self.font.render(opt, True, txt2_color)
                txt2_rect = txt2.get_rect()
                txt2_rect.left = item_rect.left + PADDING_X
                txt2_rect.centery = item_rect.centery
                content_surf.blit(txt2, txt2_rect)
            content_surf.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            final_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(final_surf, COLOR_DROPDOWN_MENU,
                             final_surf.get_rect(),
                             border_radius=DROPDOWN_RADIUS)
            pygame.draw.rect(final_surf, BUTTON_OUTLINE_COLOR,
                             final_surf.get_rect(),
                             BUTTON_OUTLINE_THICKNESS,
                             border_radius=DROPDOWN_RADIUS)
            final_surf.blit(content_surf, (0, 0))
            screen.blit(final_surf, menu_rect.topleft)

    def is_clicked(self, mx, my):
        if self.disabled:
            return None
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
