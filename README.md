benzinga
========
This app is deployed at [Heroku](http://benzinga-wenbin.herokuapp.com)


NOTES
-----
> We will not be taking the bid and ask sizes into effect and instead will be assuming that there are an infinite amount
> of shares available at the current bid and ask prices.

In this app, bid and ask sizes are taken into effect.

This app contains only the simplest HTML/CSS code because I focus more on backend.
In models.py, you will find some concepts which are very common in stock market.
For example,
* I double check price synced before making an order.
* Every Order is kept in DB (although I don't make use of them now)

I also try to write code in different ways. For example, login form is a Django form while search blank is ony a `<input>` tag.

I follow most styles from pep8, but 80-char length per line. Nowadays we have wider screen so I prefer loosening this
rule.

One env variable is set with command `heroku config:set ON_HEROKU=1`.
In settings.py, there is a flag `ON_HEROKU = 'ON_HEROKU' in os.environ` which can be used to check where am I.


Drawbacks
--------
* poor interface :(
* I do not have a full list of stocks so I create them on the fly.
	This can be improved by initializing with a django command.
* Only one app `portfolio` is created. Normally we should have a better structure, to create `auth` app for example.
* I don't use Django User model. Instead I have a simple session based authentication *system*. It's really simple :p
