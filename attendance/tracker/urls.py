from django.urls import path
from . import views   # import your app's views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),  # replace with your actual view
]