import pygame
pygame.init()

screen = pygame.display.set_mode((400, 400))
pygame.display.set_caption("8-Puzzle")

icon = pygame.image.load("assets/icon_32.png")
pygame.display.set_icon(icon)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))
    pygame.display.flip()

pygame.quit()
