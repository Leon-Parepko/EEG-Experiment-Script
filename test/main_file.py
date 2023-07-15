import Parser
import execute_experiment

experiment_sequence = Parser.get_experiment_sequence("data.json")
execute_experiment.execute_experiment_sequence(experiment_sequence)
