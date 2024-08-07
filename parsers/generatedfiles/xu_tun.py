import pandas as pd
import jinja2
from parsers import generateICs, compileDataRow, generateBounds, getSpecies
import time
import os
import numpy as np


def scaleData(source_data, variables, ics):
    dataDf = source_data.copy()
    dataDf.time = source_data.time
    for v in variables:
        if v == 'caspasea':
            dataDf[v] = dataDf[v]*ics['caspase']
        if 'std' in v and v != 'caspaseastd':
            if v[0:-3] in ics.keys():
                dataDf[v] = dataDf[v]*ics[v[0:-3]]
        if v in ics.keys() and 'caspase' not in v:
            dataDf[v] = dataDf[v]*ics[v]
    return dataDf


def compileDataTable(ics, variables, source_data):
    variables = source_data.columns
    # hacking Stress here
    dataDf = scaleData(source_data, variables, ics)
    dataPoints = []
    for i, row in dataDf.iterrows():
        dataPoints.append(compileDataRow(variables, row.values))
    return dataPoints


def generateOutput(ics, variables, dataPoints, sigmas):
    ics['STS'] = 2000*10**(-12)
    file_loader = jinja2.FileSystemLoader('../../dataXu')
    env = jinja2.Environment(loader=file_loader)
    template = env.get_template('data_test1.xml')
    # megszorozza a számolt hibával, a maximum értékét a mérésnek
    output = template.render(ics=ics, variables=variables,
                             dataPoints=dataPoints, stds=sigmas)
    return output


def generateFileName(file_index, directory, maxdigit=4):
    padded_number = str(file_index).zfill(maxdigit)
    file_name = 'xu2014_'+'tun2000'+'_'+padded_number+'.xml'
    path = os.path.join(directory, file_name)
    return path


# Define the function to generate a file with given content
def generate_file(file_index, directory, species, bounds, source_data, sigmas):
    origi_ics = generateICs(species, bounds, True)
    scaled_sigmas = sigmas.copy()
    for k, v in sigmas.items():
        if 'caspase' in k:
            scaled_sigmas[k] = v*origi_ics['caspase']
        else:
            scaled_sigmas[k] = v*origi_ics[k]

    ics = origi_ics

    variables = source_data.columns
    dataPoints = compileDataTable(ics, variables, source_data)

    vars_to_xml = []
    for v in variables:
        if v in origi_ics.keys():
            if 'std' not in v:
                if 'caspase' not in v:
                    ics[v] = origi_ics[v]*source_data[v][0]
                else:
                    ics['caspasea'] = origi_ics['caspase']*source_data[v][0]
                    ics['caspase'] = origi_ics['caspase']-ics['caspasea']
                vars_to_xml.append(v)

    output = generateOutput(ics, vars_to_xml, dataPoints, scaled_sigmas)
    filename = generateFileName(file_index, directory)

    # elmenti generált ic-ket df-be
    with open(filename, 'w') as f:
        f.write(output)
    return filename


# Directory to save files
output_directory = 'xu/tun2000'
data = pd.read_csv('./1dataMin/dataXu_tun2000nm.csv')
treatement = ''
# Create the directory if it does not exist
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Variables and bounds from file file
df = pd.read_excel('../../reactionsICs_w_species.xlsx', header=None,
                   sheet_name='ics', usecols="A:B")
bounds = generateBounds(df)
species = getSpecies('../../refs.csv')
#max_norm = data.max()[1]
sigmas = dict()
for c in data.columns:
    if c == 'time':
        continue
#    data[c] = data[c]/max_norm
    z1 = np.polyfit(data['time'], data[c], 3)
    polynomial = np.poly1d(z1)
    res = data[c]-polynomial(data[c])
    sigmas[c] = np.std(res)
# df to save generated IC sets
# data files
start = time.time()
for i in range(1, 10001):
    file_index = i
    generate_file(file_index, output_directory, species, bounds, data, sigmas)
print("job finished in:", time.time()-start)
