def help_menu():
	print("""
										**TradeBot Commands**
 <default> -- quick summary line for each 'active' crypto account (balance greater than $0.00) 
	       -- only shows balance, stock price, stock price diff., percentage diff, & overall balance
	detail -- lists all buys, sells, & trades for each 'active' crypto account 
		   -- Also shows total $ invested (total bought minus total sold) and rough-estimate $ profit made.
	   top -- lists the top 20 cryptos on Coinbase, sorted by current stock prices
	 write -- appends to or creates '<crypto stock name>_past_balances.txt' file, which tracks the date, 
			  portfolio balance, & stock price during the time main.py was run
	update -- get the names of any new cryptos added to Coinbase.com, and add them to your local list 
			  of cryptos in crypto_currency_list.txt
		   -- if you've purchased any new crypto recently, this will save its name and ID 
		      to your local account_ids.txt file
	  help -- displays this page & exits main.py
	""")

if __name__=="__main__":
	help_menu()
