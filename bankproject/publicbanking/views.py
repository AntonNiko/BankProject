from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render
from .models import Account
from .models import Transaction

# Create your views here.
def index(request):
    accounts = Account.objects.all()
    ##template = loader.get_template("publicbanking/index.html")
    context = {"accounts": accounts}
    return render(request, "publicbanking/index.html", context)

def accounts_default(request):
    return HttpResponse("This is the page that displays default account details w/ specific url")

def accounts(request, account_number):
    return HttpResponse("This is the page that displays each account's details \n {}".format(account_number))

def transactions(request):
    return HttpResponse("This is the <h1>page</h1> that displays each eaccount's transaction history")

def transactions_specific(request, request_id):
    try:
        transaction = Transaction.get(transaction_id = request_id)
    except Transaction.DoesNotExist:
        raise Http404("Transaction is not found")
    return HttpResponse("Lol")

def login(request):
    return HttpResponse("This is the page that enables clients to authenticate themselves and access their accounts")



