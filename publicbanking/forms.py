from django import forms
from .models import Account, Transaction

class LoginForm(forms.Form):
    """
    Form used to authenticate users and allow them to access their acocunts.
    """
    card_number = forms.CharField(label="Card Number", max_length=20)
    card_password = forms.CharField(widget=forms.PasswordInput(), label="Password", max_length=50)

class RequestForm(forms.Form):
    """
    Form used to send a user's transfer request to be processed by /publicbanking/
    transfer_request/. Several more fields are added in the html template, as passing
    the account numbers would have been impossible, since querying db returns a QuerySet.
    (may be fixed in later updates)
    """
    request_amount = forms.FloatField(label="Transfer Amount", max_value=10000.00)
    request_frequency = forms.ChoiceField(choices=((1,"Once"),(2,"Daily"),(3,"Weekly"),(4,"Monthly")))
