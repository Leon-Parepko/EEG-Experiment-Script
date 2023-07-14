import numpy as np
import pygame
from screeninfo import get_monitors
import tkinter as tk
import time
import geom_pattern

pygame.init()
root = tk.Tk()
root.attributes("-fullscreen", True)
screen_info = pygame.display.Info()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.destroy()
monitors = get_monitors()
dpi = monitors[0].width / monitors[0].width_mm
screen_width_cm = screen_width / dpi
cm_to_pixel = screen_width / screen_width_cm
map_of_pattern = [[0, 0, 0, 0, 0, 0], [0, 1, 1, 1, 1, 0], [0, 1, 0, 0, 1, 0], [0, 1, 0, 0, 1, 0], [0, 1, 1, 1, 1, 0],
                  [0, 0, 0, 0, 0, 0]]
reversed_map = [[1 if element == 0 else 0 for element in row] for row in map_of_pattern]
np_map_of_pattern = np.array(reversed_map)
image = geom_pattern.draw_pattern(60, screen_width, screen_height, cm_to_pixel, np_map_of_pattern)
image_surface = pygame.surfarray.make_surface(image)
image0 = geom_pattern.draw_rand_pattern(60, screen_width, screen_height, cm_to_pixel, 6, 123)
image_surface0 = pygame.surfarray.make_surface(image0)
image1 = geom_pattern.draw_rand_pattern(60, screen_width, screen_height, cm_to_pixel, 6)
image_surface1 = pygame.surfarray.make_surface(image1)
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
experiment = [(image_surface0, 2), (image_surface, 2), (image_surface1, 5)]

for elem in experiment:
    screen.blit(elem[0], (0, 0))
    pygame.display.flip()
    time.sleep(elem[1])

pygame.quit()
