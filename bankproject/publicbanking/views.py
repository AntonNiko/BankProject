from django.contrib.auth import login, logout
from django.contrib.auth import authenticate
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect

from .forms import LoginForm

from .models import Account
from .models import Transaction

# Create your views here.
def index(request):
    login_form = LoginForm()
    context = {"login_form": login_form}
    return render(request, "publicbanking/index.html", context)

def accounts_overview(request):
    if not request.user.is_authenticated:
        redirect("/publicbanking/", permament=True)
    
    accounts = Account.objects.filter(account_card=request.user.username)
    context = {"accounts":accounts}
    return render(request, "publicbanking/accounts_overview.html", context)

def accounts(request, account_number):
    if not request.user.is_authenticated:
        redirect("/publicbanking/", permament=True)
    if request.user.username != Account.objects.get(account_number=4570681).account_card:
        redirect("/publicbanking/", permanent=True)

    ## Fetch all transactions relating to account number
    try:
        transactions_debit = Transaction.objects.filter(transaction_origin=account_number)
    except Transaction.DoesNotExist:
        transactions_debit = []
    try:
        transactions_credit = Transaction.objects.filter(transaction_destination=account_number)
    except Transaction.DoesNotExist:
        transactions_credit = []
    
    context = {"account_number": account_number, "transactions_debit": transactions_debit, "transactions_credit": transactions_credit}
    return render(request, "publicbanking/account.html", context)

def transactions(request):
    return HttpResponse("This is the <h1>page</h1> that displays each eaccount's transaction history")

def transactions_specific(request, request_id):
    try:
        transaction = Transaction.get(transaction_id = request_id)
    except Transaction.DoesNotExist:
        raise Http404("Transaction is not found")
    return HttpResponse("Lol")

## Login request (no HTML code visual)
def login_user(request):
    if request.method == "POST":
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
    return HttpResponse("Invalid HTTP Login Request")

## Logout request (no HTML code visual)
def logout_user(request):
    logout(request)
    return redirect("/publicbanking/", permanent=True)

        
        

 #a = Account.objects.get(account_number =4506445697840187)

