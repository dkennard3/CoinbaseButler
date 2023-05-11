def show_top_cryptos(client):	
	stock_prices = []
	with open('crypto_currency_list.txt', 'r+') as f:
		currency_list = [item.rstrip('\n') for item in f.readlines()]
	for cur in currency_list:
		curr_pair = cur + '-USD'
		try:
			stock_price = client.get_spot_price(currency_pair=curr_pair)
		except NotFoundError:
			continue
		else:
			amt = stock_price['amount']
			stock_prices.append(float(amt))

	#grab the top 20 most valuable cryptos & sort by stock price 
	final_prices = dict(zip(currency_list, stock_prices))
	top_20 = sorted(final_prices.items(), key=lambda kv:kv[1], reverse=True)[:20]
	print("TOP 20 CRYPTOS RIGHT NOW!!")
	for i in range(0,len(top_20),5):
		print(top_20[i:i+5])
