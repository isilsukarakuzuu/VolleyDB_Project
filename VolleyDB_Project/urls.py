"""
URL configuration for VolleyDB_Project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from volleyball import views
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='base.html'), name='home'),
    path('login/', views.login_view, name='login'),
    path('dashboard/database-manager/', views.database_manager_dashboard, name='database_manager_dashboard'),
    path('dashboard/database-manager/add_user/', views.add_user, name='add_user'),
    path('get_stadium/', views.get_stadium, name='get_stadium'),
    path('dashboard/database-manager/update_stadium/', views.update_stadium, name='update_stadium'),
    path('dashboard/player/', views.player_dashboard, name='player_dashboard'),
    path('dashboard/coach/', views.coach_dashboard, name='coach_dashboard'),
    path('get_jury_names_surnames', views.get_jury_names_surnames, name='get_jury_names_surnames'),
    path('dashboard/jury/', views.jury_dashboard, name='jury_dashboard'),
    path('create_match_session/', views.create_match_session, name='create_match_sesion'),
    path('create_squad/', views.create_squad, name='create_squad'),
]
