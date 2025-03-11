from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload, name='upload'),
    path('record/', views.record, name='record'),
    path('display/<str:filename>/', views.display, name='display'),
]
