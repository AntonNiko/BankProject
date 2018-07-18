from django import forms

class LoginForm(forms.Form):
    card_number = forms.CharField(label="card_number", max_length=100)
