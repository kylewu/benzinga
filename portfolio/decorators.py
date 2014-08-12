from functools import wraps

from requests.exceptions import Timeout

from django.contrib import messages
from django.shortcuts import redirect

from .models import Account, Stock
from .utils import lookup as benzinga_lookup
from .exceptions import (
    EmptySymbolException, CannotFindStockException, PriceChangedException,
    NotEnoughStockInMarket, NotEnoughStockInHands, NotEnoughFundExceptin)


def login_required(view_func):

    @wraps(view_func)
    def func(request, *args, **kwargs):
        if 'username' not in request.session:
            return redirect('portfolio.views.login')

        # to make this project simple
        # we do not save Account instance in context processor
        try:
            request.account = Account.objects.get(username=request.session['username'])
        except Account.DoesNotExist:
            pass

        return view_func(request, *args, **kwargs)

    return func


def stock_decorator(view_func):
    @wraps(view_func)
    def func(request, *args, **kwargs):
        symbol = kwargs.pop('symbol')

        try:
            if symbol:
                try:
                    json = benzinga_lookup(symbol)
                except Timeout:
                    messages.error(request, u'Cannot connect to Benzinga.')
                    raise

                try:
                    stock = Stock.get_stock_from_json(json)
                except CannotFindStockException:
                    messages.warning(request, u'Cannot find stock symbol {0}'.format(symbol))
                    raise
                except EmptySymbolException:
                    messages.warning(request, u'Empty symbol is not allowed')
                    raise

                kwargs['stock'] = stock
                kwargs['json'] = json

            try:
                return view_func(request, *args, **kwargs)
            except NotEnoughFundExceptin:
                messages.warning(request, u'You do not have enough money')
                raise
            except NotEnoughStockInHands:
                messages.warning(request, u'You do not have enough stocks')
                raise
            except PriceChangedException:
                messages.warning(request, u'Price changes, please refetch new price')
                raise
            except NotEnoughStockInMarket:
                messages.warning(request, u'There is not enough stocks in the market')
                raise

        except:
            return redirect('portfolio.views.index')

    return func
