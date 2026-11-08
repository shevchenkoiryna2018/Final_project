from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'plants'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('plants/create/', views.plant_create, name='plant_create'),
    path('plants/update/<int:id>/', views.plant_update, name='plant_update'),
    path('plants/delete/<int:id>/', views.plant_delete, name='plant_delete'),
]

