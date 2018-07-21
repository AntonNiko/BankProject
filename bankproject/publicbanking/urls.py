from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [path("", views.index, name="index"),
               path("accounts/", views.accounts_overview, name="accounts_overview"),
               path("accounts/<int:account_number>", views.accounts, name="accounts"),
               path("transactions/", views.transactions, name="transactions"),
               path("login_user/", views.login_user, name="login_user"),
               path("logout_user/", views.logout_user, name="logout_user"),
               path("admin/", admin.site.urls),]
