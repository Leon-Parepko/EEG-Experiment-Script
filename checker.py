import pandas as pd
import json

properties_path = 'properties.json'
datablocks_path = 'exp27_2/datablocks.csv'
datablocks_path = 'datablocks.csv'
experiment_path = 'experiment_53.json'

print(1749350443.1718 - 1749348872.161915)
print(1749374945.360994 - 1749373377.2223)
print(1749364059.409791 - 1749363053.610449)
print(1749371634.650823 - 1749371394.339825)
with open(properties_path,'r') as f:
    props = json.load(f)
sr = props['sampling_interval']
chan_names  = props['channel_names']

with open(experiment_path,'r') as f:
    experiment_seq = json.load(f)

eeg_df = pd.read_csv(datablocks_path, header=None, names=['block_id']+chan_names)
prev = 0
for d, i in eeg_df.iterrows():
    if d >= prev + 2:
        print(d)
    prev = d
eeg_duration = len(eeg_df) / sr
expected_duration = sum(block['content'].get('duration') for block in experiment_seq.values())

print(f"Expected: \t {expected_duration} sec. \t {expected_duration / 60:.2f} min. \nGot: \t\t {int(eeg_duration)} sec. \t {eeg_duration / 60:.2f} min.")