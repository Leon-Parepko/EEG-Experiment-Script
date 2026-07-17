import json
import Blocks
import pygame
from screeninfo import get_monitors
import tkinter as tk
import time
import pylink
from psychopy import visual, core, event
import tqdm
import RDA_threaded as RDA


class Main:
    """
    The main class.
    """

    def __init__(self):
        """
        The constructor.
        """
        self.screen_resolution = [0, 0]
        self.experiment_sequence = []
        self.experiment_prerender = []

    def preprocess_experiment(self):
        """
        This function preprocesses the
        experiment_sequence array and creates
        a prerendered version of it.
        """
        # ctypes.windll.user32.SetProcessDPIAware() # use only for low quality displays
        root = tk.Tk()
        root.attributes("-fullscreen", True)

        # Get screen resolution in pixels
        self.screen_resolution = [root.winfo_screenwidth(), root.winfo_screenheight()]
        root.destroy()
        # Creates a fake window with the screen resolution and gets the dpi
        monitors = get_monitors()
        if monitors[0].width and monitors[0].width_mm:
            dpi = monitors[0].width / monitors[0].width_mm
            screen_width_cm = self.screen_resolution[0] / dpi
            mm_to_pixel = self.screen_resolution[0] / screen_width_cm   # Hotfix screen_resolution id for width is 0 (not 1)
        else:
            monitors[0].width_mm = 369
            dpi = monitors[0].width / monitors[0].width_mm
            screen_width_cm = self.screen_resolution[0] / dpi / 1920 * 1080
            mm_to_pixel = self.screen_resolution[0] / screen_width_cm   # Hotfix screen_resolution id for width is 0 (not 1)

        print(self.screen_resolution, monitors[0], mm_to_pixel)
        # Preprocess the experiment sequence
        for elem in self.experiment_sequence:
            if elem.type_of_block == "pattern":
                image = elem.generate_block_picture(self.screen_resolution[0], self.screen_resolution[1], mm_to_pixel)
                self.experiment_prerender.append((image, elem.duration_in_sec))

            elif elem.type_of_block == "rest":
                image = elem.generate_block_picture(self.screen_resolution[0], self.screen_resolution[1])
                self.experiment_prerender.append((image, elem.duration_in_sec))

            elif elem.type_of_block == "execution":
                image = elem.generate_block_picture(self.screen_resolution[0], self.screen_resolution[1], mm_to_pixel)
                self.experiment_prerender.append((image, elem.duration_in_sec))

            elif elem.type_of_block == "command":
                image = elem.generate_block_picture(self.screen_resolution[0], self.screen_resolution[1], mm_to_pixel)
                self.experiment_prerender.append((image, elem.duration_in_sec))

            elif elem.type_of_block == "custom":
                image = elem.generate_block_picture(self.screen_resolution[0], self.screen_resolution[1], mm_to_pixel)
                self.experiment_prerender.append((image, elem.duration_in_sec))

    def eyelink_connect(self):
        self.eyelink = pylink.EyeLink('100.1.1.1')

        # Open the connection to the EyeLink eye tracker
        # self.eyelink.open()

        # Set the EyeLink host PC IP address (default is '100.1.1.1')
        # self.eyelink.setAddress('100.1.1.1')

        # Set the data file name
        self.eyelink.setFileEventFilter("LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON")
        self.eyelink.setFileSampleFilter("LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS,HTARGET")

        # Set the link data (used for real-time data transfer)
        self.eyelink.setLinkEventFilter("LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON")
        self.eyelink.setLinkSampleFilter("LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,HTARGET")
    
    def eyelink_calibrate(self):
        pylink.openGraphics()
        self.eyelink.doTrackerSetup()
        pylink.closeGraphics()
        
    def eyelink_close(self):
                # Stop recording
        self.eyelink.stopRecording()

        # Close the EDF file and transfer it to the host PC
        self.eyelink.closeDataFile()
        self.eyelink.receiveDataFile(self.edf_file, self.edf_file)

        # Close the connection to the EyeLink eye tracker
        self.eyelink.close()

    def execute_experiment(self, testing, edffilename=False):
        self.edf_file = edffilename
        """
        Simply executes the experiment
        by showing the prerendered images.
        """
        # Initialize pygame
        print('connection...')
        if testing != 'Test':
            self.eyelink_connect()
        win = visual.Window(self.screen_resolution, fullscr=False, color=(1, 1, 1))
        print('calibration...')
        if testing != 'Test':
            self.eyelink_calibrate()
            self.eyelink.openDataFile(self.edf_file)

        print('start recording...')
        # Start recording
        if testing != 'Test':
            self.eyelink.startRecording(1, 1, 1, 1)
        print('start experiment...')
        # Seqentialy show the prerendered images
        # TODO: Add ip variable here, add timestamp
        rda = RDA.run_rda_thread()

        for elem in tqdm.tqdm(self.experiment_prerender):
            img = visual.ImageStim(win, image=elem[0]/256, size=2)
            img.draw()
            win.flip()
            # Print the shape of a picture1
            #screen.blit(elem[0], (0, 0))
            #pygame.display.flip()
            core.wait(elem[1])
        #pygame.quit()
        rda.stop_thread()
        if testing != 'Test':
            self.eyelink_close()
        win.close()
        core.quit()
        self.experiment_sequence = []
        self.experiment_prerender = []


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
                background_col = block_dict[block_name]["content"]["background_color"]
                size_in_mm = block_dict[block_name]["content"]["img_resolution"][0]
                duration_in_sec = block_dict[block_name]["content"]["duration"]
                if block_dict[block_name]["content"]["type"] == "random":
                    grid_size = 6
                    seed = (block_dict[block_name]["content"]["seed"]) % 2 ** 32
                    self.experiment_sequence.append(
                        Blocks.RandomPatternBlock(background_col, size_in_mm, duration_in_sec, grid_size, block_type, seed))
                else:
                    pattern_id = (block_dict[block_name]["content"]["pattern_id"])
                    self.experiment_sequence.append(
                        Blocks.PatternBlock(background_col, size_in_mm, duration_in_sec, block_type, pattern_id))
            elif block_type == "rest":
                duration_in_sec = block_dict[block_name]["content"]["duration"]
                noise_resolution = block_dict[block_name]["content"]["noise_resolution"]
                seed = (block_dict[block_name]["content"]["seed"]) % 2 ** 32
                self.experiment_sequence.append(
                    Blocks.RestGaussian(block_type, duration_in_sec, noise_resolution, seed_value=seed))

            elif block_type == "execution":
                background_col = block_dict[block_name]["content"]["background_color"]
                duration_in_sec = block_dict[block_name]["content"]["duration"]
                diam_in_mm = block_dict[block_name]["content"]["fixation_poit_diam"]
                self.experiment_sequence.append(Blocks.Execution(background_col, block_type, diam_in_mm, duration_in_sec))

            elif block_type == "command":
                background_col = block_dict[block_name]["content"]["background_color"]
                duration_in_sec = block_dict[block_name]["content"]["duration"]
                diam_in_mm = block_dict[block_name]["content"]["fixation_poit_diam"]
                height_in_mm = block_dict[block_name]["content"]["img_resolution"][0]
                position = block_dict[block_name]["content"]["state"]
                self.experiment_sequence.append(
                    Blocks.Command(background_col, block_type, duration_in_sec, height_in_mm, position, diam_in_mm))

            elif block_type == "custom":
                background_col = block_dict[block_name]["content"]["background_color"]
                duration_in_sec = block_dict[block_name]["content"]["duration"]
                img_path = block_dict[block_name]["content"]["image_path"]
                fit_to_screen = block_dict[block_name]["content"]["fit_to_screen"]
                self.experiment_sequence.append(
                    Blocks.Custom(background_col, block_type, duration_in_sec, img_path, fit_to_screen))

