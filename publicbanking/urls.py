from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [path("", views.index),
               path("accounts/", views.accounts_overview),
               path("accounts/<int:num>", views.account),
               path("transfer_request/", views.transfer_request),
               path("login_user/", views.login_user),
               path("logout_user/", views.logout_user),
               ]
