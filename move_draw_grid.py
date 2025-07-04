import pygame
from config import WIDTH, HEIGHT

grid = {
    "offset_x": 0,
    "offset_y": 0,
    "cell_size" : 20
}

def draw_grid(surface):
    color = (120, 120, 120)
    ox, oy = grid["offset_x"], grid["offset_y"]
    cell_size = grid["cell_size"]

    for x in range(-ox % cell_size, WIDTH, cell_size):
        pygame.draw.line(surface, color, (x, 0), (x, HEIGHT))

    for y in range(-oy % cell_size, HEIGHT, cell_size):
        pygame.draw.line(surface, color, (0, y), (WIDTH, y))