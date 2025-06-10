from django.contrib import admin
from django.urls import path
from . import views
from .views import MyLoginView

urlpatterns = [
    path('', views.index_page, name='index-page'),
    
    # ¡CORRECCIÓN AQUÍ! Añade la coma después de .as_view()
    path('login/', MyLoginView.as_view(), name='login'), 
    
    path('home/', views.home, name='home'),
    
    path('buscar/', views.search, name='buscar'),
    path('filter_by_type/', views.filter_by_type, name='filter_by_type'),

    path('favourites/', views.getAllFavouritesByUser, name='favoritos'),
    path('favourites/add/', views.saveFavourite, name='agregar-favorito'),
    path('favourites/delete/', views.deleteFavourite, name='borrar-favorito'),

    path('exit/', views.exit, name='exit'),
    
    # URL para la funcionalidad de suscripción
    path('register/', views.register, name='register'),
]