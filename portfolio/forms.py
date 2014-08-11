from django import forms
from django.core.validators import RegexValidator


class LoginForm(forms.Form):
    username = forms.CharField(
        min_length=3,
        max_length=32,
        validators=[RegexValidator(
            regex=r'\w+', message='Only a-zA-Z0-9_ allowed in username')])
