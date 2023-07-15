"""
Use this file to run the program.
-c - runs the program in CLI (command line) mode
-g - runs the program in GUI (graphical user interface) mode
"""
import sys

if __name__ == '__main__':
    params = sys.argv

    if len(params) == 1:
        print('The program is running in CLI mode by default. Please use -c or -g to specify the mode.')

    elif params[1] == '-c':
        from Wrappers.CLI_Wrapper import CLI
        print('The program is running in CLI mode.')
        cli = CLI()
        cli.run()

    elif params[1] == '-g':
        from Wrappers.GUI_Wrapper import Graphical
        print('The program is running in GUI mode.')
        gui = Graphical()
        gui.run()

    else:
        print('Invalid argument. Please use -c or -g to specify the mode.')
        exit(1)