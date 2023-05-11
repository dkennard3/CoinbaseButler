import sys

#TODO: for fee in fees: --> in a 'buy' object --> subtract out fees from any buy,sell,or trade
#		to show what you REALLY paid/profited for. Helps 'total_profit' be more accurate too!

#show_trades(all_activity, account_ids, stock_price, balance, changes)

def show_trades(show_details, transactions, buys, sells, account_ids, curr_stock_price, balance, changes):
	buys_at_stock_price = {}
	for buy in buys:
		buys_at_stock_price[buy['id']] = buy['unit_price']['amount']

	sales_at_stock_price = {}
	for sale in sells:
		sales_at_stock_price[sale['id']] = sale['unit_price']['amount']

	exchange_types = {'buys':[], 'sells':[]}
	for t in transactions:
		_type = t['type']
		if _type == 'buy':
			t['prev_stock_price'] = buys_at_stock_price[t['buy']['id']]
			exchange_types['buys'].append(t)
		elif _type == 'sell':
			amt = t['native_amount']['amount']
			t['native_amount']['amount'] = amt[1:]
			t['prev_stock_price'] = sales_at_stock_price[t['sell']['id']]
			exchange_types['sells'].append(t)
		elif _type == 'trade':
			amt = t['native_amount']['amount']
			if '-' in amt:
				t['native_amount']['amount'] = amt[1:]
				exchange_types['sells'].append(t)
			else:
				exchange_types['buys'].append(t)

	currency = exchange_types['buys'][0]['amount']['currency']
	balance = round(float(balance),2)
	total_bought = sum(float(exchange_types['buys'][i]['native_amount']['amount']) for i in range(len(exchange_types['buys'])))
	if len(exchange_types['sells']) > 0:
		total_sold = sum(float(exchange_types['sells'][i]['native_amount']['amount']) for i in range(len(exchange_types['sells'])))
	else:
		total_sold = 0.00
	total_invested = round(float(total_bought - total_sold),2)
	total_profit = round(float(balance - total_invested),2)
	if not show_details:
		return (total_invested, total_profit)

	if not changes:
		stock_print = f'Current {currency} price: ${curr_stock_price}'
	else:	
		prev_stock_price, diff, direction, perc = changes
		stock_print = f'Current {currency} price: ${curr_stock_price}, {direction} ${diff}({perc}%) from ${prev_stock_price}' 
	balance_print = f'Portfolio balance currently at ${balance}'
	profit_print = f'Your Current ${total_invested} invested(bought minus sold) has made you ${total_profit}!'
	print(('='*58).center(64))
	print(('*'*58).center(64))
	print(stock_print.center(64))
	print(balance_print.center(64))
	print(profit_print.center(64))
	print(('*'*58).center(64))
	print(('='*58).center(64))

	for _type in exchange_types.keys():
		#don't need the header printed if no transactions listed
		if not exchange_types[_type]:
			continue
		print__type = currency + " " + _type.lower() 

		print(("*"*(len(print__type)+2)).center(64)) 
		print(print__type.center(64))
		print(("*"*(len(print__type)+2)).center(64)) 
		
		for t in exchange_types[_type]:
			amt = t['native_amount']['amount']
			date = t["created_at"].split('T')[0]
			
			#t['trade']['resource_path'] -> destination of where funds went
			#t['amount']['currency'] -> specifies which account this trade falls under (+/- amount)
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
		print(('-'*36).center(64))
	print()
	return (total_invested, total_profit)
