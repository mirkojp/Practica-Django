from django.urls import path
from Usuarios import views
urlpatterns = [
    path("Home/", views.home ,name="Home")
]