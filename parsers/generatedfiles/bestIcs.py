import os
import pandas as pd
import fnmatch
import re


def find_files(directory, pattern):
    matches = []
    for root, dirnames, filenames in os.walk(directory):
        for filename in fnmatch.filter(filenames, f"*{pattern}*"):
            matches.append(os.path.join(root, filename))
    return matches


def readOutICs(path):
    ICs = dict()
    with open(path, 'r') as file:
        for line in file:
            if "component" not in line:
                continue
            key = re.findall(r'preferredKey="(.*?)"', line)[0]
            value = re.findall(r'units="mole fraction" >(.*?)</amount>', line)[0]
            ICs[key] = float(value)
    return ICs


file_list = pd.read_csv("minVals.csv", header=None)[0].to_list()

best_sims = []
for file in file_list:
    f_name = find_files('./', file)
    if f_name:
        best_sims.append(f_name[0])

all_ics = []
for sim in best_sims:
    all_ics.append(readOutICs(sim))

sim_ics = pd.DataFrame(all_ics, index=best_sims)
#sim_ics.agg(['min', 'max']).to_csv("min_and_max.csv")

tets = sim_ics.agg(['min', 'max'])

max_ics = sim_ics.max(axis=0)
min_ics = sim_ics.min(axis=0)
max_dif = max_ics - min_ics

tets.loc[len(tets)] = max_dif
tets.rename(index={2: 'dif'}, inplace=True)
tets.to_csv('min_and_max.csv')

unique_vals_sorted = max_dif.sort_values().unique()
unique_vals_sorted

no_complexes = tets.drop(columns=[col for col in tets.columns if '_' in col], inplace=False)

for series_name, series in no_complexes.items():
    if series.dif < unique_vals_sorted[1]:
        print(series_name)
