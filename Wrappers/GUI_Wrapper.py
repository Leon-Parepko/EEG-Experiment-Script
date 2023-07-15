from Wrappers import GUI_Components
from Wrappers import GUI_Grid
import tkinter as tk

class Graphical:
    def __init__(self):
        pass

    def run(self):
        window = tk.Tk()
        window.title('EEG-Experiment')

        gui = GUI_Components.Components(window)
        GUI_Grid.construct_grid(gui)

        window.mainloop()




