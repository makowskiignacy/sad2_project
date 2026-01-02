"""
Script takes two arguments: name of the file to concatanate 
and the name of the output directory(if it doesn't exist, it will be created)
Example usage : 
python3 concat.py BN_data_new/BN_data/nodes8_steps20_sample1_ntraj10_async.data fixed/ 
"""


import sys
import pandas as pd
from pathlib import Path

filepath = sys.argv[1]
# get the lenght of trajectory out of the file, For example: nodes8_steps20_sample1_ntraj10_async.data
output_directory = Path(sys.argv[2])
path = Path(filepath)
name = path.name
info = name.split("_")
lenght = int(info[1][5:]) + 1
n_series = int(info[3][5:])



df = pd.read_csv(filepath, sep="\t", skip_blank_lines=True, header= None)
formated = df.set_index(0).groupby(level=0).apply(lambda group: group.to_numpy().ravel()).apply(pd.Series)
# now the first row is probably the one that starts with gene
# delete the first row
df = formated.iloc[1:,:]

# make the header
names = []
for j in range(1,n_series+1):
    for i in range(1, lenght+1):
        names.append(f"s{j}:t{i}")

 

df.columns = names

# write the df to a file mb add smth to the original name
output_directory.mkdir(parents=True, exist_ok=True)
new_path = Path(output_directory) / ("concat_" + name)
df.index.name = "net"
df.to_csv(new_path, sep="\t", index=True, header = True)

#or just make them a new column names...