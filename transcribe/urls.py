from django.urls import path
from . import views

# Create your tests here.
urlpatterns = [
    path('', views.home, name="home"),
    path('about/', views.about, name="about"),
    path('contact/', views.contact, name="contact"),
    path('detect/', views.transcription_view, name="detect"),
    # Alias route for templates referencing 'transcription'
    path('transcription/', views.transcription_view, name="transcription"),
    path('classify-text/', views.classify_text, name="classify_text")
]
