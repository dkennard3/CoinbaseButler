
def print_summary_header(stock_print, balance_print, profit_print):
    print(('='*58).center(64))
    print(('*'*58).center(64))
    print(stock_print.center(64))
    print(balance_print.center(64))
    print(profit_print.center(64))
    print(('*'*58).center(64))
    print(('='*58).center(64))


def print_full_summary(currency, account_ids, exchange_types):
    for _type in exchange_types.keys():
        if not exchange_types[_type]:
            continue
        print__type = currency + " " + _type.lower()

        print(("*"*(len(print__type)+2)).center(64))
        print(print__type.center(64))
        print(("*"*(len(print__type)+2)).center(64))

        for t in exchange_types[_type]:
            amt = t['native_amount']['amount']
            date = t["created_at"].split('T')[0]

            if t['type'] == 'trade':
                title = t['details']['title']
                to_id = t['trade']['resource_path'].split('/')[3]
                to_name = account_ids[to_id]
                if 'to' in title:
                    from_name = t['details']['payment_method_name'].split(' ')[0]
                    for item in account_ids:
                        if item[1] == from_name:
                            from_id = item[0]
                            break
                elif 'from' in title:
                    from_id = t['resource_path'].split('/')[3]
                    from_name = account_ids[from_id]
                print(f'{date} Traded ${amt} from {from_name} to {to_name}'.center(64))
            else:
                print(f'{date} ${amt} @ ${t["prev_stock_price"]}'.center(64))
        print(('-'*36).center(64))
        print(f'Total {currency} {_type} ${round(sum(float(exchange_types[_type][i]["native_amount"]["amount"]) for i in range(len(exchange_types[_type]))),2)} '.center(64))
        print(('-'*36).center(64), '\n')


def print_brief_summary(wallet_summary, USDx_accounts, totals):
    print('='*64)
    print('\n'.join([wallet for wallet in wallet_summary]))
    total, total_balance_diff, total_profit, total_invested = totals
    for acc in USDx_accounts:
        total += round(float(acc['balance']['amount']), 2)
        print(acc['currency'] + ": $" + acc['balance']['amount'])

    result = 'gained' if total_balance_diff >= 0e-2 else 'lost'

    print(f'Total Invested: ${total_invested}')
    print(f'Total  Profits: ${total_profit}')
    print(f'Total  Balance: ${total} ({result} ${total_balance_diff})')
