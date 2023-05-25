def help_menu(display):
    print(f'usage: python main.py {display}\n\n')
    print(
    """
        detail  -- list ALL buys, sells, & trades for 'active'cryptocurrency accounts
        update  -- appends to or creates '<crypto stock name>_past_balances.txt' file
        help  -- displays this page
        [default]  -- quick summary line for each 'active' crypto account (balance greater than $0.00) 
    """)
