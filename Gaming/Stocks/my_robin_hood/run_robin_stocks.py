"""
josef.sertl@web.de
AdID0dN5fKztyr3j
"""
import robin_stocks


user_name = 'josef.sertl@web.de'
pass_word = 'AdID0dN5fKztyr3j'

# robin_stocks.login(user_name,pass_word)
# my_stocks = robin_stocks.build_holdings()
# for key,value in my_stocks.items():
#     print(key,value)

optionData = robin_stocks.find_options_for_list_of_stocks_by_expiration_date(['fb','aapl','tsla','nflx'],
    expirationDate='2019-11-16',optionType='call')
for item in optionData:
    print(' price -',item['strike_price'],' exp - ',item['expiration_date'],' symbol - ',
          item['chain_symbol'],' delta - ',item['delta'],' theta - ',item['theta'])
