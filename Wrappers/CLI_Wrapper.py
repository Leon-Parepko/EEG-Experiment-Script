from Main import Main

class CLI:
    """
    Command Line Interface for the experiment.
    """
    def __init__(self):
        """
        Initialize the CLI.
        """
        self.executor = Main()

    def run(self):
        """
        Run the experiment.
        """
        self.executor.parse_json("test.json")
        self.executor.preprocess_experiment()

        # TODO: start by pressing a button
        self.executor.execute_experiment()

