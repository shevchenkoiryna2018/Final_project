from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .forms import LoginForm

app_name = 'plants'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='login.html', authentication_form=LoginForm),
        name='login'
    ),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('plants/create/', views.plant_create, name='plant_create'),
    path('plants/update/<int:id>/', views.plant_update, name='plant_update'),
    path('plants/delete/<int:id>/', views.plant_delete, name='plant_delete'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/update/<int:id>/', views.task_update, name='task_update'),
    path('tasks/delete/<int:id>/', views.task_delete, name='task_delete'),
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/complete/<int:id>/', views.task_complete, name='task_complete'),
    path('history/', views.care_history, name='care_history'),
]

