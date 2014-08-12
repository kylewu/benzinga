from django.db import models, transaction
from django.db.models import Sum
from django.conf import settings

from .utils import lookup as benzinga_lookup
from .exceptions import (
    NotEnoughStockInMarket, NotEnoughStockInHands,
    CannotFindStockException, EmptySymbolException, NotEnoughFundExceptin)

BUY = 'B'
SELL = 'S'
ORDER_TYPES = (
    (BUY, 'Buy'),
    (SELL, 'Sell')
)


class Stock(models.Model):
    symbol = models.CharField(max_length=8)
    name = models.CharField(max_length=32)
    industry = models.CharField(max_length=32)
    exchange = models.CharField(max_length=16)  # here we can use choices

    @staticmethod
    def get_stock_from_json(json):
        """
        Create Stock instance if it's not in our db
        and returns it
        """
        if 'status' in json:
            # json is not valid
            raise CannotFindStockException()
        if 'message' in json:
            # json is not valid
            raise EmptySymbolException()

        stock, created = Stock.objects.get_or_create(symbol=json['symbol'])
        if created:
            # we only update stock information when we create a Stock instance
            # if these fields change very often,
            # we should update them in cron jobs maybe
            stock.name = json['name']
            stock.industry = json['industry']
            stock.exchange = json['exchange']
            stock.save()
        return stock


class Account(models.Model):
    """
    A simple user account implementation
    """
    username = models.CharField(max_length=32)
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=settings.INIT_CACHE)

    def __unicode(self):
        return u'{0}: {1}'.format(self.username, self.amount)

    def buy(self, stock, quantity, price, json=None):
        """
        Buy stock
        """
        self._sync(BUY, stock, quantity, price, json=None)

        # first check if we have enough fund to buy
        if quantity * price > self.amount:
            raise NotEnoughFundExceptin()

        with transaction.atomic():
            # create Order log first
            Order.objects.create(
                account=self,
                stock=stock,
                quantity=quantity,
                price=price,
                type=BUY)

            # create new HoldingStock
            HoldingStock.objects.create(
                account=self,
                stock=stock,
                quantity=quantity,
                price=price)

            # finally update amount
            self.amount -= price * quantity
            self.save()

    def sell(self, stock, quantity, price, json=None):
        """
        Sell stock
        """
        self._sync(SELL, stock, quantity, price, json=None)

        # first check if we have enough stock to sell
        sum = HoldingStock.objects.filter(stock=stock).\
            aggregate(Sum('quantity'))['quantity__sum']

        if sum < quantity:
            raise NotEnoughStockInHands()

        with transaction.atomic():
            # create Order log first
            Order.objects.create(
                account=self,
                stock=stock,
                quantity=quantity,
                price=price,
                type=SELL)

            # update HoldingStock
            hss = HoldingStock.objects.filter(stock=stock).order_by('-price')

            for hs in hss:
                if hs.quantity <= quantity:
                    quantity -= hs.quantity
                    hs.delete()
                    break

                hs.quantity = hs.quantity - quantity
                hs.save()

            # finally update amount
            self.amount += price * quantity
            self.save()

    def _sync(self, type, stock, quantity, price, json=None):
        """
        Before buy or sell stock,
        we double check latest price and quantity from Benzinga

        PriceChangedException raises,
            if price is not synced with Benzinga
        NotEnoughStockInMarket raises,
            if there's not enough quantity of stock in specific price

        NOTICE: this behavior is not the same as in real life!
        """
        price_name = {BUY: 'ask', SELL: 'bid'}[type]
        quantity_name = {BUY: 'asksize', SELL: 'bidsize'}[type]

        if json is None:
            json = benzinga_lookup(stock.symbol)

        #if Decimal(json[price_name]) != price:
            #raise PriceChangedException()

        if int(json[quantity_name]) < quantity:
            # not enough stock to provide
            raise NotEnoughStockInMarket()
        return stock


class Order(models.Model):
    """
    Order log of all buy and sell actions
    """
    account = models.ForeignKey('portfolio.Account')
    stock = models.ForeignKey('portfolio.Stock')
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=4)
    created_at = models.DateTimeField(auto_now_add=True)

    type = models.CharField(max_length=1, choices=ORDER_TYPES)


class HoldingStock(models.Model):
    """
    If one user buy the same stock twice with different price,
    we create two instances of `HoldingStock`
    """
    account = models.ForeignKey('portfolio.Account')
    stock = models.ForeignKey('portfolio.Stock')
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=4)
