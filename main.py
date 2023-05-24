from coinbase.wallet.client import Client
from coinbase.wallet.error import NotFoundError
from datetime import datetime
import json
import os
from sys import exit, argv
from pprint import pprint
from show_top_crpytos import show_top_cryptos
from exchange import show_trades
from help_menu import help_menu

#TODO: *Specify whether a buy/sell/trade occurred on the same day that a _past_balances line
#       *is being written. 

commands = ['detail', 'top', 'write', 'update']
display = '{'+(" | ").join(commands)+'}'

if len(argv)==1: 
    print(f'usage: python main.py {display}\n')
    print('- Choose one or more of the above commands, separated by a space \" \"')
    print('- You can enter these commands in any order you want')
    print('- If no commands are specified, program prints summary lines for each crypto wallet')
    while True:
        print(f'\nCommand list: {display}')
        words = input('Select commands from the command list\n[Q] to exit.[H] for help menu.\n\n-->').strip().split()
        if not words:
            print('Running in \"default\" mode')
            break
        for word in words:
            if word not in commands:
                print(f'Command \"{word}\" not recognized.')
                break
            elif word.upper() == 'Q':
                exit(0)
            elif word.upper() == 'H':
                help_menu()
        break


show_detail = True if 'detail' in argv else False 
write_to_file = True if 'write' in argv else False 
update_new_accounts = True if 'update' in argv else False 
if 'top' in argv: 
    show_top_cryptos()

#display the current time of running tradeBot.py
now = datetime.now()
right_now = now.strftime("%m/%d/%Y %H:%M:%S")
curr_date = right_now.split(" ")[0]

#read in API credentials required for subsequent HTTP requests
with open('secret.txt','r') as f:
    api_key = f.readline().rstrip('\n')
    api_secret = f.readline().rstrip()
client = Client(api_key, api_secret)

accounts = []
active_accounts = []
USDx_accounts = []
account_ids = {}
active_account_ids = {}

try:
    with open('account_ids.txt', 'r') as f:
        account_ids = json.loads(f.read())
except FileNotFoundError:
    print('No preexisting account_ids.txt file found')
    print('Creating new account_ids.txt file...')
    update_new_accounts = True
else:
    with open('active_account_ids.txt', 'r') as f:
        active_account_ids = json.loads(f.read())
    for _id in active_account_ids:
        acc = client.get_account(_id)
        USDx_accounts.append(acc) if acc['currency'] in ['USD','USDT','USDC'] else active_accounts.append(acc) 

if update_new_accounts:
    all_accounts = client.get_accounts(limit=300)['data']
    for acc in all_accounts:
        if acc['currency'] in ['USD','USDT','USDC']:
            USDx_accounts.append(acc)

        elif round(float(acc['native_balance']['amount']),2) > 0: 
            active_accounts.append(acc)
            active_account_ids[acc['id']] = acc['currency']

        #accounts.append(acc) 
        account_ids[acc['id']] = acc['currency']

    with open('account_ids.txt', 'w') as f:
        f.write('{\n')
        keys = list(account_ids.keys())
        last_key = keys[-1]
        keys = keys[:-1]
        for _id in keys:
            f.write("  \""+str(_id)+"\""+": \""+str(account_ids[_id])+"\",\n")
        f.write("  \""+str(last_key)+"\""+": \""+str(account_ids[last_key])+"\"\n")
        f.write('}\n')

    with open('active_account_ids.txt', 'w') as f:
        f.write('{\n')
        keys = list(active_account_ids.keys())
        last_key = keys[-1]
        keys = keys[:-1]
        for _id in keys:
            f.write("  \""+str(_id)+"\""+": \""+str(active_account_ids[_id])+"\",\n")
        f.write("  \""+str(last_key)+"\""+": \""+str(active_account_ids[last_key])+"\"\n")
        f.write('}\n')

    print(f'{len(all_accounts)} crpytos currently available on Coinbase.com') 
    with open('crypto_currency_list.txt', 'r+') as f:
        currency_list = [item.rstrip('\n') for item in f.readlines()]
        if len(currency_list) != len(all_accounts):
            for acc in all_accounts:
                if acc['currency'] not in currency_list:
                    f.write(acc['currency']+'\n') 

total = 0e-5
wallet_summary = []
past_balances = []
total_profit = 0.0 
total_invested = 0.0 
total_balance_diff = 0.0
t = [] 

if not os.path.exists('./past_balances'):
    os.mkdir('./past_balances')

for acc in active_accounts:
    balance = round(float(acc['native_balance']['amount']), 2)
    
    prev_stock_price, prev_balance, perc, balance_diff, diff = [0.0 for i in range(5)]
    direction = ''
    first_entry = False

    total += balance

    curr_pair = acc['currency'] + '-USD'
    stock_price = client.get_spot_price(currency_pair=curr_pair)['amount']
    stock_price = round(float(stock_price), 10 if round(float(stock_price),2) == 0 else 2)

    filename = f'./past_balances/{acc["currency"]}_past_balances.txt'
    
    with open(filename, 'ab+') as f:
        if f.tell() == 0: #first time creating this _past_balances.txt file
            f.write(bytes(f'{right_now} -> ${balance} @ ${stock_price}\n', 'utf-8'))
            first_entry = True

        else: #get the last recorded stock price and portfolio balance
            while f.read(1).decode('UTF-8') != ':':
                f.seek(-2, 1)    

            #last recorded stock price is right after '@' character
            buf = f.readline().decode('UTF-8').split(" ")
            prev_stock_price = buf[4][1:]

            prev_stock_price = round(float(prev_stock_price),2)
            diff = round(abs(stock_price - prev_stock_price),2)
            perc = abs(prev_stock_price - stock_price)/prev_stock_price
            perc = round(perc*100.0,2)    #representing as a percentage, rather than decimal. 0.02 vs. 2%

            prev_balance = buf[2][1:]
            prev_balance = round(float(prev_balance),2)
            balance_diff = round(abs(balance-prev_balance),2)

            if stock_price >= prev_stock_price: 
                direction='up'
                total_balance_diff += balance_diff
                perc = f'+{perc}'
            else: 
                direction='down'
                total_balance_diff -= balance_diff
                perc = f'-{perc}' 

            if write_to_file: 
                entry = bytes(f'{right_now} -> ${balance} @ ${stock_price} -> {direction} ${diff}({perc}%)\n','utf-8')
                f.write(entry) 

    summary_line = f'{acc["currency"]} ${balance} @ ${stock_price} -> {direction} ${balance_diff}({perc}%)' 
    wallet_summary.append(summary_line)
    
    all_activity = acc.get_transactions()['data']
    buys = acc.get_buys()['data']
    sells = acc.get_sells()['data']
    changes = [prev_stock_price, diff, direction, perc] if not first_entry else [] 

    i,p = show_trades(show_detail, all_activity, buys, sells, account_ids, stock_price, balance, changes)
    total_profit += p
    total_invested += i

print('='*64)
print('\n'.join([wallet for wallet in wallet_summary]))
for acc in USDx_accounts:
    total += round(float(acc['balance']['amount']),2)
    print(acc['currency'] + ": $" + acc['balance']['amount']) 

total = round(total,2)
total_balance_diff = round(total_balance_diff,2)
total_profit = round(total_profit, 2)
total_invested = round(total_invested, 2)
result = f'gained' if total_balance_diff >= 0e-2 else f'lost'

print(f'Total Invested: ${total_invested}')
print(f'Total  Profits: ${total_profit}')
print(f'Total  Balance: ${total} ({result} ${total_balance_diff})')
