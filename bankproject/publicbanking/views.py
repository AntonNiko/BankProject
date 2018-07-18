from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render

from .forms import LoginForm

from .models import Account
from .models import Transaction

# Create your views here.
def index(request):
    accounts = Account.objects.all()
    context = {"accounts": accounts}
    return render(request, "publicbanking/index.html", context)

def accounts_default(request):
    return render(request, "publicbanking/accounts.html")

def accounts(request, account_number):
    context = {"account_number": account_number}
    return render(request, "publicbanking/account.html", context)

def transactions(request):
    return HttpResponse("This is the <h1>page</h1> that displays each eaccount's transaction history")

def transactions_specific(request, request_id):
    try:
        transaction = Transaction.get(transaction_id = request_id)
    except Transaction.DoesNotExist:
        raise Http404("Transaction is not found")
    return HttpResponse("Lol")

## Login request
def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            return HttpResponse("Logged in")
    return HttpResponse("Failed to login")



