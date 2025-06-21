

import pygame
from constants import *

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
