import csv

states_file = open("all-states-history.csv")
r = csv.reader(states_file)
row0 = next(r)
row0.append('ids')
