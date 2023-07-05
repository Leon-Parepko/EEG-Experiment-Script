import numpy as np
import pygame
from Images import ImageGenerator as ImGen
from Blocks import BlockFabric as BlcFab


class Main:
    """
    The main class.
    """

    def __init__(self, screen_size, screen_resolution, file_path):
        self.file_path = file_path
        self.screen_size = screen_size                  # In mm.
        self.screen_resolution = screen_resolution      # In px.
        self.background_col = [60, 60, 60]              # R.G.B.

        # Generating content
        self.time_sequence = self.__parse_json()
        self.block_arr = self.__generate_block_array()
        self.experiment = self.__generate_experiment()

    def execute_experiment(self):
        pass

    def __parse_json(self):
        pass

    def __generate_block_array(self):
        pass

    def __generate_experiment(self):
        pass




