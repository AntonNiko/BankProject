from django.db import models

# Create your models here.
class Client(models.Model):
    client_name = models.CharField(max_length=200)
    client_streetname = models.CharField(max_length=200)
    client_housenum = models.IntegerField()
    client_zipCode = models.CharField(max_length=6)
    client_phone = models.CharField(max_length=200)
    client_email = models.CharField(max_length=200)

    def __str__(self):
        return str(self.client_name) +"-"+ str(self.client_phone) +"-"+ str(self.client_email)

class Account(models.Model):
    account_transitNum = models.IntegerField()
    account_instNum = models.IntegerField()
    account_number = models.IntegerField()
    account_type = models.CharField(max_length=200)
    account_balance = models.DecimalField(max_digits=20, decimal_places=2)
    account_card = models.IntegerField(default=None, null=True, blank=True)
    
    account_holder = models.ManyToManyField(Client)
    def __str__(self):
        return self.account_type + "-"+ str(self.account_instNum) +"-"+ str(self.account_transitNum) + "-" + str(self.account_number)

class Transaction(models.Model):
    transaction_id = models.IntegerField()
    transaction_amount = models.FloatField()
    transaction_time = models.DateTimeField("transaction time")
    transaction_name = models.CharField(max_length=200)
    
    transaction_origin = models.ManyToManyField(Account, related_name = "Origin")
    transaction_destination = models.ManyToManyField(Account, related_name = "Destination")

    def __str__(self):
        return str(self.transaction_id)+"-"+str(self.transaction_origin)+"-"+str(self.transaction_destination)
