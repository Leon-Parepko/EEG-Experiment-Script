import numpy as np
import cv2


class Block:
    def generate_block_picture(self, *args, **kwargs):
        pass


class PatternBlock(Block):
    map_of_pattern = [[0, 0, 0, 0, 0, 0], [0, 1, 1, 1, 1, 0], [0, 1, 0, 0, 1, 0], [0, 1, 0, 0, 1, 0],
                      [0, 1, 1, 1, 1, 0],
                      [0, 0, 0, 0, 0, 0]]
    reversed_map = [[1 if element == 0 else 0 for element in row] for row in map_of_pattern]
    map_of_pattern = np.array(reversed_map)
    array_of_patterns = [map_of_pattern]

    def __init__(self, size_in_mm, duration_in_sec, type_of_block, pattern_id):
        self.size_in_mm = size_in_mm
        self.duration_in_sec = duration_in_sec
        self.type_of_block = type_of_block
        self.map_of_pattern = self.array_of_patterns[pattern_id % len(self.array_of_patterns)]

    def generate_block_picture(self, screen_width, screen_height, mm_to_pixel):
        image = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)
        image[:, :] = (60, 60, 60)
        grid_size = len(self.map_of_pattern)
        size_pixel = int(self.size_in_mm * mm_to_pixel)
        grid_square_size_pixel = size_pixel // grid_size
        inner_square_top_left_x = (screen_width // 2) - (size_pixel // 2)
        inner_square_top_left_y = (screen_height // 2) - (size_pixel // 2)
        for i in range(grid_size):
            for j in range(grid_size):
                square_top_left_x = inner_square_top_left_x + (j * grid_square_size_pixel)
                square_top_left_y = inner_square_top_left_y + (i * grid_square_size_pixel)
                color = (
                    255 * int(self.map_of_pattern[i, j]), 255 * int(self.map_of_pattern[i, j]),
                    255 * int(self.map_of_pattern[i, j]))
                cv2.rectangle(image, (square_top_left_x, square_top_left_y),
                              (square_top_left_x + grid_square_size_pixel, square_top_left_y + grid_square_size_pixel),
                              color, -1)
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image


class RandomPatternBlock(Block):
    def __init__(self, size_in_mm, duration_in_sec, grid_size, type_of_block, seed=None):
        self.size_in_mm = size_in_mm
        self.duration_in_sec = duration_in_sec
        self.grid_size = grid_size
        self.type_of_block = type_of_block
        np.random.seed(seed)
        self.map_of_pattern = np.random.randint(0, 2, size=(self.grid_size, self.grid_size))

    def generate_block_picture(self, screen_width, screen_height, mm_to_pixel):
        image = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)
        image[:, :] = (60, 60, 60)
        grid_size = len(self.map_of_pattern)
        size_pixel = int(self.size_in_mm * mm_to_pixel)
        grid_square_size_pixel = size_pixel // grid_size
        inner_square_top_left_x = (screen_width // 2) - (size_pixel // 2)
        inner_square_top_left_y = (screen_height // 2) - (size_pixel // 2)
        for i in range(grid_size):
            for j in range(grid_size):
                square_top_left_x = inner_square_top_left_x + (j * grid_square_size_pixel)
                square_top_left_y = inner_square_top_left_y + (i * grid_square_size_pixel)
                color = (
                    255 * int(self.map_of_pattern[i, j]), 255 * int(self.map_of_pattern[i, j]),
                    255 * int(self.map_of_pattern[i, j]))
                cv2.rectangle(image, (square_top_left_x, square_top_left_y),
                              (square_top_left_x + grid_square_size_pixel, square_top_left_y + grid_square_size_pixel),
                              color, -1)
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image


class RestGaussian(Block):
    def __init__(self, type_of_block, duration_in_sec, cell_size=2, blur_value=7, seed_value=None):
        self.duration_in_sec = duration_in_sec
        self.type_of_block = type_of_block
        self.blur_value = blur_value
        self.cell_size = cell_size
        self.seed_value = seed_value

    def generate_block_picture(self, screen_width, screen_height):
        np.random.seed(self.seed_value)
        cv2.setRNGSeed(self.seed_value)
        grid_width = screen_width // self.cell_size
        grid_height = screen_height // self.cell_size
        cell_pixels = np.random.choice([0, 255], size=(grid_height, grid_width), p=[0.5, 0.5])
        image = np.zeros((screen_height, screen_width), dtype=np.uint8)
        for i in range(grid_height):
            for j in range(grid_width):
                cell_value = cell_pixels[i, j]
                image[i * self.cell_size: (i + 1) * self.cell_size,
                j * self.cell_size: (j + 1) * self.cell_size] = cell_value
        blurred_image = cv2.GaussianBlur(image, (self.blur_value, self.blur_value), 0)
        image = cv2.rotate(blurred_image, cv2.ROTATE_90_CLOCKWISE)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image
