import pygame
import random

# Khởi tạo Pygame
pygame.init()
WIDTH, HEIGHT = 300, 300
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("8 Puzzle Test UI")
FONT = pygame.font.SysFont(None, 60)

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TILE_COLOR = (173, 216, 230)
TILE_SIZE = WIDTH // 3

# Tạo trạng thái shuffle của board
def generate_puzzle():
    tiles = list(range(1, 9)) + [0]
    while True:
        random.shuffle(tiles)
        if is_solvable(tiles):
            return [tiles[i:i+3] for i in range(0, 9, 3)]

# Kiểm tra trạng thái có thể giải được không
def is_solvable(tiles):
    inv_count = sum(
        1 for i in range(8) for j in range(i+1, 9)
        if tiles[j] and tiles[i] and tiles[i] > tiles[j]
    )
    return inv_count % 2 == 0

# Vẽ board
def draw_board(board):
    SCREEN.fill(WHITE)
    for row in range(3):
        for col in range(3):
            tile = board[row][col]
            rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(SCREEN, TILE_COLOR if tile != 0 else WHITE, rect)
            pygame.draw.rect(SCREEN, BLACK, rect, 2)
            if tile != 0:
                text = FONT.render(str(tile), True, BLACK)
                text_rect = text.get_rect(center=rect.center)
                SCREEN.blit(text, text_rect)

# Tìm ô trống (0)
def find_blank(board):
    for r in range(3):
        for c in range(3):
            if board[r][c] == 0:
                return r, c

# Thử di chuyển
def move_tile(board, row, col):
    blank_r, blank_c = find_blank(board)
    if abs(blank_r - row) + abs(blank_c - col) == 1:
        board[blank_r][blank_c], board[row][col] = board[row][col], board[blank_r][blank_c]

# Hàm main
def main():
    board = generate_puzzle()
    running = True
    while running:
        draw_board(board)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                row, col = y // TILE_SIZE, x // TILE_SIZE
                move_tile(board, row, col)

    pygame.quit()

if __name__ == "__main__":
    main()
