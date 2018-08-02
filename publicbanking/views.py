from django.contrib.auth import login, logout
from django.contrib.auth import authenticate
from django.http import Http404, HttpResponse
from django.db.models import Q
from django.shortcuts import render, redirect
from django.utils import timezone
from django import forms

from .forms import LoginForm, RequestForm
from .models import Account, Transaction

from datetime import datetime
from decimal import Decimal

import random
import json

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return redirect("/publicbanking/accounts")

    login_form = LoginForm()
    context = {"login_form": login_form}
    return render(request, "publicbanking/index.html", context)

def accounts_overview(request):
    if not request.user.is_authenticated:
        return redirect("/publicbanking/")

    account_choices = []
    card_account_holder = Account.objects.filter(account_card = int(request.user.username))[0].account_holder
    account_holder_accounts = list(Account.objects.filter(account_holder = card_account_holder))
    for i in range(len(account_holder_accounts)):
        account_choices.append((account_holder_accounts[i]))

    request_form = RequestForm()
    accounts = Account.objects.filter(account_card=request.user.username)
    context = {"accounts":accounts, "request_form":request_form, "account_choices":account_choices}
    return render(request, "publicbanking/accounts_overview.html", context)

def account(request, num):
    if not request.user.is_authenticated:
        return redirect("/publicbanking/")
    if request.user.username != str(Account.objects.get(account_number=num).account_card):
        return redirect("/publicbanking/")
    
    try:
        account = Account.objects.get(account_number=num)
    except Account.DoesNotExist:
        account = None
    try:
        transactions = Transaction.objects.filter(Q(transaction_origin=Account.objects.get(account_number=num)) | Q(transaction_destination=Account.objects.get(account_number=num)))
    except Transaction.DoesNotExist:
        transactions = []

    ## Modify transactions variable to display account numbers in place of QuerySet
    transactions_modified = []
    for i in range(len(transactions)):
        transactions_modified.append({})
        transactions_modified[i]["transaction_id"] = transactions[i].transaction_id
        transactions_modified[i]["transaction_amount"] = transactions[i].transaction_amount
        transactions_modified[i]["transaction_time"] = transactions[i].transaction_time
        transactions_modified[i]["transaction_name"] = transactions[i].transaction_name
        transactions_modified[i]["transaction_origin"] = list(transactions[i].transaction_origin.all())[0].account_number
        transactions_modified[i]["transaction_destination"] = list(transactions[i].transaction_destination.all())[0].account_number
    context = {"account": account, "transactions": transactions_modified}
    return render(request, "publicbanking/account.html", context)


def transfer_request(request):
    if request.method != "POST":
        return redirect("/publicbanking/accounts")
    if not request.user.is_authenticated:
        return redirect("/publicbanking")

    form = RequestForm(request.POST)
    if not form.is_valid():
        return redirect("/publicbanking")

    post_data = dict(request.POST.items())
    request_amount = form.cleaned_data["request_amount"]
    request_origin = post_data["request_origin"]
    request_destination = post_data["request_destination"]
    request_frequency = form.cleaned_data["request_frequency"]

    account_origin = Account.objects.get(account_number=request_origin)
    account_destination = Account.objects.get(account_number=request_destination)

    ## Process transaction
    transaction = Transaction.objects.create(transaction_id=random.randrange(500),
                              transaction_amount = request_amount,
                              transaction_time = timezone.now(),
                              transaction_name = "Internet Transfer - Test")
    transaction.save()
    transaction.transaction_origin.add(account_origin)
    transaction.transaction_destination.add(account_destination)
    

    account_origin.account_balance = account_origin.account_balance - Decimal(request_amount)
    account_origin.save()
    account_destination.account_balance = account_destination.account_balance - Decimal(request_amount)
    account_destination.save()
    
    ## Adjust balance for respective accounts
    
    return redirect("/publicbanking/accounts")

## Login request (no HTML code visual)
def login_user(request):
    if request.method != "POST":
        return redirect("/publicbanking/")
        
    form = LoginForm(request.POST)
    if form.is_valid():
        card_number = form.cleaned_data["card_number"]
        card_password = form.cleaned_data["card_password"]

        user = authenticate(request, username=card_number, password=card_password)
        if user is not None:
            login(request, user)
            return redirect("/publicbanking/accounts")
        else:
            return HttpResponse("Login failed.")

def logout_user(request):
    logout(request)
    return redirect("/publicbanking/")

