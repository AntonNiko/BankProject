from django import forms

class LoginForm(forms.Form):
    card_number = forms.CharField(label="Card Number", max_length=20)
    card_password = forms.CharField(widget=forms.PasswordInput(), label="Password", max_length=50)
