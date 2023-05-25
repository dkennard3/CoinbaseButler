'''
    TODO: Account for transaction fees.
'''

def get_previous_summary(filename, current_info = []):
    with open(filename, 'ab+') as f:
        right_now, balance, stock_price = current_info
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

def get_basic_history(records):
    history = {}
    for record in records:
        history[records['id']] = records['unit_price']['amount']
    return history


def get_full_history(buys, sells, transactions):
    exchange_types = {'buys': [], 'sells': []}
    for t in transactions:
        _type = t['type']
        if _type == 'buy':
            t['prev_stock_price'] = buys[t['buy']['id']]
            exchange_types['buys'].append(t)
        elif _type == 'sell':
            amt = t['native_amount']['amount']
            t['native_amount']['amount'] = amt[1:]
            t['prev_stock_price'] = sells[t['sell']['id']]
            exchange_types['sells'].append(t)
        elif _type == 'trade':
            amt = t['native_amount']['amount']
            if '-' in amt:
                t['native_amount']['amount'] = amt[1:]
                exchange_types['sells'].append(t)
            else:
                exchange_types['buys'].append(t)
    return exchange_types
