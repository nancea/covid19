import csv

f = open('all-states-history.csv')
reader=csv.reader(f)

states={}
for row in reader:
    state=row[1]
    states[state]=0

state_abbreviations = list(states.keys())
for k in range(len(state_abbreviations)):
    abbreviation=state_abbreviations[k]
    states[abbreviation]=k

f.close()
f=open('all-states-history.csv')
reader=csv.reader(f)
writer=csv.writer(open('covid19_days.csv', 'w'))

state_ids=list(states.values())
for row in reader:
   state_id=row[1]
   new_row=[row[0], states[state_id], row[2], row[3], row[4], row[5]]
   writer.writerow(new_row)
   print(row) 