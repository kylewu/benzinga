from decimal import Decimal

from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings

from .utils import lookup as benzinga_lookup
from .forms import LoginForm
from .decorators import login_required, stock_decorator
from .models import Stock, HoldingStock, Account, Order


def login(request):
    # to make this portfolio simple
    # we use session to keep login information
    form = LoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        request.session['username'] = form.cleaned_data['username']

        Account.objects.get_or_create(username=request.session['username'])

        return redirect('portfolio.views.index')

    return render(request, 'portfolio/login.html', {'form': form})


@login_required
def index(request):
    holding_stocks = HoldingStock.objects.filter(account=request.account).order_by('stock__symbol')

    context = {'holding_stocks': holding_stocks}

    if 'symbol' in request.GET:
        symbol = request.GET['symbol']
        json = benzinga_lookup(symbol)
        stock = Stock.get_stock_from_json(json)
        context['stock'] = stock
        context['bid_price'] = json['bid']
        context['bid_size'] = json['bidsize']
        context['ask_price'] = json['ask']
        context['ask_size'] = json['asksize']
    else:
        stock = None

    return render(request, 'portfolio/index.html', context)


@login_required
def logout(request):
    request.session.pop('username', '')
    return redirect('portfolio.views.login')


@login_required
def reset(request):
    # delete all Account related data
    Order.objects.filter(account=request.account).delete()
    HoldingStock.objects.filter(account=request.account).delete()
    request.account.amount = settings.INIT_CACHE
    request.account.save()
    return logout(request)


@login_required
@stock_decorator
def buy(request, stock, quantity, price, json):
    quantity = int(quantity)
    price = Decimal(price)

    request.account.buy(stock, quantity, price, json)
    messages.success(request, 'Successfully buy {0} {1} at ${2}'.format(quantity, stock.symbol, price))
    return redirect('portfolio.views.index')


@login_required
@stock_decorator
def sell(request, stock, quantity, price, json):
    quantity = int(quantity)
    price = Decimal(price)

    request.account.sell(stock, quantity, price, json)
    messages.success(request, 'Successfully sell {0} {1} at ${2}'.format(quantity, stock.symbol, price))
    return redirect('portfolio.views.index')
