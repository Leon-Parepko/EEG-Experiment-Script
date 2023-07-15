import numpy as np
import cv2
import ast


class Block:
    """
    Abstract class for blocks.
    """
    def generate_block_picture(self, *args, **kwargs):
        pass


class PatternBlock(Block):
    """
    Block with a pattern.
    """

    # Read patterns from file
    file = open("geometric_patterns.txt", "r")
    patterns = res = ast.literal_eval(file.read())
    file.close()

    array_of_patterns = []
    for pattern in patterns:
        reversed_map = [[1 if element == 0 else 0 for element in row] for row in pattern]
        map_of_pattern = np.array(reversed_map)
        array_of_patterns.append(map_of_pattern)


    def __init__(self, size_in_mm, duration_in_sec, type_of_block, pattern_id):
        """
        Initialize the block.
        """
        self.size_in_mm = size_in_mm
        self.duration_in_sec = duration_in_sec
        self.type_of_block = type_of_block
        self.map_of_pattern = self.array_of_patterns[pattern_id % len(self.array_of_patterns)]

    def generate_block_picture(self, screen_width, screen_height, mm_to_pixel):
        """
        Generate the picture of the block.
        """
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
        np.random.seed(seed)
        self.size_in_mm = size_in_mm
        self.duration_in_sec = duration_in_sec
        self.grid_size = grid_size
        self.type_of_block = type_of_block
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



class Execution(Block):
    def __init__(self, type_of_block, diam_in_mm, duration_in_sec):
        self.type_of_block = type_of_block
        self.diam_in_mm = diam_in_mm
        self.duration_in_sec = duration_in_sec

    def generate_block_picture(self, screen_width, screen_height, mm_to_pixel):
        image = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)
        image[:, :] = (60, 60, 60)
        diameter_in_pixels = int(self.diam_in_mm * mm_to_pixel)
        center_x = screen_width // 2
        center_y = screen_height // 2
        cv2.circle(image, (center_x, center_y), diameter_in_pixels // 2, (255, 255, 255), -1)
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image


class Command(Block):
    def __init__(self, type_of_block, duration_in_sec, height_in_mm, position, diameter_in_mm):
        self.type_of_block = type_of_block
        self.duration_in_sec = duration_in_sec
        self.height_in_mm = height_in_mm
        self.position = position
        self.diameter_in_mm = diameter_in_mm

    def generate_block_picture(self, screen_width, screen_height, mm_to_pixel):
        image = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)
        image[:, :] = (60, 60, 60)
        height_in_pixels = int(self.height_in_mm * mm_to_pixel)
        side_length_in_pixels = int((height_in_pixels * 2) / np.sqrt(3))
        start_x = (screen_width - side_length_in_pixels) // 2
        start_y = (screen_height // 2) - ((2 * height_in_pixels) // 3)
        x1 = start_x
        y1 = start_y + height_in_pixels
        x2 = start_x + (side_length_in_pixels // 2)
        y2 = start_y
        x3 = start_x + side_length_in_pixels
        y3 = start_y + height_in_pixels
        diameter_in_pixels = int(self.diameter_in_mm * mm_to_pixel)
        center_x = screen_width // 2
        center_y = screen_height // 2
        if self.position == 0:
            cv2.circle(image, (center_x, center_y), diameter_in_pixels // 2, (255, 255, 255), -1)
        else:
            cv2.circle(image, (center_x, center_y), diameter_in_pixels // 2, (0, 255, 0), -1)
        mm_otstup = 5
        otstup_pixel = mm_otstup * mm_to_pixel
        kx = center_x - otstup_pixel
        ky = y1
        nx = x1 + int(((side_length_in_pixels / 2) - otstup_pixel) / 2)
        ny = y1 - int(height_in_pixels * ((side_length_in_pixels / 2) - otstup_pixel) / side_length_in_pixels)
        mx = kx
        my = y1 - int(((side_length_in_pixels / 2) - otstup_pixel) / np.sqrt(3))
        pts1 = np.array([[x1, y1], [kx, ky], [mx, my], [nx, ny]], np.int32)
        if self.position == 2:
            cv2.fillPoly(image, [pts1], (0, 255, 0))
        else:
            cv2.fillPoly(image, [pts1], (255, 255, 255))
        ax = center_x + otstup_pixel
        ay = y3
        bx = ax
        by = my
        cx = x3 - int(((side_length_in_pixels / 2) - otstup_pixel) / 2)
        cy = ny
        pts2 = np.array([[x3, y3], [ax, ay], [bx, by], [cx, cy]], np.int32)
        if self.position == 1:
            cv2.fillPoly(image, [pts2], (0, 255, 0))
        else:
            cv2.fillPoly(image, [pts2], (255, 255, 255))
        qx = x2 - int(((side_length_in_pixels / 2) - otstup_pixel) / 2)
        qy = y2 + int(height_in_pixels * ((side_length_in_pixels / 2) - otstup_pixel) / side_length_in_pixels)
        wx = center_x
        wy = y2 + int((side_length_in_pixels - otstup_pixel * 2) / np.sqrt(3))
        ex = x2 + int(((side_length_in_pixels / 2) - otstup_pixel) / 2)
        ey = qy
        pts3 = np.array([[x2, y2], [qx, qy], [wx, wy], [ex, ey]], np.int32)
        if self.position == 3:
            cv2.fillPoly(image, [pts3], (0, 255, 0))
        else:
            cv2.fillPoly(image, [pts3], (255, 255, 255))
        image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image
