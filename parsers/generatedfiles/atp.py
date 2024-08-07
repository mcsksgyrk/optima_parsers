import pandas as pd
import jinja2
from no_casp_parser import generateICs, compileDataRow, generateBounds, getSpecies
import time
import os


def scaleData(source_data, variables, ics):
    dataDf = source_data.copy()
    dataDf.time = source_data.time
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


def generateOutput(ics, variables, dataPoints):
    file_loader = jinja2.FileSystemLoader('../../dataXu')
    env = jinja2.Environment(loader=file_loader)
    template = env.get_template('data_no_sigma.xml')
    ics['ATP'] = 3.000000*10**(-6)
    output = template.render(ics=ics, variables=variables,
                             dataPoints=dataPoints)
    return output


def generateFileName(file_index, directory, maxdigit=4):
    padded_number = str(file_index).zfill(maxdigit)
    file_name = 'atp'+'test'+'_'+padded_number+'.xml'
    path = os.path.join(directory, file_name)
    return path


# Define the function to generate a file with given content
def generate_file(file_index, directory, species, bounds, source_data):
   
    origi_ics = generateICs(species, bounds, True)

    ics = origi_ics

    variables = source_data.columns
    dataPoints = compileDataTable(ics, variables, source_data)

    vars_to_xml = []
    for v in variables:
        if v in origi_ics.keys():
            if 'std' not in v:
                vars_to_xml.append(v)
                ics[v] = origi_ics[v]*source_data[v][0]

    output = generateOutput(ics, vars_to_xml, dataPoints)
    filename = generateFileName(file_index, directory)

    # elmenti generált ic-ket df-be
    with open(filename, 'w') as f:
        f.write(output)
    return filename