import pandas as pd
import jinja2
from no_casp_parser import generateICs, compileDataRow, generateBounds, getSpecies
import time
import os


def scaleData(source_data, variables, ics):
    dataDf = source_data.copy()
    dataDf.time = source_data.time*60
    for v in variables:
        if v == 'caspasea':
            dataDf[v] = dataDf[v]*ics['caspase']
            dataDf[v+"std"] = dataDf[v+"std"]*ics['caspase']
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


def generateOutput(ics, variables, dataPoints):
    file_loader = jinja2.FileSystemLoader('../../dataXu')
    env = jinja2.Environment(loader=file_loader)
    template = env.get_template('data_w_std.xml')
    # megszorozza a számolt hibával, a maximum értékét a mérésnek
    output = template.render(ics=ics, variables=variables,
                             dataPoints=dataPoints)
    return output


def generateFileName(file_index, directory, name, maxdigit=4):
    padded_number = str(file_index).zfill(maxdigit)
    file_name = 'atp'+'_test'+'_'+padded_number+'.xml'
    path = os.path.join(directory, file_name)
    return path


# Define the function to generate a file with given content
def generate_file(file_index, directory, species, bounds, source_data):
    origi_ics = generateICs(species, bounds, True)
    variables = source_data.columns
    name = ['100nm', '2000nm']

    ics = origi_ics
    dataPoints = compileDataTable(ics, variables, source_data)

    vars_to_xml = []
    for v in variables:
        if v in origi_ics.keys():
            if 'std' not in v:
                if 'caspase' not in v:
                    vars_to_xml.append(v)
                    ics[v] = origi_ics[v]*source_data[v][0]
                else:
                    ics['caspasea'] = origi_ics['caspase']*source_data['caspasea'][0]
                    ics['caspase'] = origi_ics['caspase']-ics['caspasea']
                    vars_to_xml.append('caspasea')

    output = generateOutput(ics, vars_to_xml, dataPoints)
    filename = generateFileName(file_index, directory, name[1])

    # elmenti generált ic-ket df-be
    with open(filename, 'w') as f:
        f.write(output)
    return filename