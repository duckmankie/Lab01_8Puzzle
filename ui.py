

import pygame
from constants import *

class Button:
    def __init__(self, x, y, w, h, label):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.font = pygame.font.SysFont(None, 30)

    def draw(self, screen):
        mx, my = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mx, my)
        color = COLOR_BUTTON_HOVER if hovered else COLOR_BUTTON
        pygame.draw.rect(screen, color, self.rect)
        txt = self.font.render(self.label, True, COLOR_TEXT)
        txt_pos = (
            self.rect.x + (self.rect.width - txt.get_width()) // 2,
            self.rect.y + (self.rect.height - txt.get_height()) // 2
        )
        screen.blit(txt, txt_pos)

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
        pygame.draw.rect(screen, color, self.rect)
        if self.is_checked:
            
            pygame.draw.line(screen, COLOR_TEXT,
                             (self.rect.x + 4, self.rect.y + self.rect.height // 2),
                             (self.rect.x + self.rect.width // 2, self.rect.y + self.rect.height - 4), 3)
            pygame.draw.line(screen, COLOR_TEXT,
                             (self.rect.x + self.rect.width // 2, self.rect.y + self.rect.height - 4),
                             (self.rect.x + self.rect.width - 4, self.rect.y + 4), 3)
        
        lbl = self.font.render(self.label, True, COLOR_TEXT)
        screen.blit(lbl, (self.rect.x + self.rect.width + 5, self.rect.y - 2))

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

    def draw(self, screen):
        
        mx, my = pygame.mouse.get_pos()
        hovered = self.header_rect.collidepoint(mx, my)
        color = COLOR_BUTTON_HOVER if hovered else COLOR_BUTTON
        pygame.draw.rect(screen, color, self.header_rect)
        txt = self.font.render(self.options[self.current], True, COLOR_TEXT)
        screen.blit(txt, (self.header_rect.x + 10, self.header_rect.y + 8))
        
        pygame.draw.polygon(screen, COLOR_TEXT, [
            (self.header_rect.right - 20, self.header_rect.y + 15),
            (self.header_rect.right - 10, self.header_rect.y + 15),
            (self.header_rect.right - 15, self.header_rect.y + 25)
        ])

        
        if self.is_open:
            for i, opt in enumerate(self.options):
                item_rect = pygame.Rect(
                    self.header_rect.x,
                    self.header_rect.y + (i + 1) * self.header_rect.height,
                    self.header_rect.width,
                    self.header_rect.height
                )
                pygame.draw.rect(screen, COLOR_BUTTON, item_rect)
                txt2 = self.font.render(opt, True, COLOR_TEXT)
                screen.blit(txt2, (item_rect.x + 10, item_rect.y + 8))

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
