#!/bin/python3

import sys

filename = sys.argv[1] # Read the filename from the command line argument
sum_second_col = 0
count = 0
if filename.find('stiming') >= 0:
    freq = float(sys.argv[2])
else:
    freq = 1

with open(filename, 'r') as file:
    for line in file:
        columns = line.strip().split(',')
        if len(columns) >= 2 and columns[1].isdigit():
            sum_second_col += int(columns[1])
            count += 1

mean_second_col = sum_second_col / freq / count * 2.5 / 2
nsamp = int(mean_second_col)
print(nsamp)
