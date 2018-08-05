from django.contrib.auth import login, logout
from django.contrib.auth import authenticate
from django.http import Http404, HttpResponse
from django.db.models import Q
from django.shortcuts import render, redirect
from django.utils import timezone
from django import forms

from .forms import LoginForm, RequestForm
from .models import Account, Transaction, AccountType

from decimal import Decimal
import random, re

# Create your views here.
def index(request):
    """
    Handles requests to /publicbanking/, by displaying a standard login page, or redirects
    the user to the accounts page if they are already logged in to the website
    """
    ## If user has been authenticated already, redirect
    if request.user.is_authenticated:
        return redirect("/publicbanking/accounts")
    if request.COOKIES.get("card_number") is not None:
        card_remember = request.COOKIES.get("card_number")
    else:
        card_remember = ""

    ## Login form to display when page loads
    login_form = LoginForm()
    context = {"login_form": login_form, "card_remember": card_remember}
    return render(request, "publicbanking/index.html", context)

def accounts_overview(request):
    """
    Handles requests to /publicbanking/accounts, by displaying a summary of each account
    associated to the card holder. Page includes a transfer request form. If user is not
    logged in, then redirect to /publicbanking/ to login
    """
    
    ## If user has not been authenticated, redirect
    if not request.user.is_authenticated:
        return redirect("/publicbanking/")

    ## Finds the account holder's name related to the card used for the login
    card_account_holder = Account.objects.filter(account_card = int(request.user.username))[0].account_holder
    ## Finds all accounts associated with the card's account holder, to display in transfer request form
    account_holder_accounts = list(Account.objects.filter(account_holder = card_account_holder)) 
    
    ## Transfer request form to display to user, to transfer money between accounts
    request_form = RequestForm()
    ## Finds all accounts associated with the account holder's card to display
    accounts = Account.objects.filter(account_card=request.user.username)
    ## Set account details in a list, such that every piece of information can be used
    accounts_modified = []
    balance = 0
    for i in range(len(accounts)):
        accounts_modified.append({})
        accounts_modified[i]["account_holder"] = accounts[i].account_holder
        accounts_modified[i]["account_transitNum"] = accounts[i].account_transitNum
        accounts_modified[i]["account_instNum"] = accounts[i].account_instNum
        accounts_modified[i]["account_number"] = accounts[i].account_number
        accounts_modified[i]["account_type"] = list(accounts[i].account_type.values_list("account_type_name", flat=True))[0]
        accounts_modified[i]["account_balance"] = accounts[i].account_balance
        accounts_modified[i]["account_card"] = accounts[i].account_card
        balance+=accounts[i].account_balance

    context = {"accounts":accounts_modified, "total_balance":balance, "request_form":request_form, "account_choices":account_holder_accounts, "account_holder":card_account_holder}
    return render(request, "publicbanking/accounts_overview.html", context)

def account(request, num):
    """
    Handles requests to /publicbanking/accounts/<accountnum>. <accountnum> specifies an
    account owned by the user who is logged in. If the account number holder does not match
    with the logged in user, redirect them to /publicbanking/ to login.

    Displays information including: balance, transit number, account number, and a history of
    transactions related to that account
    """
    ## If not logged in, redirect to /publicbanking/ for login
    if not request.user.is_authenticated:
        return redirect("/publicbanking/")
    ## If the user's card number does not match the card number associated with the account
    ## being requested, redirect to /publicbanking/ for login
    if request.user.username != str(Account.objects.get(account_number=num).account_card):
        return redirect("/publicbanking/")

    ## If no accounts are found, continue and display blank page
    try:
        account = Account.objects.get(account_number=num)
    except Account.DoesNotExist:
        account = None
    ## Similar process to find transactions related to account
    try:
        transactions = Transaction.objects.filter(Q(transaction_origin=Account.objects.get(account_number=num)) | Q(transaction_destination=Account.objects.get(account_number=num)))
    except Transaction.DoesNotExist:
        transactions = []

    ## Modify transactions variable to display account numbers in place of QuerySet. Allows
    ## the page to display useful information including amount transferred, time, origin, and
    ## destination
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
    """
    Handles POST requests to /publicbanking/transfer_request. Processes logged in users' requests
    to transfer money between one of their accounts. If successful, redirects them to /publicbanking/
    accounts
    """
    ## Request method for transfer_request must be POST, consistent with a form being submitted
    if request.method != "POST":
        return redirect("/publicbanking/accounts")
    if not request.user.is_authenticated:
        return redirect("/publicbanking/")

    ## Fetch information that was submitted with the form, but not as part of the Django
    ## Form object. (This was necessary to avoid displaying no accounts to transfer from
    ## in the form)
    post_data = dict(request.POST.items())
    request_amount = post_data["request_amount"]
    request_origin = post_data["request_origin"]
    request_destination = post_data["request_destination"]
    request_frequency = post_data["request_frequency"]

    ## If origin and destinationa accounts are the same, cancel the transfer and redirect
    if request_origin == request_destination:
        return redirect("/publicbanking/accounts")

    ## Finds the origin and destination account objects for the transaction object,
    ## and update balances
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

    ## Update balances, and save the objects to their databases
    account_origin.account_balance = account_origin.account_balance - Decimal(request_amount)
    account_origin.save()
    account_destination.account_balance = account_destination.account_balance + Decimal(request_amount)
    account_destination.save()
    
    return redirect("/publicbanking/accounts")

## Login request (no HTML code visual)
def login_user(request):
    """
    Handles POST requests to /publicbanking/login_user/. Processes login requests from the form
    LoginForm to authenticate a user with their card number and password. If login is invalid,
    redirect them to the login page again.
    """
    ## Redirect user if not POST, since consistent with a form submission
    if request.method != "POST":
        return redirect("/publicbanking/")

    ## Fetch the information sent by the login form, in the POST request
    post_data = dict(request.POST.items())
    ## If the card number contains any non-number entry, redirect back to login page
    if re.search("[a-zA-Z]", post_data["card_number"]):
        print("Letter found...")
        return redirect("/publicbanking/")
    
    card_number = post_data["card_number"]
    card_password = post_data["card_password"]
    try:
        card_remember = post_data["remember_card"]
    except KeyError:
        card_remember = None

    ## Authenticate user details
    user = authenticate(request, username=card_number, password=card_password)
    if user is not None:
        ## Successful authentication, and login user to access their accounts
        login(request, user)
        response = redirect("/publicbanking/accounts")
        if card_remember is not None:
            response.set_cookie("card_number", request.user.username, max_age=30)
        return response
    else:
        return redirect("/publicbanking/")

def logout_user(request):
    """
    Processes logout requests for the website. Once the user is logged out, redirect them to the
    login page.
    """
    ## TODO: only process POST requests
    logout(request)
    return redirect("/publicbanking/")

