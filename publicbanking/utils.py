from .models import Account, Transaction, AccountType, WireTransaction
from django.db.models import Q

def fetch_account(accountNum):
    ## If no accounts are found, continue and display blank page
    try:
        account = Account.objects.get(account_number=accountNum)
    except Account.DoesNotExist:
        account = None
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
    ## Finds all accounts associated with the account holder's card to display
    accounts = Account.objects.filter(account_card=clientCard)
    accounts_modified = []
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

def fetch_accountTransactions(accountNum):
    ## Similar process to find transactions related to account
    try:
        transactions = Transaction.objects.filter(Q(transaction_origin=Account.objects.get(account_number=accountNum)) | Q(transaction_destination=Account.objects.get(account_number=accountNum)))
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
        transactions_modified[i]["transaction_origin_balance"] = transactions[i].transaction_origin_balance
        transactions_modified[i]["transaction_destination_balance"] = transactions[i].transaction_destination_balance

    ## Find wire transactions (pending or completed)
    try:
        wire_transactions = WireTransaction.objects.filter(transaction_origin=Account.objects.get(account_number=accountNum))
    except WireTransaction.DoesNotExist:
        wire_transactions = []
    wire_transactions_modified = []
    for i in range(len(wire_transactions)):
        wire_transactions_modified.append({})
        wire_transactions_modified[i]["transaction_id"] = wire_transactions[i].transaction_id
        wire_transactions_modified[i]["transaction_amount"] = wire_transactions[i].transaction_amount
        wire_transactions_modified[i]["transaction_time"] = wire_transactions[i].transaction_time
        wire_transactions_modified[i]["transaction_name"] = wire_transactions[i].transaction_name
        wire_transactions_modified[i]["transaction_origin"] = list(wire_transactions[i].transaction_origin.all())[0].account_number
        wire_transactions_modified[i]["transaction_origin_balance"] = wire_transactions[i].transaction_origin_balance

    transactions_modified.extend(wire_transactions_modified)
    return transactions_modified

def fetch_totalBalance(clientCard):
    accounts = Account.objects.filter(account_card=clientCard)
    balance = 0
    for i in range(len(accounts)):
        balance+=accounts[i].account_card
    return balance
