from django.urls import path
from . import views

urlpatterns = [
    path('verify/', views.verify_account_view, name='verify_account'),
    path('verify-now/<int:account_id>/', views.start_verification, name='start_verification'),
    path('connect/', views.connect_account, name='connect_account'),
    path('delete-connected/<int:account_id>/', views.delete_connected_account, name='delete_connected_account'),
]
