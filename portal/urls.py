from django.urls import path

from . import views

app_name = 'portal'
urlpatterns = [
    path('ssh_home', views.ssh_home, name='ssh_home' ),
    path('partner_home', views.partner_home, name='partner_home'),

    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),


]