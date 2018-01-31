import coinmarketcap
import requests
from bs4 import BeautifulSoup
import re


def get_coins(quantity):
    market = coinmarketcap.Market()
    coins = market.ticker(start=0, limit=quantity)

    return [{k: coin[k] for k in ('name', 'rank', 'symbol')} for coin in coins]


def get_markets(coin, quantity=1):
    url = 'https://coinmarketcap.com/currencies/{}/'.format(coin)
    page = requests.get(url)
    if page.status_code == 200:
        c = page.content
        soup = BeautifulSoup(c, 'html.parser')
        table = soup.find('table', id='markets-table')
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        for row in rows[:quantity]:
            exchange = row.find_all('a', {'href': re.compile(r'/exchanges/*')})
            print(exchange[0].text)

    else:
        print('Error reaching page')

    return


if __name__ == '__main__':
    print(get_coins(3))
    get_markets('bitcoin', quantity=3)
