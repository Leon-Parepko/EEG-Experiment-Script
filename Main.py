import json
import Blocks
import pygame
from screeninfo import get_monitors
import tkinter as tk
import time


class Main:
    """
    The main class.
    """

    def __init__(self):
        """
        The constructor.
        """
        self.screen_resolution = [0, 0]
        self.background_col = [60, 60, 60]              # R.G.B.
        self.experiment_sequence = []
        self.experiment_prerender = []

    def preprocess_experiment(self):
        """
        This function preprocesses the
        experiment_sequence array and creates
        a prerendered version of it.
        """
        # ctypes.windll.user32.SetProcessDPIAware() # use only for low quality displays
        pygame.init()
        root = tk.Tk()
        root.attributes("-fullscreen", True)

        # Get screen resolution in pixels
        self.screen_resolution = [root.winfo_screenwidth(), root.winfo_screenheight()]

        # Creates a fake window with the screen resolution and gets the dpi
        root.destroy()
        monitors = get_monitors()
        dpi = monitors[0].width / monitors[0].width_mm
        screen_width_cm = self.screen_resolution[0] / dpi
        mm_to_pixel = self.screen_resolution[1] / screen_width_cm

        # Preprocess the experiment sequence
        for elem in self.experiment_sequence:
            if elem.type_of_block == "pattern":
                image = elem.generate_block_picture(self.screen_resolution[0], self.screen_resolution[1], mm_to_pixel)
                image_surface = pygame.surfarray.make_surface(image)
                self.experiment_prerender.append((image_surface, elem.duration_in_sec))

            elif elem.type_of_block == "rest":
                image = elem.generate_block_picture(self.screen_resolution[0], self.screen_resolution[1])
                image_surface = pygame.surfarray.make_surface(image)
                self.experiment_prerender.append((image_surface, elem.duration_in_sec))

            elif elem.type_of_block == "execution":
                image = elem.generate_block_picture(self.screen_resolution[0], self.screen_resolution[1], mm_to_pixel)
                image_surface = pygame.surfarray.make_surface(image)
                self.experiment_prerender.append((image_surface, elem.duration_in_sec))

            elif elem.type_of_block == "command":
                image = elem.generate_block_picture(self.screen_resolution[0], self.screen_resolution[1], mm_to_pixel)
                image_surface = pygame.surfarray.make_surface(image)
                self.experiment_prerender.append((image_surface, elem.duration_in_sec))


    def execute_experiment(self):
        """
        Simply executes the experiment
        by showing the prerendered images.
        """
        # Initialize pygame
        screen = pygame.display.set_mode((self.screen_resolution[0], self.screen_resolution[1]), pygame.FULLSCREEN)

        # Seqentialy how the prerendered images
        for elem in self.experiment_prerender:
            screen.blit(elem[0], (0, 0))
            pygame.display.flip()
            time.sleep(elem[1])
        pygame.quit()


    def parse_json(self, json_file_path):
        """
        This function parses the json file into the array of Blocks.
        """

        # Read the json file
        with open(json_file_path, "r") as file:
            json_data = file.read()
        data = json.loads(json_data)
        result = [{"Block_{}".format(key.split("_")[1]): value} for key, value in data.items()]

        # Iterate through the json file and create the array of Blocks
        for block_dict in result:
            block_name = next(iter(block_dict))
            block_type = block_dict[block_name]["type"]
            if block_type == "pattern":
                size_in_mm = block_dict[block_name]["content"]["img_resolution"][0]
                duration_in_sec = block_dict[block_name]["content"]["duration"]
                if block_dict[block_name]["content"]["type"] == "random":
                    grid_size = 6
                    seed = (block_dict[block_name]["content"]["seed"]) % 2 ** 32
                    self.experiment_sequence.append(
                        Blocks.RandomPatternBlock(size_in_mm, duration_in_sec, grid_size, block_type, seed))
                else:
                    pattern_id = (block_dict[block_name]["content"]["pattern_id"])
                    self.experiment_sequence.append(
                        Blocks.PatternBlock(size_in_mm, duration_in_sec, block_type, pattern_id))
            elif block_type == "rest":
                duration_in_sec = block_dict[block_name]["content"]["duration"]
                noise_resolution = block_dict[block_name]["content"]["noise_resolution"]
                seed = (block_dict[block_name]["content"]["seed"]) % 2 ** 32
                self.experiment_sequence.append(
                    Blocks.RestGaussian(block_type, duration_in_sec, noise_resolution, seed_value=seed))

            elif block_type == "execution":
                duration_in_sec = block_dict[block_name]["content"]["duration"]
                diam_in_mm = block_dict[block_name]["content"]["fixation_poit_diam"]
                self.experiment_sequence.append(Blocks.Execution(block_type, diam_in_mm, duration_in_sec))

            elif block_type == "command":
                duration_in_sec = block_dict[block_name]["content"]["duration"]
                diam_in_mm = block_dict[block_name]["content"]["fixation_poit_diam"]
                height_in_mm = block_dict[block_name]["content"]["img_resolution"][0]
                position = block_dict[block_name]["content"]["state"]
                self.experiment_sequence.append(
                    Blocks.Command(block_type, duration_in_sec, height_in_mm, position, diam_in_mm))



