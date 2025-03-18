from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload, name='upload'),
    path('record/', views.record_audio, name='record_audio'),  # POST endpoint for recording audio
    path('record_page/', views.record, name='record'),  # View to render the audio recording page
    path('display/<str:filename>/', views.display, name='display'),  # Display the spectrogram
]
