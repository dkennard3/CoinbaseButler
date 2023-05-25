'''
    TODO: Account for transaction fees.
'''


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
