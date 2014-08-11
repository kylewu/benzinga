from django.shortcuts import render, redirect

from .forms import LoginForm


def index(request):
    if 'username' not in request.session:
        return redirect('portfolio.views.login')

    # TODO fetch stock data from DB
    return render(request, 'portfolio/index.html')


def login(request):
    # to make this portfolio simple
    # we use session to keep login information
    form = LoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        request.session['username'] = form.cleaned_data['username']
        return redirect('portfolio.views.index')

    return render(request, 'portfolio/login.html', {'form': form})


def logout(request):
    request.session.pop('username', '')
    return redirect('portfolio.views.login')
