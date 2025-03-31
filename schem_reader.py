import sys

import nbtlib
import pygame as pygame
from colors import BlOCK_COLORS_FROM_NAMES, BlOCK_COLORS
import re

from names import BLOCK_NAMES

RULER_SIZE = 40
BLOCK_SIZE = 5


def load_schem(file_path):
    # Load the schematic data as nbt
    nbt_data = nbtlib.load(file_path)

    # try to get Schematic from the data, for certain .schem versions
    try:
        nbt_data = nbt_data['Schematic']
    except KeyError:
        print("This file is not weird!")

    width = nbt_data['Width']
    height = nbt_data['Height']
    length = nbt_data['Length']

    if '.schematic' in file_path:
        blocks = list(nbt_data['Blocks'])
    else:
        version = nbt_data['Version']
        if version == 2:
            block_data = nbt_data['BlockData']
            palette = nbt_data['Palette']

        if version == 3:
            blocks = nbt_data['Blocks']     # Palette and Data are in Blocks
            palette = blocks['Palette']
            block_data = blocks['Data']

        palette_map = {v.real: k for k, v in palette.items()}
        block_data_decoded = byte_to_int(block_data)
        blocks = [palette_map[idx] for idx in block_data_decoded]

    return width, height, length, blocks


def draw_layer(screen, blocks, width, length, layer, font, block_id=None, pos=None, is_old=False):
    screen.fill((255, 255, 255))

    for x in range(width):
        for z in range(length):
            index = layer * width * length + z * width + x
            if 0 <= index < len(blocks):
                block = blocks[index]

                if is_old:
                    color = BlOCK_COLORS.get(block, (50, 50, 50))
                else:
                    stupid, block_name = block.split(':')
                    if '[' in block_name:
                        block_name, stupid = block_name.split('[')
                    color = BlOCK_COLORS_FROM_NAMES.get(block_name, (50, 50, 50))

                pygame.draw.rect(screen, color, (x * BLOCK_SIZE, z * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

    draw_grid(screen, width, length)
    draw_ruler(screen, length, width)

    text_position = 20

    # Draw layer number
    if layer is not None:
        layer_text = font.render(f'Layer #{layer}', True, (30, 30, 30))
        screen.blit(layer_text, (BLOCK_SIZE, text_position))
        text_position += 20

    # draw the name and parameters of the block under the cursor, and highlights the block
    if block_id is not None:
        if is_old:
            block_name = BLOCK_NAMES.get(block_id)
        else:
            block_name, block_vars = get_block_name(block_id)

        text_surface = font.render(f'Block: {block_name}', True, (30, 30, 30))
        screen.blit(text_surface, (BLOCK_SIZE, text_position))
        text_position += 20

        if not is_old:
            for key, state in block_vars.items():
                key_state_surface = font.render(f'{key}: {state}', True, (30, 30, 30))
                screen.blit(key_state_surface, (BLOCK_SIZE, text_position))
                text_position += 20

        # makes the highligted block under cursor
        point1 = ((pos[0] // BLOCK_SIZE) * BLOCK_SIZE, (pos[1] // BLOCK_SIZE) * BLOCK_SIZE)
        point2 = (((pos[0] // BLOCK_SIZE) + 1) * BLOCK_SIZE, (pos[1] // BLOCK_SIZE) * BLOCK_SIZE)
        point3 = (((pos[0] // BLOCK_SIZE) + 1) * BLOCK_SIZE, ((pos[1] // BLOCK_SIZE) + 1) * BLOCK_SIZE)
        point4 = ((pos[0] // BLOCK_SIZE) * BLOCK_SIZE, ((pos[1] // BLOCK_SIZE) + 1) * BLOCK_SIZE)
        pygame.draw.line(screen, (255, 255, 255), point1, point2)
        pygame.draw.line(screen, (255, 255, 255), point2, point3)
        pygame.draw.line(screen, (255, 255, 255), point3, point4)
        pygame.draw.line(screen, (255, 255, 255), point4, point1)

    pygame.display.flip()


def draw_grid(screen, width, length):
    for x in range(0, (width * BLOCK_SIZE) + BLOCK_SIZE, BLOCK_SIZE):
        pygame.draw.line(screen, (100, 100, 100), (x, 0), (x, length * BLOCK_SIZE))
    for z in range(0, (length * BLOCK_SIZE) + BLOCK_SIZE, BLOCK_SIZE):
        pygame.draw.line(screen, (100, 100, 100), (0, z), (width * BLOCK_SIZE, z))


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


def get_block_name(block_id):
    pattern = r':|\[|\]'
    split = re.split(pattern, block_id)
    id_name = split[1]

    # process name
    id_name_split = id_name.split('_')
    id_name_cap = [x.capitalize() for x in id_name_split]
    name = ' '.join(id_name_cap)

    states_dict = {}
    if len(split) > 2:  # process states if they exist
        id_states = split[2]
        split_states = id_states.split(',')
        for state_str in split_states:
            var, val = state_str.split('=')
            states_dict[var] = val

    block_name = name
    return block_name, states_dict


def byte_to_int(data):
    proper_bytes = []
    prev_byte = 0
    for byte in data:
        if prev_byte < 0:
            prev_byte = 0
            continue
        if byte < 0:
            prev_byte = byte
            byte = 256 + byte
        proper_bytes.append(byte)

    return proper_bytes


def main():
    file_path = "schems/0201-house-e380.schem"
    if ".schematic" in file_path:
        is_old = True
    else:
        is_old = False

    w, h, l, bl = load_schem(file_path)

    # Negative IDs are, allegedly: ID + 256
    # s = set(bl)
    # print(s)

    pygame.init()
    screen = pygame.display.set_mode((w * BLOCK_SIZE + RULER_SIZE, l * BLOCK_SIZE + RULER_SIZE))
    pygame.display.set_caption("Schematic Viewer")

    layer = 0
    font = pygame.font.Font(None, 24)
    draw_layer(screen, bl, w, l, layer, font, is_old=is_old)

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
                draw_layer(screen, bl, w, l, layer, font, is_old=is_old)

        mouse_pos = pygame.mouse.get_pos()
        block_id = get_block_at_cursor(mouse_pos, w, l, layer, bl)
        draw_layer(screen, bl, w, l, layer, font, block_id, mouse_pos, is_old=is_old)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
