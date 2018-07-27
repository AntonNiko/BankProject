from django.contrib.auth import login, logout
from django.contrib.auth import authenticate
from django.http import Http404, HttpResponse
from django.db.models import Q
from django.shortcuts import render, redirect
from django.utils import timezone

from .forms import LoginForm, RequestForm
from .models import Account, Transaction

from datetime import datetime
from decimal import Decimal

import random

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

    request_form = RequestForm()
    accounts = Account.objects.filter(account_card=request.user.username)
    context = {"accounts":accounts, "request_form":request_form}
    return render(request, "publicbanking/accounts_overview.html", context)

def account(request,num):
    if not request.user.is_authenticated:
        return redirect("/publicbanking/")
    if request.user.username != str(Account.objects.get(account_number=num).account_card):
        return redirect("/publicbanking/")
    
    try:
        account = Account.objects.get(account_number=num)
    except Account.DoesNotExist:
        account = None
    try:
        transactions = Transaction.objects.filter(Q(transaction_origin=num) | Q(transaction_destination=num))
    except Transaction.DoesNotExist:
        transactions = [] 

    context = {"account": account, "transactions": transactions}
    return render(request, "publicbanking/account.html", context)


def transfer_request(request):
    if request.method != "POST":
        return redirect("/publicbanking/accounts")
    if not request.user.is_authenticated:
        return redirect("/publicbanking")

    form = RequestForm(request.POST)
    if not form.is_valid():
        return redirect("/publicbanking")
    
    request_amount = form.cleaned_data["request_amount"]
    request_origin = form.cleaned_data["request_origin"]
    request_destination = form.cleaned_data["request_destination"]
    request_frequency = form.cleaned_data["request_frequency"]

    ## Process transaction
    transaction = Transaction(transaction_id=random.randrange(5),
                              transaction_amount = request_amount,
                              transaction_time = timezone.now(),
                              transaction_name = "Internet Transfer - Test",
                              transaction_origin = request_origin,
                              transaction_destination = request_destination)

    account_origin = Account.objects.get(account_number=request_origin)
    account_destination = Account.objects.get(account_number=request_destination)

    account_origin.account_balance = account_origin.account_balance - Decimal(request_amount)
    account_origin.save()
    account_destination.account_balance = account_destination.account_balance - Decimal(request_amount)
    account_destination.save()
    
    ## Adjust balance for respective accounts
    transaction.save()
    
    return HttpResponse("This page is where all online transfer requests will be processed")

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

