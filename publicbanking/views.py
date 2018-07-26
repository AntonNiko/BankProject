from django.contrib.auth import login, logout
from django.contrib.auth import authenticate
from django.http import Http404, HttpResponse
from django.db.models import Q
from django.shortcuts import render, redirect

from .forms import LoginForm, RequestForm

from .models import Account
from .models import Transaction

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
    if form.is_valid():
        request_amount = form.cleaned_data["request_amount"]
        request_origin = form.cleaned_data["request_origin"]
        request_destination = form.cleaned_data["request_destination"]
        request_frequency = form.cleaned_data["request_frequency"]
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

