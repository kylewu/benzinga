import requests

BENZINGA_API_URL = 'http://data.benzinga.com/stock/'


def lookup(symbol):
    r = requests.get(BENZINGA_API_URL + symbol)
    return r.json()
