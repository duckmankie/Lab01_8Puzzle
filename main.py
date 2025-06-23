import pygame
import sys
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, FPS
from puzzle import EightPuzzle
from ui import GameUI

def main():
    pygame.init()
    pygame.display.set_caption("Eight Puzzle Solver")
    pygame.display.set_icon(pygame.image.load("assets/icon_32.png"))
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    puzzle = EightPuzzle(screen)
    ui = GameUI(screen, puzzle)
    running = True
    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                ui.handle_click(mx, my)
        puzzle.update()
        puzzle.draw_background()
        puzzle.draw_puzzle()
        ui.draw()
        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
