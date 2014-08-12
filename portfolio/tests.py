from decimal import Decimal

from django.test import TestCase

from .models import Stock, Account, Order, BUY, SELL, HoldingStock
from .exceptions import (
    CannotFindStockException, EmptySymbolException, NotEnoughStockInHands,
    NotEnoughFundExceptin, NotEnoughStockInMarket)


VALID_JSON = {
    "sector": "Capital Goods",
    "yearlow": "8.82",
    "pricedaychange": "0.08",
    "price": "16.68000",
    "volume": "17711536",
    "daylow": "9.97000",
    "peratio": "10.51",
    "ask": "16.68000",
    "marketcap": "66.593B",
    "yearhigh": "18.23000",
    "dayhigh": "18.23000",
    "priceclose": "17.09",
    "bid": "16.67000",
    "name": "Ford Motor Company",
    "asksize": "22",
    "industry": "Auto Manufacturing",
    "exchange": "NYSE",
    "eps": None,
    "epsdiluted": "1.626",
    "pricepercentchange": "0.47",
    "priceopen": "17.17",
    "bidsize": "6",
    "symbol": "F"
}


NOT_FOUND_JSON = {
    "status": "error",
    "msg": "Symbol not found"
}


EMPTY_JSON = {
    "message": "404: Not Found"
}


class StockTestCase(TestCase):
    def test_valid_json(self):
        stock = Stock.get_stock_from_json(VALID_JSON)
        self.assertEqual(stock.symbol, VALID_JSON['symbol'])
        self.assertEqual(stock.name, VALID_JSON['name'])
        self.assertEqual(stock.industry, VALID_JSON['industry'])
        self.assertEqual(stock.exchange, VALID_JSON['exchange'])

    def test_bad_json(self):
        with self.assertRaises(EmptySymbolException):
            Stock.get_stock_from_json(EMPTY_JSON)

        with self.assertRaises(CannotFindStockException):
            Stock.get_stock_from_json(NOT_FOUND_JSON)


class OrderTestCase(TestCase):
    def setUp(self):
        self.account = Account.objects.create(username='test')
        self.stock = Stock.get_stock_from_json(VALID_JSON)

    def test_order(self):
        price = Decimal(VALID_JSON['ask'])
        quantity = 1

        # if we don't have enough money
        self.account.amount = Decimal(1.0)
        self.account.save()
        with self.assertRaises(NotEnoughFundExceptin):
            self.account.buy(self.stock, 1, price, VALID_JSON)

        # not we get some money
        self.account.amount = Decimal(100000.0)
        self.account.save()

        # if we buy more stocks than we can get from the market
        # we expect NotEnoughStockInMarket
        with self.assertRaises(NotEnoughStockInMarket):
            self.account.buy(self.stock, 100000, price, VALID_JSON)

        # if we only buy one, that's ok
        # however in real life,
        # it's not wise at all considering the commission fee
        self.account.buy(self.stock, quantity, price, VALID_JSON)

        account = Account.objects.get(id=self.account.id)
        self.assertEquals(
            account.amount,
            Decimal(100000.0) - price * quantity)

        # meanwhile, we have Order in our db
        # and most importantly, Stock in our hands
        self.assertEquals(
            Order.objects.filter(account=account, type=BUY).count(),
            1)
        self.assertEquals(
            HoldingStock.objects.filter(account=account).count(),
            1)

        # what if I buy the same stock again?
        self.account.buy(self.stock, quantity, price, VALID_JSON)

        account = Account.objects.get(id=self.account.id)
        self.assertEquals(
            account.amount,
            Decimal(100000.0) - price * quantity * 2)

        self.assertEquals(
            Order.objects.filter(account=account, type=BUY).count(),
            2)
        self.assertEquals(
            HoldingStock.objects.filter(account=account).count(),
            2)

        # now we start to sell
        price = Decimal(VALID_JSON['bid'])
        # we do not have enough stock to sell
        with self.assertRaises(NotEnoughStockInHands):
            self.account.sell(self.stock, 3, price, VALID_JSON)

        account.sell(self.stock, 1, price, VALID_JSON)
        self.assertEquals(
            Order.objects.filter(account=account, type=SELL).count(),
            1)
        self.assertEquals(
            HoldingStock.objects.filter(account=account).count(),
            1)

        # we sell the last one
        self.account.sell(self.stock, 1, price, VALID_JSON)

        # we don't have this stock any more
        with self.assertRaises(NotEnoughStockInHands):
            self.account.sell(self.stock, 1, price, VALID_JSON)
