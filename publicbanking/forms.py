from django import forms

class LoginForm(forms.Form):
    card_number = forms.CharField(label="Card Number", max_length=20)
    card_password = forms.CharField(widget=forms.PasswordInput(), label="Password", max_length=50)

class RequestForm(forms.Form):
    request_amount = forms.FloatField(label="Transfer Amount", max_value=10000.00)
    request_origin = forms.CharField(label="Origin", max_length=20)
    request_destination = forms.CharField(label="Destination", max_length=20)
    request_frequency = forms.ChoiceField(choices=((1,"Once"),(2,"Daily"),(3,"Weekly"),(4,"Monthly")))
    
