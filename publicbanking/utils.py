""" 
Provides useful functions to scripts to fetch and return information related to
accounts, transactions, and clients. Also contains functions that can process
various requests such as changing account balances or creating objects. This is
not a complete set of functions as others will be added in the future. 

"""
from .models import Account, Transaction, AccountType, WireTransaction
from django.db.models import Q

def fetch_account(accountNum):
    """
    Function to return the information related to an account number provided as a parameter. This function
    assumes that the user is authenticated and that a previous script ensures that they are sending a
    request to an account they own.

    Args:
        accountNum (int): Account number
    Returns:
        account_modified (dict): Dictionary with keys and fields related to account
    """
    ## Get the account object by using Django's model function .get()
    ## If no accounts are found, a None type will be returned
    try:
        account = Account.objects.get(account_number=accountNum)
    except Account.DoesNotExist:
        account = None

    ## Append the account data to a new dict. M2M field in account_type means
    ## that it has to be converted to a string type to show the user
    account_modified = {}
    account_modified["account_holder"] = account.account_holder
    account_modified["account_transitNum"] = account.account_transitNum
    account_modified["account_instNum"] = account.account_instNum
    account_modified["account_number"] = account.account_number
    account_modified["account_type"] = list(account.account_type.values_list("account_type_name", flat=True))[0]
    account_modified["account_balance"] = account.account_balance
    account_modified["account_card"] = account.account_card
    return account_modified


def fetch_accounts(clientCard):
    """
    Function to return the accounts owned by the account holder that is linked to the bank card they
    used to login into the website, and associated information.

    Args:
        clientCard (int): Bank card used for login
    Returns:
        accounts_modified (list): List with (dict) elements with info about each account
    """
    ## Finds all accounts associated with the account holder's card to display
    accounts = Account.objects.filter(account_card=clientCard)
    accounts_modified = []

    ## For each account found, add a new dict to accounts_modified containing
    ## information related to account. M2M field account_type means that it has
    ## to be converted to a string to show the user
    for i in range(len(accounts)):
        accounts_modified.append({})
        accounts_modified[i]["account_holder"] = accounts[i].account_holder
        accounts_modified[i]["account_transitNum"] = accounts[i].account_transitNum
        accounts_modified[i]["account_instNum"] = accounts[i].account_instNum
        accounts_modified[i]["account_number"] = accounts[i].account_number
        accounts_modified[i]["account_type"] = list(accounts[i].account_type.values_list("account_type_name", flat=True))[0]
        accounts_modified[i]["account_balance"] = accounts[i].account_balance
        accounts_modified[i]["account_card"] = accounts[i].account_card
    return accounts_modified

def fetch_account_type(accountNum):
    """
    Function that returns the accountType object related to the account number that is provided by the
    parameter. Assumes that the user has been validated and is sending a legitimate request that calls
    this function.

    Args:
        accountNum (int): User's account number
    Returns:
        accountType (publicbanking.models.AccountType): Account Type object with information about account's details

    """
    account = Account.objects.filter(account_number=accountNum)
    accountType = list(AccountType.objects.filter(account_type__in=account))[0]
    return accountType

def fetch_accountTransactions(accountNum):
    """
    Function to return all the transaction related to an account number provided as a parameter. This
    function assumes that the user has been previously authenticated and that the request is for an
    account they own.

    Args:
        accountNum (int): User's account number
    Returns:
        transactions_modified (list): A list containing (dict) elements with info about each account,
                                      including wire transfers

    """
    ## Search for any transactions that has originated from or destined to that account. If
    ## no transactions are found, simply return an empty string
    try:
        transactions = Transaction.objects.filter(Q(transaction_origin=Account.objects.get(account_number=accountNum)) | Q(transaction_destination=Account.objects.get(account_number=accountNum)))
    except Transaction.DoesNotExist:
        transactions = []
    ## For each transaction found, add a new dict to transactions_modified to display information
    ## to the user. M2M fields transaction_origin and transaction_destination hasve to be converted
    ## to string to show user    
    transactions_modified = []
    for i in range(len(transactions)):
        transactions_modified.append({})
        transactions_modified[i]["transaction_id"] = transactions[i].transaction_id
        transactions_modified[i]["transaction_amount"] = "${:,.2f}".format(transactions[i].transaction_amount)
        transactions_modified[i]["transaction_time"] = transactions[i].transaction_time
        transactions_modified[i]["transaction_name"] = transactions[i].transaction_name
        transactions_modified[i]["transaction_origin"] = list(transactions[i].transaction_origin.all())[0].account_number
        transactions_modified[i]["transaction_destination"] = list(transactions[i].transaction_destination.all())[0].account_number
        transactions_modified[i]["transaction_origin_balance"] = "${:,.2f}".format(transactions[i].transaction_origin_balance)
        transactions_modified[i]["transaction_destination_balance"] = "${:,.2f}".format(transactions[i].transaction_destination_balance)

    ## Search for any wire transactions for that account
    try:
        wire_transactions = WireTransaction.objects.filter(transaction_origin=Account.objects.get(account_number=accountNum))
    except WireTransaction.DoesNotExist:
        wire_transactions = []
    ## Repeat same process for adding dict element to a list
    wire_transactions_modified = []
    for i in range(len(wire_transactions)):
        wire_transactions_modified.append({})
        wire_transactions_modified[i]["transaction_id"] = wire_transactions[i].transaction_id
        wire_transactions_modified[i]["transaction_amount"] = "${:,.2f}".format(wire_transactions[i].transaction_amount)
        wire_transactions_modified[i]["transaction_time"] = wire_transactions[i].transaction_time
        wire_transactions_modified[i]["transaction_name"] = wire_transactions[i].transaction_name
        wire_transactions_modified[i]["transaction_origin"] = list(wire_transactions[i].transaction_origin.all())[0].account_number
        wire_transactions_modified[i]["transaction_origin_balance"] = "${:,.2f}".format(wire_transactions[i].transaction_origin_balance)

    ## Add any wire transactions found to the original transactions_modified list 
    transactions_modified.extend(wire_transactions_modified)

    ## Sort the transactions by the time it was processed, starting from latest first
    transactions_modified.sort(key = lambda x: (x["transaction_time"]), reverse=True)

    
    return transactions_modified

def fetch_totalBalance(clientCard):
    """
    Function which returns the sum of all the balances of accounts related to the bank card's holder.

    Args:
        clientCard (int): The bank card number used to login into the website
    Returns:
        balance (float): Sum of the balances of card holder's accounts
    """
    ## Search for any accounts that match the client's bank card number
    accounts = Account.objects.filter(account_card=clientCard)
    balance = 0
    for i in range(len(accounts)):
        balance+=accounts[i].account_balance
    return balance

def validate_transfer_user(request, request_origin, request_destination):
    """
    Function which checks that the transfer origin and destination accounts are both owned by the same user,
    thus validating the funds transfer. If not valid, returns False, if valid, returns True

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): Django request
        request_origin (str): Account number for transfer's origin account
        request_destination (str): Account number for transfer's destination account
    Returns:
        valid (bool): Variable indicating if validity check is successful

    """
    origin_account = Account.objects.get(account_number=int(request_origin))      
    destination_account = Account.objects.get(account_number=int(request_destination))
    user_accounts = Account.objects.filter(account_card=int(request.user.username))

    if (origin_account not in user_accounts) or (destination_account not in user_accounts):
        valid = False
    else:
        valid = True
    return valid
