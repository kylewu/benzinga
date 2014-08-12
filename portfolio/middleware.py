from urllib import urlencode

from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import redirect


class StockExceptionMiddleware(object):
    """
    Show error messages in index page
    TODO we should not output all error message
    """
    def process_exception(self, request, exception):
        messages.warning(request, str(exception))
        return redirect('portfolio.views.index')


class GETQueryStringRedirectMiddleware(object):
    """
    If it's a redirect, we carry GET query string to new url
    """
    def process_response(self, request, response):
        if isinstance(response, HttpResponseRedirect) and request.GET:
            response['Location'] += '?' + urlencode(request.GET)
        return response
