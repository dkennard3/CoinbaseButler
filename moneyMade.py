import os
import sys
# XXX_past_balances.txt format --> "05/23/2022 11:06:04 -> $49.99 @ $53.34 -> up $1.84(+3.57%)"
try:
	numDays = int(sys.argv[1])
except:
	print('usage: python moneyMade.py numDays')
	sys.exit(-1)
try:
	files = os.listdir('./past_balances/')
except:
	print('No \"past_balances/\" directory found. Run main.py to create this directory.')
totals = []
names, infos = [], []
for filename in files:
	if '.txt' != filename[-4:]:
		continue
	with open(f"./past_balances/{filename}", 'r') as f:
		lines = f.readlines()
		smaller_file, days = (True,len(lines)) if numDays > len(lines)+1 else (False,numDays)
		last = [float(fi.strip('\n').split(' ')[3][1:]) for fi in lines[-days-1:]]


		diffs = sum([last[i+1]-last[i] for i in range(len(last)-1)])
		totals.append(round(diffs,2))

	plural = 'day' if days == 1 else 'days'
	name = filename[:-4]
	info = f"${totals[-1]} in last {days} {plural}"
	names.append('{:^30}'.format(name))
	infos.append('{:^30}'.format(info))

print()
n = [names[i:i+3] for i in range(0,len(names)-2,3)]
info = [infos[i:i+3] for i in range(0,len(infos)-2,3)]

for i in range(len(n)):
	print(' '.join(n[i]))
	print(' '.join(info[i]))
	print()

print(f'${round(sum(totals),2)} total for last {days} {plural}')
print()
