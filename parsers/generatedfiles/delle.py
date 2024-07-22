import pandas as pd
import jinja2
from parsers import generateICs, compileDataRow, generateBounds, getSpecies
import time
import os


def scaleData(source_data, variables, ics):
    dataDf = source_data.copy()
    dataDf.time = source_data.time*60
    for v in variables:
        if 'std' in v:
            if v[0:-3] in ics.keys():
                dataDf[v] = dataDf[v]*ics[v[0:-3]]
        if v in ics.keys():
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
    file_loader = jinja2.FileSystemLoader('../../dataXu')
    env = jinja2.Environment(loader=file_loader)
    template = env.get_template('data_test1.xml')
    # megszorozza a számolt hibával, a maximum értékét a mérésnek
    output = template.render(ics=ics, variables=variables,
                             dataPoints=dataPoints, stds=sigmas)
    return output


def generateFileName(file_index, directory, maxdigit=4):
    padded_number = str(file_index).zfill(maxdigit)
    file_name = 'delle2014_'+'suppl'+'_'+padded_number+'.xml'
    path = os.path.join(directory, file_name)
    return path


# Define the function to generate a file with given content
def generate_file(file_index, directory, species, bounds, source_data):
   # sigmas_non_scaled = {'mTORa': 0.17878573914637977,
   #                      'AKTa': 0.18604569416239872,
   #                      'AMPKa': 0.14158496278501073}
    sigmas_non_scaled = {'mTORa': 0.23498394810272363,
                         'TSCa': 0.18381371460154958,
                         'AKTa': 0.2646293403942731,
                         'AMPKa': 0.2969378196038133}

    origi_ics = generateICs(species, bounds, True)
    scaled_sigmas = sigmas_non_scaled.copy()
    for k, v in sigmas_non_scaled.items():
        scaled_sigmas[k] = v*origi_ics[k]

    ics = origi_ics

    variables = source_data.columns
    dataPoints = compileDataTable(ics, variables, source_data)

    vars_to_xml = []
    for v in variables:
        if v in origi_ics.keys():
            if 'std' not in v:
                vars_to_xml.append(v)
                ics[v] = origi_ics[v]*source_data[v][0]

    output = generateOutput(ics, vars_to_xml, dataPoints, scaled_sigmas)
    filename = generateFileName(file_index, directory)

    # elmenti generált ic-ket df-be
    with open(filename, 'w') as f:
        f.write(output)
    return filename


# Directory to save files
output_directory = 'delle2014/suppl'
data = pd.read_csv('./1dataMin/delle2014_dataSuppl.csv')
treatement = ''
# Create the directory if it does not exist
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Variables and bounds from file file
df = pd.read_excel('../../reactionsICs_w_species.xlsx', header=None,
                   sheet_name='ics', usecols="A:B")
bounds = generateBounds(df)
species = getSpecies('../../refs.csv')

# df to save generated IC sets
allICs = pd.DataFrame(index=species)
# data files
start = time.time()
for i in range(1, 10001):
    file_index = i
    generate_file(file_index, output_directory, species, bounds, data)
print("job finished in:", time.time()-start)
