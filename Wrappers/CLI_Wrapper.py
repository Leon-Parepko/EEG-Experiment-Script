from Main import Main

class CLI:
    def __init__(self):
        self.executor = Main("data.json")

    def run(self):
        self.executor.preprocess_experiment()
        self.executor.execute_experiment()

