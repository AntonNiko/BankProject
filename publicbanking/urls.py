from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [path("", views.index),
               path("accounts/", views.accounts_overview),
               path("accounts/<int:account_number>", views.accounts),
               path("transactions/", views.transactions),
               path("login_user/", views.login_user),
               path("logout_user/", views.logout_user),
               ]
