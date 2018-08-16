from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [path("", views.index),
               path("accounts/", views.accounts_overview),
               path("accounts/<int:num>", views.account),
               path("transfer_request/", views.transfer_request),
               path("wire_transfer_request/", views.wire_transfer_request),
               path("transaction_info/<int:num>", views.transaction_info_request),
               path("wire_transfers/", views.wire_transfers),
               path("currency_exchange/", views.currency_exchange),
               path("login_user/", views.login_user),
               path("logout_user/", views.logout_user),
               ]
