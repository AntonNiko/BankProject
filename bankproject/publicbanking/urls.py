from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [path("", views.index, name="index"),
               path("accounts/", views.accounts_default, name="accounts_default"),
               path("accounts/<int:account_number>", views.accounts, name="accounts"),
               path("transactions/", views.transactions, name="transactions"),
               path("login/", admin.site.urls),
               path("admin/", admin.site.urls),]
