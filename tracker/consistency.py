import csv

file = 'SPOT_BTC_USDT_1m.csv'

with open(file, newline='') as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    timestamps = [float(row[2]) for row in csv_reader]

from collections import Counter

# Check hoe groot de tijdstappen zijn.
# Als er verschillende groottes zijn, kan dan duiden op onvolledige data
diffs = Counter([(timestamps[i+1]-timestamps[i])/60000 for i in range(len(timestamps)-1)])
print(diffs)
