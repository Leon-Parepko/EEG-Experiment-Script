import tkinter as tk
from tkinter import IntVar

# Create a simple graphical interface with 4 parameters: screen size, screen resolution, background color, and file path.
class Components:
    """
    This class contains all graphical components.
    """

    def __init__(self, window):
        self.window = window

        # Get background color
        self.BG_label = tk.Label(self.window, text="Background color:")
        self.BG_entry = tk.Entry(self.window, width=20)

        # Pattern Block
        self.pattern_show_time_label = tk.Label(self.window, text="Pattern show time:")
        self.pattern_show_time = tk.Entry(self.window, width=10)

        self.generate_experiment_button = tk.Button(self.window, text="Generate Experiment", width=25)

        self.start_experiment_button = tk.Button(self.window, text="Start Experiment", width=25)