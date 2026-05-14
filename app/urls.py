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

    # Estas son las tres vistas que actualizamos al estándar snake_case
    path('favourites/', views.get_all_favourites_by_user, name='favoritos'),
    path('favourites/add/', views.save_favourite, name='agregar-favorito'),
    path('favourites/delete/', views.delete_favourite, name='borrar-favorito'),

    path('exit/', views.exit, name='exit'),
    
    # URL para la funcionalidad de suscripción
    path('register/', views.register, name='register'),
]