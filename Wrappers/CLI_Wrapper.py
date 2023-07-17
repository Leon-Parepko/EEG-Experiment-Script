from Main import Main
from JSONGenerator import JSONGenerator

class CLI:
    """
    Command Line Interface for the experiment.
    """
    def __init__(self):
        """
        Initialize the CLI.
        """
        self.executor = Main()

        while True:
            print("Choose an option:\n1. Run the experiment\n2. Generate an experiment file\n3. Exit")
            option = input()
            if option == "1":
                self.run()
            elif option == "2":
                self.generate()
            elif option == "3":
                exit(0)

    def run(self):
        """
        Run the experiment.
        """
        experiment_file_path = input("Enter the experiment file path: ")
        print(f"Parsing the {experiment_file_path} file...")
        self.executor.parse_json(experiment_file_path)
        print("Preprocessing the experiment...")
        self.executor.preprocess_experiment()
        print("Press 'Enter' to start the experiment.")

        # Sorry for that part, but i think it should work :)
        input()
        print("Running the experiment...")
        self.executor.execute_experiment()

    def generate(self):
        file_name = str(input("Enter the file name in format 'name.json': "))
        background_color = str(input("Enter the background color in rgb format (for example: '(30, 42, 255)'): "))

        # Convert the string to tuple
        background_color = tuple(map(int, background_color.strip('()').split(',')))
        pattern_show_time = int(input("Enter the pattern block show duration (in seconds): "))
        command_pattern_correspondance_time = int(input("Enter the command block (after patterns are shown) duration (in seconds): "))
        command_before_execution_time = int(input("Enter the command block (before execution) duration (in seconds): "))
        execution_time = int(input("Enter the execution block duration (in seconds): "))

        print("Generating the experiment file...")
        json_gen = JSONGenerator(file_name=file_name, background_color=background_color, pattern_show_time=pattern_show_time, command_pattern_correspondance_time=command_pattern_correspondance_time, command_before_execution_time=command_before_execution_time, execution_time=execution_time)
        json_gen.gen_experiment_json()

