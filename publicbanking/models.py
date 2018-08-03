from django.db import models

# Create your models here.
class Client(models.Model):
    """
    Client model: Represents a bank's client, properties of which include being able to
    own several bank accounts, request transfers in between their accounts and other accounts.
    """
    client_id = models.CharField(primary_key=True, max_length=50, default=None)
    client_name = models.CharField(max_length=200)
    client_streetname = models.CharField(max_length=200)
    client_housenum = models.IntegerField()
    client_city = models.CharField(max_length=100)
    client_zipCode = models.CharField(max_length=6)
    client_phone = models.CharField(max_length=200)
    client_email = models.CharField(max_length=200)

    def __str__(self):
        return str(self.client_name) +"-"+ str(self.client_phone) +"-"+ str(self.client_email)

class Account(models.Model):
    """
    Account model: Represents a bank account, which is owned by one specific account holder
    (can expand to joint accounts). Information stored includes the account's number and
    transit number, balance, optional related bank card.
    """
    account_holder = models.ForeignKey("Client", on_delete=models.CASCADE)
    account_transitNum = models.IntegerField()
    account_instNum = models.IntegerField()
    account_number = models.IntegerField()
    account_type = models.CharField(max_length=200)
    account_balance = models.DecimalField(max_digits=20, decimal_places=2)
    account_card = models.IntegerField(default=None, null=True, blank=True)
    
    def __str__(self):
        return self.account_type + "-"+ str(self.account_instNum) +"-"+ str(self.account_transitNum) + "-" + str(self.account_number)

class AccountTypes(models.Model):
    account_type_name = models.CharField(max_length=100)
    account_free_transaction_len = models.IntegerField()
    account_free_transaction_period = models.CharField(max_length=100)
    account_website_transaction_fee = models.DecimalField(max_digits=10, decimal_places=2)
    account_retail_transaction_fee = models.DecimalField(max_digits=10, decimal_places=2)
    account_etransfer_transaction_fee = models.DecimalField(max_digits=10, decimal_places=2)
    account_interest_rate = models.DecimalField(max_digits=10, decimal_places=5)

    def __str__(self):
        return str(self.account_type_name)


class Transaction(models.Model):
    """
    Transaction model: Represents a transaction, which occurs between 2 accounts registered with
    the bank. Information stored includes the amount transferred, time, name of transaction, its
    origin as well as destination. For transfers to accounts not registered with the bank, a special
    account is dedicated for such transfer requests.
    """
    transaction_id = models.IntegerField()
    transaction_amount = models.FloatField()
    transaction_time = models.DateTimeField("transaction time")
    transaction_name = models.CharField(max_length=200)
    
    transaction_origin = models.ManyToManyField(Account, related_name = "transaction_origin+")
    transaction_destination = models.ManyToManyField(Account, related_name = "transaction_destination+")

    def __str__(self):
        return str(self.transaction_id)+"-"+str(self.transaction_origin)+"-"+str(self.transaction_destination)
