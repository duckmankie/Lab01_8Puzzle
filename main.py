import pygame
import sys
from constants import *
from puzzle import EightPuzzle, pixel_to_grid
from ui import Button, Checkbox, Dropdown

def main():
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    game_icon = pygame.image.load("assets/icon_32.png").convert_alpha()
    pygame.display.set_caption("8-Puzzle")
    pygame.display.set_icon(game_icon)
    
    puzzle = EightPuzzle(screen)

    
    solve_btn = Button(RIGHT_PANEL_X + 20, 200, RIGHT_PANEL_WIDTH - 40, 50, "Solve/Stop")
    next_btn = Button(RIGHT_PANEL_X + 20, 270, RIGHT_PANEL_WIDTH - 40, 50, "Next Step")
    reset_btn = Button(RIGHT_PANEL_X + 20, 340, RIGHT_PANEL_WIDTH - 40, 50, "Reset")

    combo = Dropdown(RIGHT_PANEL_X + 20, 140, RIGHT_PANEL_WIDTH - 40, 40, ALGORITHMS)
    checkbox = Checkbox(CHECKBOX_X, CHECKBOX_Y, CHECKBOX_SIZE, "Show Numbers")

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()

                
                if (PUZZLE_OFFSET_X <= mx < PUZZLE_OFFSET_X + PUZZLE_SIZE and
                    PUZZLE_OFFSET_Y <= my < PUZZLE_OFFSET_Y + PUZZLE_SIZE and
                    not puzzle.in_reset and not puzzle.in_fade):
                    gr, gc = pixel_to_grid(mx, my)
                    if gr is not None:
                        puzzle.start_move(gr, gc)
                        continue

                
                if checkbox.is_clicked(mx, my):
                    puzzle.toggle_numbers()
                    continue

                
                if solve_btn.is_clicked(mx, my):
                    puzzle.solve()
                    continue
                if next_btn.is_clicked(mx, my):
                    
                    continue
                if reset_btn.is_clicked(mx, my):
                    puzzle.shuffle()
                    continue

                
                dd_choice = combo.is_clicked(mx, my)
                if dd_choice is not None:
                    puzzle.selected_algorithm = ALGORITHMS[dd_choice]
                    continue

                
                
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
                        break

        
        puzzle.update()

        
        puzzle.draw_background()
        
        puzzle.draw_puzzle()
        
        solve_btn.draw(screen)
        next_btn.draw(screen)
        reset_btn.draw(screen)
        combo.draw(screen)
        checkbox.draw(screen)

        
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

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
