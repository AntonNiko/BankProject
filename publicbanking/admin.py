from django.contrib import admin
from .models import Account, Transaction, Client, AccountTypes

# Register your models here.
admin.site.register(Account)
admin.site.register(AccountTypes)
admin.site.register(Transaction)
admin.site.register(Client)
