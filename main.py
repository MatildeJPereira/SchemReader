import sys

import nbtlib
import pygame as pygame
from colors import BlOCK_COLORS
from names import BLOCK_NAMES

RULER_SIZE = 40
BLOCK_SIZE = 6


def load_schematic(file_path):
    data = nbtlib.load(file_path)
    width = data['Width'].real
    height = data['Height'].real
    length = data['Length'].real
    blocks = list(data['Blocks'])
    return width, height, length, blocks


def load_schem(file_path):
    nbt_data = nbtlib.load(file_path)
    width = nbt_data['Size'][0].real
    height = nbt_data['Size'][1].real
    length = nbt_data['Size'][2].real

    palette = nbt_data['Palette']
    block_data = list(nbt_data['BlockData'])

    # Convert palette indices to block names
    palette_map = {v.real: k for k, v in palette.items()}
    blocks = [palette_map[idx] for idx in block_data]

    return width, height, length, blocks


def draw_layer(screen, blocks, width, length, layer, font, block_id=None, pos=None):
    screen.fill((255, 255, 255))

    for x in range(width):
        for z in range(length):
            index = layer * width * length + z * width + x
            if 0 <= index < len(blocks):
                block = blocks[index]
                color = BlOCK_COLORS.get(block, (50, 50, 50))
                pygame.draw.rect(screen, color, (x * BLOCK_SIZE, z * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

    for x in range(0, (width * BLOCK_SIZE) + BLOCK_SIZE, BLOCK_SIZE):
        pygame.draw.line(screen, (100, 100, 100), (x, 0), (x, length * BLOCK_SIZE))
    for z in range(0, (length * BLOCK_SIZE) + BLOCK_SIZE, BLOCK_SIZE):
        pygame.draw.line(screen, (100, 100, 100), (0, z), (width * BLOCK_SIZE, z))

    draw_ruler(screen, length, width)

    if block_id is not None:
        block_name = BLOCK_NAMES.get(block_id)
        text_surface = font.render(f'Block: {block_name}', True, (30, 30, 30))
        screen.blit(text_surface, (BLOCK_SIZE, 4 * BLOCK_SIZE))

        point1 = ((pos[0] // BLOCK_SIZE) * BLOCK_SIZE, (pos[1] // BLOCK_SIZE) * BLOCK_SIZE)
        point2 = (((pos[0] // BLOCK_SIZE) + 1) * BLOCK_SIZE, (pos[1] // BLOCK_SIZE) * BLOCK_SIZE)
        point3 = (((pos[0] // BLOCK_SIZE) + 1) * BLOCK_SIZE, ((pos[1] // BLOCK_SIZE) + 1) * BLOCK_SIZE)
        point4 = ((pos[0] // BLOCK_SIZE) * BLOCK_SIZE, ((pos[1] // BLOCK_SIZE) + 1) * BLOCK_SIZE)
        pygame.draw.line(screen, (255, 255, 255), point1, point2)
        pygame.draw.line(screen, (255, 255, 255), point2, point3)
        pygame.draw.line(screen, (255, 255, 255), point3, point4)
        pygame.draw.line(screen, (255, 255, 255), point4, point1)

    if layer is not None:
        layer_text = font.render(f'Layer #{layer}', True, (30, 30, 30))
        screen.blit(layer_text, (BLOCK_SIZE, BLOCK_SIZE))

    pygame.display.flip()


def draw_ruler(screen, length, width):
    font2 = pygame.font.Font(None, 15)
    total_length = length * BLOCK_SIZE
    total_width = width * BLOCK_SIZE

    pygame.draw.line(screen, (100, 100, 100),
                     (0, total_length + (RULER_SIZE / 3)),
                     (total_width, total_length + (RULER_SIZE / 3)))
    pygame.draw.line(screen, (100, 100, 100),
                     (total_width + (RULER_SIZE / 3), 0),
                     (total_width + (RULER_SIZE / 3), total_length))

    for x in range(0, total_width, BLOCK_SIZE * 5):
        pygame.draw.line(screen, (100, 100, 100),
                         (x, total_length + (RULER_SIZE / 3)),
                         (x, total_length + (RULER_SIZE / 3) + 5))
        pygame.draw.line(screen, (100, 100, 100), (x, 0), (x, length * BLOCK_SIZE), 2)

        nums_txt = font2.render(f'{x // BLOCK_SIZE}', True, (30, 30, 30))
        screen.blit(nums_txt, (x - 2.5, total_length + (RULER_SIZE / 3) + 10))

    for z in range(0, total_length, BLOCK_SIZE*5):
        pygame.draw.line(screen, (100, 100, 100),
                         (total_width + (RULER_SIZE / 3), z),
                         (total_width + (RULER_SIZE / 3) + 5, z))
        pygame.draw.line(screen, (100, 100, 100), (0, z), (width * BLOCK_SIZE, z), 2)

        nums_txt = font2.render(f'{z // BLOCK_SIZE}', True, (30, 30, 30))
        screen.blit(nums_txt, ((total_width + (RULER_SIZE / 3) + 10), z - 5))


def get_block_at_cursor(pos, width, length, layer, blocks):
    x, z = pos[0] // BLOCK_SIZE, pos[1] // BLOCK_SIZE
    if 0 <= x < width and 0 <= z < length:
        index = layer * width * length + z * width + x
        if 0 <= index < len(blocks):
            return blocks[index]
    return None


def main():
    file_path = "schems/3177.schematic"
    w, h, l, bl = load_schematic(file_path)

    # Negative IDs are, allegedly: ID + 256
    s = set(bl)
    print(s)

    pygame.init()
    screen = pygame.display.set_mode((w * BLOCK_SIZE + RULER_SIZE, l * BLOCK_SIZE + RULER_SIZE))
    pygame.display.set_caption("Schematic Viewer")

    layer = 0
    font = pygame.font.Font(None, 24)
    draw_layer(screen, bl, w, l, layer, font)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and layer < h-1:
                    layer += 1
                elif event.key == pygame.K_DOWN and layer > 0:
                    layer -= 1
                draw_layer(screen, bl, w, l, layer, font)

        mouse_pos = pygame.mouse.get_pos()
        block_id = get_block_at_cursor(mouse_pos, w, l, layer, bl)
        draw_layer(screen, bl, w, l, layer, font, block_id, mouse_pos)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
