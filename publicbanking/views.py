from django.contrib.auth import login, logout
from django.contrib.auth import authenticate
from django.http import Http404, HttpResponse
from django.db.models import Q
from django.shortcuts import render, redirect

from .forms import LoginForm

from .models import Account
from .models import Transaction

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return redirect("/publicbanking/accounts", permanent=True)

    login_form = LoginForm()
    context = {"login_form": login_form}
    return render(request, "publicbanking/index.html", context)

def accounts_overview(request):
    if not request.user.is_authenticated:
        return redirect("/publicbanking/", permament=True)
    
    accounts = Account.objects.filter(account_card=request.user.username)
    context = {"accounts":accounts}
    return render(request, "publicbanking/accounts_overview.html", context)

def accounts(request, number):
    if not request.user.is_authenticated:
        redirect("/publicbanking/", permament=True)
    if request.user.username != Account.objects.get(account_number=number).account_card:
        redirect("/publicbanking/", permanent=True)

    try:
        account = Account.objects.get(account_number=number)
    except Account.DoesNotExist:
        account = None
    try:
        transactions = Transaction.objects.filter(Q(transaction_origin=number) | Q(transaction_destination=number))
    except Transaction.DoesNotExist:
        transactions = []

    context = {"account": account, "transactions": transactions}
    return render(request, "publicbanking/account.html", context)

def transactions_specific(request, request_id):
    try:
        transaction = Transaction.get(transaction_id = request_id)
    except Transaction.DoesNotExist:
        raise Http404("Transaction is not found")
    return HttpResponse("Lol")


def transfer_request(request):
    if request.method != "POST":
        return redirect("/publicbanking/accounts", permanent=True)
    return HttpResponse("This page is where all online transfer requests will be processed")


## Login request (no HTML code visual)
def login_user(request):
    if request.method != "POST":
        return redirect("/publicbanking/", permanent=True)
        
    form = LoginForm(request.POST)
    if form.is_valid():
        card_number = form.cleaned_data["card_number"]
        card_password = form.cleaned_data["card_password"]

        user = authenticate(request, username=card_number, password=card_password)
        if user is not None:
            login(request, user)
            return redirect("/publicbanking/accounts", permanent=True)
        else:
            return HttpResponse("Login failed.")

def logout_user(request):
    logout(request)
    return redirect("/publicbanking/", permanent=True)

