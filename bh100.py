import coinmarketcap
import requests
from bs4 import BeautifulSoup
import re
import click
import json
from collections import OrderedDict


class Coin:
    def __init__(self, cmc_id, name, rank, symbol):
        self.id = cmc_id
        self.name = name
        self.rank = rank
        self.symbol = symbol
        self.url = 'https://coinmarketcap.com/currencies/{}/'.format(cmc_id)
        self.get_exchanges()

    def get_exchanges(self):
        cmc_page = requests.get(self.url)
        c = cmc_page.content
        soup = BeautifulSoup(c, 'html.parser')
        table = soup.find('table', id='markets-table')
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        exchanges = []
        for row in rows:
            exchange = row.find_all('a', {'href': re.compile(r'/exchanges/*')})
            exchanges.append(exchange[0].text.lower())

        dedup = list(OrderedDict.fromkeys(exchanges))
        self.exchanges = dedup


class Exchange:
    def __init__(self, name, preference_rank):
        self.name = name
        self.preference_rank = preference_rank
        self.coins = []

    def in_exchange(self, coin):
        if self.name in coin.exchanges:
            self.coins.append(coin.name)


def get_coins(quantity):
    market = coinmarketcap.Market()
    coins = market.ticker(start=0, limit=quantity)

    return [Coin(coin['id'],
                 coin['name'],
                 coin['rank'],
                 coin['symbol']) for coin in coins]


def get_prefered_exchanges(prefered):
    exchanges = []
    for rank, exchange in enumerate(prefered):
        exchanges.append(Exchange(exchange, rank + 1))

    return exchanges


def to_json(items, file_name, coins=True):
    as_dicts =[]
    for item in items:
        as_dict = item.__dict__
        if coins:
            as_dict.pop('id')

        as_dicts.append(as_dict)

    with open(file_name, 'w') as fp:
        json.dump(as_dicts, fp)

    return


@click.command()
def main():
    num_coins = click.prompt('How many Cryptos would you like to buy?', type=int)
    prefered = click.prompt('List your prefered exchanges in order, seperate with a space')
    prefered = prefered.lower().split()

    print('Getting coins...')
    coins = get_coins(num_coins)

    print('Writing coin data to coins.json')
    to_json(coins, 'coins.json')

    prefered_exchanges = get_prefered_exchanges(prefered)
    for coin in coins:
        for exchange in prefered_exchanges:
            exchange.in_exchange(coin)

    for rank, exchange in enumerate(prefered_exchanges):
        if rank > 0:
            for coin in prefered_exchanges[rank - 1].coins:
                if coin in exchange.coins:
                    exchange.coins.remove(coin)

    print('Writing prefered exchange data to prefered.json')
    to_json(prefered_exchanges, 'prefered.json', coins=False)

    return


if __name__ == '__main__':
    main()
