import json
import numpy as np


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

# TODO: Add file_path as the argument of geometric pattern block
class JSONGenerator:
    def __init__(self, file_name):
        self.content = {}
        self.file_name = file_name
        self.block_id = 0
        self.pattern_show_time = 10
        self.command_pattern_correspondance_time = 5
        self.command_before_execution_time = 3
        self.execution_time = 15
        self.geometric_patterns_num = 12


        # Generate sequence 6 unique geometric patterns id"s
        geometric_patterns = np.random.choice(range(0, 12), 6, replace=False)
        geometric_patterns_commands = [1, 2, 3, 1, 2, 3]

        # Generate a 3 random seed 10 digits long for random pattern generation
        random_patterns = np.random.randint(10**10, size=3)
        random_patterns_commands = [1, 2, 3]

        # Merge a pair of two lists into ones
        self.pattern_sequence = np.concatenate((random_patterns, geometric_patterns))
        self.pattern_commands_sequence = random_patterns_commands + geometric_patterns_commands
        self._pattern_iterator = 0


        # Create 3 arrays of 7 randomly chosen numbers out of 1, 2, 3.
        # each number should occure at least once in each array.
        arr1 = self.__arr_occurance_check(np.random.choice([1, 2, 3], 7))
        arr2 = self.__arr_occurance_check(np.random.choice([1, 2, 3], 7))
        arr3 = self.__arr_occurance_check(np.random.choice([1, 2, 3], 7))
        self.command_sequence = np.concatenate((arr1, arr2, arr3))
        self._execution_iterator = 0


    def __arr_occurance_check(self, arr):
        while True:
            if 1 not in arr:
                arr[np.random.randint(0, 6)] = 1
                continue
            if 2 not in arr:
                arr[np.random.randint(0, 6)] = 2
                continue
            if 3 not in arr:
                arr[np.random.randint(0, 6)] = 3
                continue
            return arr


    # --- Primitive blocks generators ---
    def gen_rest_block_content(self, duration):

        # generate a random seed 10 digits long for noise generation in rest block
        seed = np.random.randint(10**10)

        content = {f"Block_{self.block_id}": {
                        "type": "rest",
                        "content": {
                            "duration": duration,
                            "noise_resolution": 1,
                            "seed": seed
                        }}}
        self.block_id += 1
        return content

    def gen_pattern_block_content(self, pattern_type, pattern_id_or_seed):
        content = {}

        if pattern_type == "random":
            content = {f"Block_{self.block_id}": {
                "type": "pattern",
                "content": {
                    "duration": self.pattern_show_time,
                    "type": "random",
                    "seed": pattern_id_or_seed,
                    "img_resolution": [60, 60]
                }}}

        elif pattern_type == "geometric":
            pass
            content = {f"Block_{self.block_id}": {
                "type": "pattern",
                "content": {
                    "duration": self.pattern_show_time,
                    "type": "geometric",
                    "pattern_id": pattern_id_or_seed,
                    "img_resolution": [60, 60]
                }}}

        self.block_id += 1
        return content

    def gen_command_block_content(self, duration, state):
        content = {f"Block_{self.block_id}": {
            "type": "command",
            "content": {
                "duration": duration,
                "state": state,
                "img_resolution": [80, 80],
                "fixation_poit_diam": 10
            }}}

        self.block_id += 1
        return content

    def gen_execution_block_content(self):
        content = {f"Block_{self.block_id}": {
            "type": "execution",
            "content": {
                "duration": self.execution_time,
                "fixation_poit_diam": 10
            }}}

        self.block_id += 1
        return content




    # --- Sub-blocks generators ---
    def gen_task_subblock(self, pattern_type):
        content = {}

        # Add 3 pairs of pattern and command blocks
        for i in range(3):
            # Add pattern block
            content = {**content, **self.gen_pattern_block_content(pattern_type, self.pattern_sequence[self._pattern_iterator])}
            # Add command block
            content = {**content, **self.gen_command_block_content(self.command_pattern_correspondance_time, self.pattern_commands_sequence[self._pattern_iterator])}

            self._pattern_iterator += 1

        return content

    def gen_execution_subblock(self, last=False):
        content = {}

        # Add command block
        content = {**content, **self.gen_command_block_content(self.command_before_execution_time, self.command_sequence[self._execution_iterator])}
        # Add execution block
        content = {**content, **self.gen_execution_block_content()}
        # Add rest block
        if not last:
            content = {**content, **self.gen_rest_block_content(10)}

        self._execution_iterator += 1

        return content




    # --- Task blocks generator ---
    def gen_pattern_task(self, pattern_type):
        content = {}

        # Add task sub-block
        content = {**content, **self.gen_task_subblock(pattern_type)}
        # Add rest block
        content = {**content, **self.gen_rest_block_content(15)}
        # Add 7 execution sub-block
        for i in range(7):
            last = False
            if i == 6:
                last = True
            content = {**content, **self.gen_execution_subblock(last=last)}

        return content






    def gen_experiment_json(self):
        for i_task in range(5):
            # Merge content dictionary with the first random pattern task block
            if i_task == 0:
                self.content = {**self.content, **self.gen_pattern_task("random")}

            # In two cases merge with geometric pattern task block
            elif i_task == 2 or i_task == 4:
                self.content = {**self.content, **self.gen_pattern_task("geometric")}

            # In other cases merge with rest blocks
            else:
                self.content = {**self.content, **self.gen_rest_block_content(300)}

        # Finally create json file
        with open(self.file_name, "w") as f:
            json.dump(self.content, f, cls=NpEncoder, indent=4)


# TODO: Uncomment for debugging purposes only
# if __name__ == "__main__":
#     json_gen = JSONGenerator("experiment.json")
#     json_gen.gen_experiment_json()


