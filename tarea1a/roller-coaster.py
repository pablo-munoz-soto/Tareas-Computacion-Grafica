import numpy as np
import csv
import transformations as tr
puntos=[]
with open('track.txt') as csv_file:
    csv_reader=csv.reader(csv_file, delimiter='\t')
    for row in csv_reader:
        puntos.append(', '.join(row))

print(puntos)