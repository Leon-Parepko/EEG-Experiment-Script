import numpy as np
import cv2


def draw_pattern(size_in_mm, screen_width, screen_height, mm_to_pixel, map_of_pattern):
    """
       Generates image based on input parameters

       Parameters:
       - size_in_mm (int): Size of grid in mm
       - screen_width (int): Screen width in mm
       - screen_height (int): Screen height in mm
       - mm_to_pixel (float): Conversion rate from pixel to mm
       - map_of_pattern (numpy.ndarray): Numpy array specifying the image

       Returns:
       - numpy.ndarray: image, specified with map_of_pattern

       Note:
       - Numpy array must contain only square matrices and contain only 0's and 1's
       - In map_of_pattern 1 specifies black square, 0 specifies white square
       """
    image = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)
    image[:, :] = (60, 60, 60)
    grid_size = len(map_of_pattern)
    size_pixel = int(size_in_mm * mm_to_pixel)
    grid_square_size_pixel = size_pixel // grid_size
    inner_square_top_left_x = (screen_width // 2) - (size_pixel // 2)
    inner_square_top_left_y = (screen_height // 2) - (size_pixel // 2)
    for i in range(grid_size):
        for j in range(grid_size):
            square_top_left_x = inner_square_top_left_x + (j * grid_square_size_pixel)
            square_top_left_y = inner_square_top_left_y + (i * grid_square_size_pixel)
            color = (255 * int(map_of_pattern[i, j]), 255 * int(map_of_pattern[i, j]), 255 * int(map_of_pattern[i, j]))
            cv2.rectangle(image, (square_top_left_x, square_top_left_y),
                          (square_top_left_x + grid_square_size_pixel, square_top_left_y + grid_square_size_pixel),
                          color, -1)
    image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image


def draw_rand_pattern(size_in_mm, screen_width, screen_height, mm_to_pixel, grid_size, seed_value=None):
    """
           Creates a random map_of_pattern given the grid_size and seed. After that passes to draw_pattern to generate
           image.

           Parameters:
           - size_in_mm (int): Size of grid in mm
           - screen_width (int): Screen width in mm
           - screen_height (int): Screen height in mm
           - mm_to_pixel (float): Conversion rate from pixel to mm
           - grid_size (int): Amount of squares in one row
           - seed_value (int): Seed for random
           Returns:
           - numpy.ndarray: image, specified with map_of_pattern
        """
    np.random.seed(seed_value)
    random_array = np.random.randint(0, 2, size=(grid_size, grid_size))
    return draw_pattern(size_in_mm, screen_width, screen_height, mm_to_pixel, random_array)