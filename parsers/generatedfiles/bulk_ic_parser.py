import os
import pandas as pd
import fnmatch
import re
import numpy as np

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


def getXMLpath(path, n):
    with open(path,'r') as f:
        for line in f:
            if 'NAME' not in line:
                continue
            if n in line:
                val = line.strip()[5:]
                return val

opt_path = '/home/nvme/Opt/'
mech_list = find_files(opt_path+'5_Bence/1_mechtest/','onebyone')
# delle supl:
# mtor=4153, ampk=7618, akt=9473, tsc=5877
#art
# akt=4264 mtor=8167 ampk=7351
best_ICs={'delle2014_suppl': {'mtor':4153, 'ampk':7618, 'akt':9473, 'tsc':5877},
          'delle2014_art': {'akt':4264, 'mtor':8167, 'ampk':7351},
          #'holczer': {'ulk':4153, 'mtor':6235, 'ampk':8795, 'aut':5011},
          'holczer': {'ulk':4153, 'mtor':6235},
          'zeng': {'casp':6366, 'aut':9572, 'bax':5951, 'bec1':3893}}


all_ics = []
file_names = []
for k,v in best_ICs.items():
    for mech in mech_list:
        if k in mech:
            for vk,vv in v.items():
                if vk in mech:
                    xml_path = opt_path+getXMLpath(mech,str(vv))
                    all_ics.append(readOutICs(xml_path))
                    file_names.append(xml_path)

sim_ics = pd.DataFrame(all_ics, index=file_names)
np.log10(10**(-12))
tets = sim_ics.agg(['min', 'max'])


max_ics = sim_ics.max(axis=0)
min_ics = sim_ics.min(axis=0)
max_dif = max_ics - min_ics

mag_dif = (max_ics.apply(np.log10) - min_ics.apply(np.log10)).apply(np.abs)
mag_dif.replace([np.inf, -np.inf], np.nan, inplace=True)
mag_dif.dropna(inplace=True)
mag_dif.sort_values(inplace=True)
mag_dif.to_csv('./onebyone_mag_norips.csv')

tets.loc[len(tets)] = max_dif
tets.rename(index={2: 'dif'}, inplace=True)
tets.to_csv('./min_and_max_norips.csv')

unique_vals_sorted = max_dif.sort_values().unique()

no_complexes = tets.drop(columns=[col for col in tets.columns if '_' in col], inplace=False)
no_complexes.apply(np.log10).apply(np.abs)

for series_name, series in no_complexes.items():
    if series.dif < unique_vals_sorted[1]:
        print(series_name)
