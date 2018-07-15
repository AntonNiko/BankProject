from django.http import HttpResponse

from .models import Account
from .models import Transaction

# Create your views here.
def index(request):
    return HttpResponse("This is the home page for client's public banking")

def accounts_default(request):
    return HttpResponse("This is the page that displays default account details w/ specific url")

def accounts(request, account_number):
    return HttpResponse("This is the page that displays each account's details \n {}".format(account_number))

def transactions(request):
    return HttpResponse("This is the page that displays each eaccount's transaction history")

def login(request):
    return HttpResponse("This is the page that enables clients to authenticate themselves and access their accounts")



