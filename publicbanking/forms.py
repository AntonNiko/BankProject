from django import forms
from .models import Account, Transaction

class LoginForm(forms.Form):
    card_number = forms.CharField(label="Card Number", max_length=20)
    card_password = forms.CharField(widget=forms.PasswordInput(), label="Password", max_length=50)

class RequestForm(forms.Form):
    ACCOUNT_CHOICES = None

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(RequestForm, self).__init__(*args, **kwargs)

    def clean(self):
        card_account_holder = Account.objects.get(account_card = int(self.request.user.username)).account_holder



    request_amount = forms.FloatField(label="Transfer Amount", max_value=10000.00)
    ACCOUNT_CHOICES = [[1, ("Not relevant")], 
                       [2, ("Review")],
                       [3, ("Maybe relevant")],
                       [4, ("Relevant")],
                       [5, ("Leading candidate")]]
    request_origin = forms.CharField(label="Origin", max_length=20)
    request_origin = forms.ChoiceField(choices = ACCOUNT_CHOICES)
    request_destination = forms.CharField(label="Destination", max_length=20)
    request_frequency = forms.ChoiceField(choices=((1,"Once"),(2,"Daily"),(3,"Weekly"),(4,"Monthly")))
