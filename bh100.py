import coinmarketcap
import requests
from bs4 import BeautifulSoup
import re
import click
import json
from collections import OrderedDict


def get_coins(quantity):
    market = coinmarketcap.Market()
    coins = market.ticker(start=0, limit=quantity)

    return [{k: coin[k] for k in ('id', 'name', 'rank', 'symbol')} for coin in coins]


def get_markets(coin, quantity):
    url = 'https://coinmarketcap.com/currencies/{}/'.format(coin)
    page = requests.get(url)
    if page.status_code == 200:
        c = page.content
        soup = BeautifulSoup(c, 'html.parser')
        table = soup.find('table', id='markets-table')
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        exchanges = []
        for row in rows:
            exchange = row.find_all('a', {'href': re.compile(r'/exchanges/*')})
            exchanges.append(exchange[0].text)

#        for row in rows[:quantity]:
#             exchange = row.find_all('a', {'href': re.compile(r'/exchanges/*')})
#             exchanges.append(exchange[0].text)

    else:
        print('Error reaching page')
        exchanges = ['Error']

    return list(OrderedDict.fromkeys(exchanges))[:quantity]


@click.command()
@click.option('--num_coins', prompt='How many coins would you like in the list?')
@click.option('--num_markets', prompt='How many exchanges would you like to see for each coin?')
def main(num_coins, num_markets):
    print('Getting coins...')
    coins = get_coins(num_coins)
    for coin in coins:
        exchanges = get_markets(coin['id'], int(num_markets))
        coin['markets'] = exchanges
        coin.pop('id')

    with open('results.json', 'w') as fp:
        json.dump(coins, fp)

    print('Results in results.json')
    return


if __name__ == '__main__':
    main()
