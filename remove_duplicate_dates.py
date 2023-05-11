import re
from sys import exit, argv
import os

#date format -> mm/dd/yyyy
if __name__ == "__main__":
	files = []
	for _file in os.listdir('./past_balances'):
		if _file.endswith('.txt'):
			files.append('./past_balances/'+_file)
	if len(argv) == 1:
		print("Usage: remove_duplicate_dates.py {dup|last}")
		print("dup  -- removes duplicate dates in all past_balance files")
		print("last -- removes last recorded date in all past_balance files")

	elif argv[1] == 'dup':
		for past_file in files:
			with open(past_file, 'r') as f:
				curr_line = f.readline()
				working_date = curr_line.split(" ")[0]
				new_lines = []
				new_lines.append(curr_line)

				while curr_line:
					curr_date = curr_line.split(" ")[0]
					if curr_date != working_date:
						working_date = curr_date
						new_lines.append(curr_line)
					curr_line = f.readline()

			with open(past_file, 'w') as f:
				for line in new_lines:
					f.write(line)

	elif argv[1] == 'last':
		answer = str(input("Delete last recorded date for all past_balance files?(y/n)")).lower().strip()
		if answer == 'y':
			for past_file in files:
				with open(past_file, 'ab+') as f:
					f.seek(-4,1)
					while f.read(1).decode('utf-8') != '\n':
						f.seek(-2,1)
					f.truncate() #delete everything ahead of file pointer
		elif answer == 'n' or answer != 'y':
			exit(0)
