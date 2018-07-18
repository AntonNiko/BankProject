from django.db import models

# Create your models here.
class Account(models.Model):
    account_transitNum = models.IntegerField()
    account_instNum = models.IntegerField()
    account_number = models.IntegerField()
    account_type = models.CharField(max_length=200)
    account_balance = models.FloatField()
    

    account_holder = models.CharField(max_length=200)
    ## TODO: Add more information about accounts

    def __str__(self):
        return self.account_type + "-" + str(self.account_transitNum) + "-" + str(self.account_number)

class Transaction(models.Model):
    transaction_id = models.IntegerField()
    transaction_amount = models.FloatField()
    transaction_time = models.DateTimeField("transaction time")
    transaction_name = models.CharField(max_length=200)
    
    transaction_origin = models.ForeignKey(Account, on_delete=models.CASCADE)
    transaction_destination = models.IntegerField()
    ## TODO: Add more information about transactions

    def __str__(self):
        return str(self.transaction_id)
