import json
import Blocks


def get_experiment_sequence(json_file_path):
    experiment_sequence = []
    with open(json_file_path, "r") as file:
        json_data = file.read()
    data = json.loads(json_data)
    result = [{"Block_{}".format(key.split("_")[1]): value} for key, value in data.items()]
    for block_dict in result:
        block_name = next(iter(block_dict))
        block_type = block_dict[block_name]["type"]
        if block_type == "pattern":
            size_in_mm = block_dict[block_name]["content"]["img_resolution"][0]
            duration_in_sec = block_dict[block_name]["content"]["duration"]
            if block_dict[block_name]["content"]["type"] == "random":
                grid_size = 6
                seed = (block_dict[block_name]["content"]["seed"]) % 2 ** 32
                experiment_sequence.append(
                    Blocks.RandomPatternBlock(size_in_mm, duration_in_sec, grid_size, block_type, seed))
            else:
                pattern_id = (block_dict[block_name]["content"]["pattern_id"])
                experiment_sequence.append(
                    Blocks.PatternBlock(size_in_mm, duration_in_sec, block_type, pattern_id))
        elif block_type == "rest":
            duration_in_sec = block_dict[block_name]["content"]["duration"]
            noise_resolution = block_dict[block_name]["content"]["noise_resolution"]
            experiment_sequence.append(
                Blocks.RestGaussian(block_type, duration_in_sec, noise_resolution))
    return experiment_sequence
