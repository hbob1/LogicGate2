import pygame
from config import COMP_WIDTH, COMP_HEIGHT, COMP_COLOR, COMP_COLOR_OUTLINE
from move_draw_grid import grid, draw_grid

components = []

def add_component(surface, pos):
    x, y = pos
    world_x = x + grid["offset_x"]
    world_y = y + grid["offset_y"]

    font = pygame.font.SysFont(None, 24)
    name = ""
    input_active = True
    rect = pygame.Rect(x - COMP_WIDTH // 2, y - COMP_HEIGHT // 2, COMP_WIDTH, COMP_HEIGHT)

    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 16:
                        name += event.unicode

        surface.fill((90, 90, 90))
        draw_grid(surface)
        draw_components(surface)
        pygame.draw.rect(surface, COMP_COLOR, rect)
        pygame.draw.rect(surface, COMP_COLOR_OUTLINE, rect, 1)
        text_surface = font.render(name + "|", True, (0, 0, 0))
        surface.blit(text_surface, (rect.x + 5, rect.y + 5))
        pygame.display.flip()
        pygame.time.Clock().tick(30)

    components.append({"pos": (world_x, world_y), "name": name})

def draw_components(surface):
    font = pygame.font.SysFont(None, 24)
    for comp in components:
        world_x, world_y = comp["pos"]
        name = comp["name"]
        screen_x = world_x - grid["offset_x"]
        screen_y = world_y - grid["offset_y"]
        rect = pygame.Rect(screen_x - COMP_WIDTH // 2, screen_y - COMP_HEIGHT // 2, COMP_WIDTH, COMP_HEIGHT)
        pygame.draw.rect(surface, COMP_COLOR, rect)
        pygame.draw.rect(surface, COMP_COLOR_OUTLINE, rect, 1)
        text_surface = font.render(name, True, (0, 0, 0))
        surface.blit(text_surface, (rect.x + 5, rect.y + 5))