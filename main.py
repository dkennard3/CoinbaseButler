import json
import history as hist
import summary_formats as fmt
from sys import exit, argv
from os import path, mkdir
from coinbase.wallet.client import Client
from datetime import datetime
from help_menu import help_menu
from getpass import getpass


def write_ids(account_dict, f):
    f.write('{\n')
    keys = list(account_dict.keys())
    last_key = keys[-1]
    keys = keys[:-1]
    for _id in keys:
        f.write("  \""+str(_id)+"\""+": \""+str(account_dict[_id])+"\",\n")
    f.write("  \""+str(last_key)+"\""+": \""+str(account_dict[last_key])+"\"\n")
    f.write('}\n')

def update_accounts(client):
    active_accounts = []
    all_accounts = client.get_accounts(limit=300)['data']
    for acc in all_accounts:
        if round(float(acc['native_balance']['amount']), 2) > 0:
            active_accounts.append(acc)
    with open('active_account_ids.txt', 'w') as f:
        write_ids(active_accounts, f)

    return active_accounts

def get_previous_summary(filename):
    with open(filename, 'ab+') as f:
        # very first entry for new crypto purchase
        if f.tell() == 0:
            f.write(bytes(f'{right_now} -> ${balance} @ ${stock_price}\n', 'utf-8'))
            return 0e-2, 0e-2
        # get the last recorded stock price and portfolio balance
        while f.read(1).decode('UTF-8') != ':':
            f.seek(-2, 1)
        # last recorded stock price is right after '@' character
        buf = f.readline().decode('UTF-8').split(" ")

    prev_stock_price = round(float(buf[4][1:]), 2)
    prev_balance = round(float(buf[2][1:], 2))

    return prev_stock_price, prev_balance


if __name__ == "__main__":
    print('''
        \nPlease provide your Coinbase API key and secret
        \nYour input will be invisible. Right-Click to paste from clipboard\n
        \nNEVER SHARE YOUR CREDENTIALS WITH ANYONE!!!\n
          ''')
    try:
        api_key = getpass('API key: ')
        api_secret = getpass('Secret: ')
        client = Client(api_key, api_secret)
    except:
        print('ERROR: Invalid key and/or secret\nPlease try again.')
        exit(-1)

    commands = ['detail', 'write', 'update']
    display = '{'+(" | ").join(commands)+'}'

    # CLI intro pops when user runs main.py w/out args
    if len(argv) == 1:
        print(f'usage: python main.py {display}\n')
        print('- Choose from the above commands, separated by whitespace')
        print('- You can enter these commands in any order you want')
        print('- Press Enter for quick summary (default)\n')
        while True:
            prompt = f'\nCommand list: {display}'
            prompt += 'Select commands from the command list\n' \
                'Press [Q] to exit [H] for help menu.\n\n-->'
            words = input(prompt).strip().split()
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

    if 'update' in argv:
        update_accounts()

    # display the current time of running tradeBot.py
    now = datetime.now()
    right_now = now.strftime("%m/%d/%Y %H:%M:%S")
    curr_date = right_now.split(" ")[0]

    try:
        with open('active_account_ids.txt', 'r') as f:
            active_account_ids = json.loads(f.read())

    except FileNotFoundError:
        print('No preexisting active_account_ids.txt file found')
        print('Creating new active_account_ids.txt file...')
        active_accounts = update_accounts(client)

    else:
        for _id in active_account_ids:
            acc = client.get_account(_id)
            active_accounts.append(acc)

    USDx_accounts, wallet_summary, past_balances = [[] for i in range(3)]
    total, total_profit, total_invested, total_balance_diff = [0.0 for i in range(4)]

    if not path.exists('./past_balances'):
        mkdir('./past_balances')

    for acc in active_accounts:
        if 'USD' in str(acc['currency']):
            USDx_accounts.append(acc)
            continue

        filename = f'./past_balances/{acc["currency"]}_past_balances.txt'
        prev_stock_price, prev_balance = get_previous_summary(filename)
        balance_diff = round(balance-prev_balance, 2)
        total_balance_diff += balance_diff

        perc, balance_diff, diff = [0e-2 for i in range(3)]
        all_activity = acc.get_transactions()['data']
        balance = round(float(acc['native_balance']['amount']), 2)
        buy_history = hist.get_basic_history(acc.get_buys()['data'])
        sell_history = hist.get_basic_history(acc.get_sells()['data'])

        exchange_types = hist.get_full_history(buy_history, sell_history, all_activity)
        buy_amounts = [float(item['native_amount']['amount']) for item in exchange_types['buys'].keys()]
        sell_amounts = [float(item['native_amount']['amount']) for item in exchange_types['sells'].keys()]

        total_bought = sum(buy_amounts)
        if len(exchange_types['sells']) > 0:
            total_sold = sum(sell_amounts)
        else:
            total_sold = 0.00

        i = round(float(total_bought - total_sold), 2)
        p = round(float(balance - i), 2)

        total += balance
        total_invested += i
        total_profit += p

        curr_pair = acc['currency'] + '-USD'
        stock_price_raw = client.get_spot_price(currency_pair=curr_pair)['amount']
        stock_price = round(float(stock_price_raw), 10 if round(float(stock_price_raw), 2) == 0 else 2)

        diff = round(stock_price - prev_stock_price, 2)

        # represent as a percentage, rather than decimal
        if int(prev_stock_price) != 0:
            perc = abs(prev_stock_price - stock_price)/prev_stock_price
        perc = round(perc*100.0, 2)

        if diff >= 0e-2:
            direction = 'up'
            perc = f'+{perc}'
        else:
            direction = 'down'
            perc = f'-{perc}'

        summary_str = f'${balance} @ ${stock_price} -> {direction} ${balance_diff}({perc}%)'
        if 'write' in argv:
            with open(filename, 'a') as f:
                entry = f'{right_now} -> {summary_str}\n'
                f.write(entry, 'utf-8')

        one_line_summary = f'{acc["currency"]} {summary_str}'
        wallet_summary.append(one_line_summary)

        if 'detail' in argv:
            movement_text = ''
            if diff != 0e-2:
                movement_text = f', {direction} ${diff}({perc}%) from ${prev_stock_price}'

            stock_print = f'Current {acc["currency"]} price: ${stock_price}{movement_text}'
            balance_print = f'Portfolio balance currently at ${balance}'
            profit_print = f'Your Current ${total_invested} invested' \
                f'(bought minus sold) has made you ${total_profit}!'

            fmt.print_summary_header(stock_print, balance_print, profit_print)
            fmt.print_full_summary(acc['currency'], active_account_ids, exchange_types)

    totals = [total, total_balance_diff, total_profit, total_invested]
    fmt.print_brief_summary(wallet_summary, USDx_accounts, totals)
