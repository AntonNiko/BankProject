from django.db import models

# Create your models here.
class Account(models.Model):
    account_number = model.IntegerField()
    account_balance = model.FloatField()

    account_holder = models.CharField(max_length=200)
    ## TODO: Add more information about accounts

class Transaction(models.Model):
    transaction_id = model.IntegerField()
    transaction_amount = model.FloatField()
    transaction_time = model.DateTimeField("transaction time")
    
    transaction_origin = model.IntegerField()
    transaction_destination = model.IntegerField()
    ## TODO: Add more information about transactions
