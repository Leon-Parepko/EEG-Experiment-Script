import pygame
from screeninfo import get_monitors
import tkinter as tk
import time
import ctypes


def execute_experiment_sequence(experiment_sequence):
    # ctypes.windll.user32.SetProcessDPIAware() # use only for low quality displays
    pygame.init()
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    # screen_info = pygame.display.Info()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.destroy()
    monitors = get_monitors()
    dpi = monitors[0].width / monitors[0].width_mm
    screen_width_cm = screen_width / dpi
    mm_to_pixel = screen_width / screen_width_cm
    experiment_sequence_prerender = []
    for elem in experiment_sequence:
        if elem.type_of_block == "pattern":
            image = elem.generate_block_picture(screen_width, screen_height, mm_to_pixel)
            image_surface = pygame.surfarray.make_surface(image)
            experiment_sequence_prerender.append((image_surface, elem.duration_in_sec))
        elif elem.type_of_block == "rest":
            image = elem.generate_block_picture(screen_width, screen_height)
            image_surface = pygame.surfarray.make_surface(image)
            experiment_sequence_prerender.append((image_surface, elem.duration_in_sec))
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    print(experiment_sequence_prerender)
    for elem in experiment_sequence_prerender:
        screen.blit(elem[0], (0, 0))
        pygame.display.flip()
        time.sleep(elem[1])
    pygame.quit()
