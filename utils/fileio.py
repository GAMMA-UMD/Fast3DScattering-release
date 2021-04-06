import re
import numpy as np

def read_field_points(path):
    with open (path, 'rt') as myfile:
        content = myfile.readlines()
    content = [x.strip() for x in content]
    specs = list(map(int, content[3].split()))
    
    spec_offset = 10
    field_start = spec_offset + specs[0] + specs[1] + 3
    field_points = []
    for i in range(specs[2]):
        data = list(map(float, content[field_start+i].split()))
        field_points.append(data[1:])
    return np.array(field_points)

def read_field_pressure(path, use_real=True):
    with open (path, 'rt') as myfile:
        content = myfile.read()
    rgx = re.compile('[%s]' % "(),")
    content = rgx.sub(' ', content)
    res = content[content.find("Field Points"):].split('\n')
    field_pressure = []
    if use_real:
        for line in res[3:-9]:
            data = list(map(float, line.split()))
            field_pressure.append(np.linalg.norm([data[7], data[8]]))
    else:        
        for line in res[3:-9]:
            data = list(map(float, line.split()))
            field_pressure.append(complex(data[7], data[8]))
    return np.array(field_pressure)