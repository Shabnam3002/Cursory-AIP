from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.campaign_list, name='campaign_dashboard'),
    path('detail/<int:pk>/', views.campaign_detail, name='campaign_detail'), #<int:pk> meaning campaign id no. will appear in the url 
    path('activate/<int:campaign_id>/', views.activate_campaign, name='activate_campaign'),
    path('submit/', views.submit_campaign, name='submit_campaign'),
    path('tracking/<int:campaign_id>/', views.campaign_tracking, name='campaign_tracking'),
]