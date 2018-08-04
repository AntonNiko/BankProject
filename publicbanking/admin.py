from django.contrib import admin
from .models import Account, Transaction, Client, AccountType

# Register your models here.
admin.site.register(Account)
admin.site.register(AccountType)
admin.site.register(Transaction)
admin.site.register(Client)
