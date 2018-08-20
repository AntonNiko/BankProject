"""
View file used to direct requests to publicbanking/. Follows Django's guidelines in terms
of providing functions to process requests sent by the browser. Contains functions that process
both GET and POST requests.

"""
from django import forms
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone

from .forms import LoginForm, RequestForm
from .models import Account, Transaction, AccountType, WireTransaction
from .utils import *

from decimal import Decimal
import random, re

INTERNET_TRANSFER_MIN_ID = 1000000
INTERNET_TRANSFER_MAX_ID = 9999999
WIRE_TRANSFER_MIN_ID = 100000000
WIRE_TRANSFER_MAX_ID = 199999999

INTERNET_TRANSFER = 0
WIRE_TRANSFER = 1

# Create your views here.
def index(request):
    """
    Handles requests to /publicbanking/, by displaying a standard login page, or redirects
    the user to the accounts page if they are already logged in to the website

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): Django request
    Returns:
        render (django.http.response.HttpResponse): Django Http Request for the login page of /publicbanking/
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

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): Django request
    Returns:
        render (django.http.response.HttpResponse): Django Http Request for the /publicbanking/accounts/ view
    """
    
    ## If user has not been authenticated, redirect
    if not request.user.is_authenticated:
        return redirect("/publicbanking/")
    
    ## Finds the account holder's name related to the card used for the login, and logouts the user if either, the username
    ## (card number) is not a number, or the account search results in no matches found
    try:
        account_holder = Account.objects.filter(account_card = int(request.user.username))[0].account_holder
    except ValueError:
        logout(request)
        return redirect("/publicbanking/")
    except Account.DoesNotExist:
        logout(request)
        return redirect("/publicbanking/")
    
    ## Finds all accounts associated with the card's account holder, to display in transfer request form
    account_choices = list(Account.objects.filter(account_holder = account_holder)) 
    ## Transfer request form to display to user, to transfer money between accounts
    request_form = RequestForm()
    accounts = fetch_accounts(request.user.username)
    balance = fetch_totalBalance(request.user.username)

    context = {"accounts":accounts, "account_choices":account_choices, "total_balance":balance, "request_form":request_form, "account_holder":account_holder}
    return render(request, "publicbanking/accounts_overview.html", context)

def account(request, num):
    """
    Handles requests to /publicbanking/accounts/<accountnum>. <accountnum> specifies an
    account owned by the user who is logged in. If the account number holder does not match
    with the logged in user, redirect them to /publicbanking/ to login. Displays information including: balance, transit number, account number, and a history of
    transactions related to that account

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): Django request
        num (int): Account number
    Returns:
        render (django.http.response.HttpResponse): Django Http Request for the /publicbanking/account/<accountnum> view
    """
    ## If not logged in, redirect to /publicbanking/ for login
    if not request.user.is_authenticated:
        return redirect("/publicbanking/")
    ## If the user's card number does not match the card number associated with the account
    ## being requested, redirect to /publicbanking/ for login
    if request.user.username != str(Account.objects.get(account_number=num).account_card):
        return redirect("/publicbanking/")

    account = fetch_account(num)
    account_type = fetch_account_type(account["account_number"])
    ## Similar process to find transactions related to account
    transactions = fetch_accountTransactions(num)
    context = {"account": account, "transactions": transactions, "account_type": account_type}
    return render(request, "publicbanking/account.html", context)

def wire_transfers(request):
    """
    Handles requests to /publicbanking/wire_transfers, by displaying a page which allows the user to
    request a wire transfer after inputting all the necessary information into the form fields provided.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): Django request
    Returns:
        request (django.http.response.HttpResponse: Django Http Request for the /publicbanking/wire_transfer view

    """
    if not request.user.is_authenticated:
        return redirect("/publicbanking/")

    ## Finds the account holder's name related to the card used for the login, and logouts the user if either, the username
    ## (card number) is not a number, or the account search results in no matches found
    try:
        account_holder = Account.objects.filter(account_card = int(request.user.username))[0].account_holder
    except ValueError:
        logout(request)
        return redirect("/publicbanking/")
    except Account.DoesNotExist:
        logout(request)
        return redirect("/publicbanking/")

    ## Finds all accounts associated with the card's account holder, to display in transfer request form
    account_choices = list(Account.objects.filter(account_holder = account_holder)) 
    
    context = {"account_choices":account_choices}
    return render(request, "publicbanking/wire_transfers.html", context)


def transfer_request(request):
    """
    Handles POST requests to /publicbanking/transfer_request. Processes logged in users' requests
    to transfer money between one of their accounts. If successful, redirects them to /publicbanking/
    accounts

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): Django request
    Returns:
        redirect (django.http.response.HttpResponse): Django Http Redirect Request for the /publicbanking/account/<accountnum> view
    """
    ## Request method for transfer_request must be POST, consistent with a form being submitted
    ## TODO: Validate user and origin account
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

    ## Checks that both the origin and destination accounts are both owned by the logged in user
    if not validate_transfer_user(request, request_origin, request_destination):
        logout(request)
        return redirect("/publicbanking/")

    ## If origin and destinationa accounts are the same, cancel the transfer and redirect
    if request_origin == request_destination:
        messages.add_message(request, messages.WARNING, "Origin and Destination accounts cannot be the same")
        return redirect("/publicbanking/accounts")

    ## Finds the origin and destination account objects for the transaction object,
    ## and update balances
    account_origin = Account.objects.get(account_number=request_origin)
    account_destination = Account.objects.get(account_number=request_destination)

    ## If insufficient funds in origin account, redirect
    if (float(account_origin.account_balance) - float(request_amount)) < 0:
        messages.add_message(request, messages.WARNING, "Insufficient funds in origin account for transfer")
        return redirect("/publicbanking/accounts/")

    ## Create transaction ID
    id_num=random.randint(INTERNET_TRANSFER_MIN_ID, INTERNET_TRANSFER_MAX_ID)
    ## Process transaction
    transaction = Transaction.objects.create(transaction_id=id_num,
                              transaction_amount = request_amount,
                              transaction_time = timezone.now(),
                              transaction_name = "Internet Banking INTERNET TRANSFER {}".format(id_num),
                              transaction_origin_balance = account_origin.account_balance - Decimal(request_amount),
                              transaction_destination_balance = account_destination.account_balance + Decimal(request_amount))
    transaction.save()
    transaction.transaction_origin.add(account_origin)
    transaction.transaction_destination.add(account_destination)

    ## Update balances, and save the objects to their databases
    account_origin.account_balance = account_origin.account_balance - Decimal(request_amount)
    account_origin.save()
    account_destination.account_balance = account_destination.account_balance + Decimal(request_amount)
    account_destination.save()
    
    return redirect("/publicbanking/accounts")


def currency_exchange(request):
    """
    Handles requests to /publicbanking/currency_exchange, by displaying a page that allows the user
    to search a specific currency and input data that allows the user to view the results of calculations,
    and how much it will cost the customer to request such a currency exchange.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): Django request
    Returns:
        render (django.http.response.HttpResponse): Django Http Request for the /publicbanking/wire_transfers view

    """
    if not request.user.is_authenticated:
        return redirect("/publicbanking/")

    ## Finds the account holder's name related to the card used for the login, and logouts the user if either, the username
    ## (card number) is not a number, or the account search results in no matches found
    try:
        account_holder = Account.objects.filter(account_card = int(request.user.username))[0].account_holder
    except ValueError:
        logout(request)
        return redirect("/publicbanking/")
    except Account.DoesNotExist:
        logout(request)
        return redirect("/publicbanking/")

    ## Finds all accounts associated with the card's account holder, to display in transfer request form
    account_choices = list(Account.objects.filter(account_holder = account_holder))
    currencies = ["AUD","CAD","CHF","EUR","GBP","JPY","NZD","USD"]

    
    context = {"account_choices":account_choices, "currencies":currencies}
    return render(request, "publicbanking/currency_exchange.html", context)

def wire_transfer_request(request):
    """
    Handles requests to /publicbanking/wire_transfer_request/, which is deisgned to be a POST request for a
    wire transfer request, and to a destination account to another institution. Creates a transaction object
    which keeps track of originating account balance, and of which the destination is a buffer account for processing.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): Django request
    Returns:
        redirect (django.http.response.HttpResponse): Django Http Request for the /publicbanking/wire_transfers view


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
    request_instNum = post_data["request_instNum"]
    request_routingNum = post_data["request_routingNum"]
    request_accountNum = post_data["request_accountNum"]
    request_bankaddress = post_data["request_bankaddress"]
    request_name = post_data["request_name"]
    request_address = post_data["request_address"]


    ## Finds the origin account object for the wire transaction object, and update balances
    account_origin = Account.objects.get(account_number=request_origin)
    ## Create transaction ID
    id_num=random.randint(WIRE_TRANSFER_MIN_ID, WIRE_TRANSFER_MAX_ID)
    wire_transaction = WireTransaction.objects.create(transaction_id=id_num,
                                                      transaction_amount = request_amount,
                                                      transaction_time = timezone.now(),
                                                      transaction_name = "Internet Banking WIRE TRANSFER {}".format(id_num),
                                                      transaction_origin_balance = account_origin.account_balance - Decimal(request_amount),
                                                      transaction_destination_instNum = request_instNum,
                                                      transaction_destination_routingNum = request_routingNum,
                                                      transaction_destination_bankAddress = request_bankaddress,
                                                      transaction_destination_accountNum = request_accountNum,
                                                      transaction_destination_recipient_name = request_name,
                                                      transaction_destination_recipient_address = request_address
                                                      )                                  
    wire_transaction.save()
    wire_transaction.transaction_origin.add(account_origin)

    ## Update balances, and save the objects to their databases
    account_origin.account_balance = account_origin.account_balance - Decimal(request_amount)
    account_origin.save()
    return redirect("/publicbanking/accounts/")

def transaction_info_request(request, num):
    """
    Handles GET requests to /publicbanking/transaction_info_request/<int:num>, and returns a JsonResponse
    objet which contains information about the requested transaction. Assumes the user has been authenticated
    previously, and is calling this function legitimately.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): Django request
        num (int): Transaction id requested
    Returns:
        redirect (django.http.response.HttpResponse): Redirect HttpResponse object in case the request cannot be completed
        JsonResponse (django.http.response.JsonResponse): Response that returns transaction information on request submitted
    """
    if request.method != "GET":
        return redirect("/publicbanking/")

    
    if num>=INTERNET_TRANSFER_MIN_ID and num<=INTERNET_TRANSFER_MAX_ID:
        transaction_type = INTERNET_TRANSFER
    elif num>=WIRE_TRANSFER_MIN_ID and num<=WIRE_TRANSFER_MIN_ID:
        transaction_type = WIRE_TRANSFER
    else:
        transaction_type = None
        

    ## TODO: Ensure non-authenticated users are redirected
    response = {}
    if transaction_type == INTERNET_TRANSFER:
        transaction = Transaction.objects.get(transaction_id=num)
        response = {"transaction_id": transaction.transaction_id,
            "transaction_amount": transaction.transaction_amount,
            "transaction_time": transaction.transaction_time,
            "transaction_name": transaction.transaction_name,
            "transaction_origin": list(transaction.transaction_origin.all())[0].account_number,
            "transaction_destination": list(transaction.transaction_destination.all())[0].account_number,
            "transaction_origin_balance": transaction.transaction_origin_balance,
            "transaction_destination_balance": transaction.transaction_destination_balance
            } 
    elif transaction_type == WIRE_TRANSFER:
        transaction = WireTransaction.objects.get(transaction_id=num)
        response = {"transaction_id": transaction.transaction_id,
                    "transaction_amount": transaction.transaction_amount,
                    "transaction_time": transaction.transaction_time,
                    "transaction_name": transaction.transaction_name,
                    "transaction_origin": transaction.transaction_origin,
                    "transaction_origin_balance": transaction.transaction_origin_balance}
    else:
        pass
            
    return JsonResponse(response)

def currency_exchange_request(request):
    pass


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
    ## If the card number contains any non-number entry, redirect back to login page with message
    if re.search("[a-zA-Z]", post_data["card_number"]):
        ## Append error message to request in order to show user
        messages.add_message(request, messages.ERROR, "Invalid Card Number")
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
        ## Append error message to request in order to show user in case no matches found in database
        messages.add_message(request, messages.ERROR, """No accounts founds under current login. If you
                             feel that this is not correct, please contact us as soon as possible so we
                             can help you out.""")
        return redirect("/publicbanking/")

def logout_user(request):
    """
    Processes logout requests for the website. Once the user is logged out, redirect them to the
    login page.
    """
    ## Redirect user if not POST, since consistent with a form submission
    if request.method != "POST":
        return redirect("/publicbanking/")
    
    logout(request)
    return redirect("/publicbanking/")

def error_403_view(request, exception):
    """
    Handle any 400 Http status codes by displaying a page that provides information on the error in a
    style consistent with the rest of the website.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): Django request
        exception (django.urls.exceptions.Resolver404): Exception that is raised in case no view is provided
    Returns:
        render (django.http.response.HttpResponse): Django Http request to display 404 error page
    
    """
    context = {}
    return render(request, "publicbanking/error_403_view.html", context)

def error_404_view(request, exception):
    """
    Handle any 400 Http status codes by displaying a page that provides information on the error in a
    style consistent with the rest of the website.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): Django request
        exception (django.urls.exceptions.Resolver404): Exception that is raised in case no view is provided
    Returns:
        render (django.http.response.HttpResponse): Django Http request to display 404 error page
    
    """
    context = {}
    return render(request, "publicbanking/error_400_view.html", context)

def error_500_view(request, exception):
    """
    Handle any 500 Http status codes by displaying a page that provides information on the error in a
    style consistent with the rest of the website.

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): Django request
        exception ???
    Returns:
        render (django.http.response.HttpResponse): Django Http request to display 500 error page
    
    """
    context = {}
    return render(request, "publicbanking/error_500_view.html", context)

