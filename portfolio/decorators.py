from functools import wraps
from urllib import urlencode

from requests.exceptions import Timeout

from django.contrib import messages
from django.shortcuts import redirect

from .models import Account, Stock
from .utils import lookup as benzinga_lookup
from .exceptions import EmptySymbolException, CannotFindStockException


def login_required(view_func):
    """
    Redirects to login page if user is not login
    """

    @wraps(view_func)
    def func(request, *args, **kwargs):
        if 'username' not in request.session:
            return redirect('portfolio.views.login')

        # to make this project simple
        # we do not save Account instance in context processor
        try:
            request.account = Account.objects.get(
                username=request.session['username'])
        except Account.DoesNotExist:
            pass

        return view_func(request, *args, **kwargs)

    return func


def stock_decorator(view_func):
    """
    Gets or crates Stock instance based on symbol in kwargs
    then passes it to view_func
    """
    @wraps(view_func)
    def func(request, *args, **kwargs):
        symbol = kwargs.pop('symbol')

        if symbol:
            try:
                json = benzinga_lookup(symbol)
            except Timeout:
                messages.error(request, u'Cannot connect to Benzinga.')
                raise

            try:
                stock = Stock.get_stock_from_json(json)
            except CannotFindStockException as e:
                messages.warning(request, str(e))
                raise
            except EmptySymbolException as e:
                messages.warning(request, str(e))
                raise

            kwargs['stock'] = stock
            kwargs['json'] = json

            return view_func(request, *args, **kwargs)

    return func
