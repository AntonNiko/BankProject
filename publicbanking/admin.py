from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Client)
admin.site.register(AccountType)
admin.site.register(Account)
admin.site.register(BufferAccount)
admin.site.register(Transaction)
admin.site.register(WireTransaction)

