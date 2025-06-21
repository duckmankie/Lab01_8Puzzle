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

    solve_btn = Button(RIGHT_PANEL_X + 30, 215, RIGHT_PANEL_WIDTH - 60, 50, "Solve")
    next_btn = Button(RIGHT_PANEL_X + 30, 275, RIGHT_PANEL_WIDTH - 60, 50, "Next Step")
    reset_btn = Button(RIGHT_PANEL_X + 30, 335, RIGHT_PANEL_WIDTH - 60, 50, "Reset")

    combo = Dropdown(RIGHT_PANEL_X + 20, 140, RIGHT_PANEL_WIDTH - 40, 50, ALGORITHMS)
    checkbox = Checkbox(CHECKBOX_X, CHECKBOX_Y, CHECKBOX_SIZE, "Show Numbers")

    is_solving = False
    solve_btn_color_progress = 0.0  # 0.0: màu gốc, 1.0: màu đỏ
    SOLVE_BTN_TWEEN_SPEED = 0.08

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()

                # Dropdown click handling (header toggle and option selection)
                if not is_solving:
                    dd_choice = combo.is_clicked(mx, my)
                    if dd_choice is not None:
                        puzzle.selected_algorithm = ALGORITHMS[dd_choice]
                        continue

                # Nếu dropdown đang mở, kiểm tra click có nằm ngoài vùng dropdown không
                if combo.is_open and not is_solving:
                    # Tính toán vùng dropdown (header + các option)
                    dropdown_rect = combo.header_rect.copy()
                    dropdown_rect.height += combo.header_rect.height * (len(combo.options))
                    if not dropdown_rect.collidepoint(mx, my):
                        combo.is_open = False  # Đóng dropdown nếu click ngoài
                    else:
                        # Nếu click trong dropdown mà không chọn option thì không làm gì
                        continue

                # Puzzle grid click (chỉ khi không solve)
                if (not is_solving and PUZZLE_OFFSET_X <= mx < PUZZLE_OFFSET_X + PUZZLE_SIZE and
                    PUZZLE_OFFSET_Y <= my < PUZZLE_OFFSET_Y + PUZZLE_SIZE and
                    not puzzle.in_reset and not puzzle.in_fade):
                    gr, gc = pixel_to_grid(mx, my)
                    if gr is not None:
                        puzzle.start_move(gr, gc)
                        continue

                # Checkbox click (luôn cho phép)
                if checkbox.is_clicked(mx, my):
                    puzzle.toggle_numbers()
                    continue

                # Buttons click
                if solve_btn.is_clicked(mx, my):
                    if not is_solving:
                        is_solving = True
                        solve_btn.label = "Stop"
                        solve_btn.color_override = (237,85,85)  # Đỏ
                        puzzle.solve()  # Giả sử puzzle.solve() sẽ bắt đầu giải
                    else:
                        is_solving = False
                        solve_btn.label = "Solve"
                        solve_btn.color_override = None
                        if hasattr(puzzle, 'stop_solve'):
                            puzzle.stop_solve()  # Nếu có hàm dừng giải
                    continue
                if next_btn.is_clicked(mx, my) and not is_solving:
                    continue
                if reset_btn.is_clicked(mx, my) and not is_solving:
                    puzzle.shuffle()
                    continue

                # Thumbnail click (chỉ khi không solve)
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
                            break

        # Update state
        puzzle.update()

        # Draw scene
        puzzle.draw_background()
        puzzle.draw_puzzle()

        # Draw UI controls
        mx, my = pygame.mouse.get_pos()
        disable_hover = False
        if combo.is_open:
            dropdown_rect = combo.header_rect.copy()
            dropdown_rect.height += combo.header_rect.height * (len(combo.options))
            if dropdown_rect.collidepoint(mx, my):
                disable_hover = True
        # Tween màu solve_btn
        solve_btn_base = (60, 60, 60)
        solve_btn_red = (234, 69, 69)
        if is_solving:
            solve_btn_color_progress = min(1.0, solve_btn_color_progress + SOLVE_BTN_TWEEN_SPEED)
        else:
            solve_btn_color_progress = max(0.0, solve_btn_color_progress - SOLVE_BTN_TWEEN_SPEED)
        tween_color = tuple(
            int(solve_btn_base[i] + (solve_btn_red[i] - solve_btn_base[i]) * solve_btn_color_progress)
            for i in range(3)
        )
        # Draw border around button group
        BUTTON_GROUP_PADDING = 10
        group_left = solve_btn.rect.x - BUTTON_GROUP_PADDING
        group_top = solve_btn.rect.y - BUTTON_GROUP_PADDING
        group_width = solve_btn.rect.width + 2 * BUTTON_GROUP_PADDING
        group_height = (reset_btn.rect.bottom - solve_btn.rect.y) + 2 * BUTTON_GROUP_PADDING
        pygame.draw.rect(screen, (120, 120, 120), (group_left, group_top, group_width, group_height), 2)
        # Vẽ solve_btn với tween màu đỏ
        solve_btn.draw(screen, disabled_hover=disable_hover, disabled=False, color_override=tween_color)
        # Next/Reset không đổi màu khi disable, chỉ không bấm được
        next_btn.draw(screen, disabled_hover=disable_hover)
        reset_btn.draw(screen, disabled_hover=disable_hover)
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

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()