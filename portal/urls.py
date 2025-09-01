from django.urls import path

from . import views

app_name = 'portal'
urlpatterns = [
    path('', views.home, name='home'),

    path('customers',views.customers, name='customers'),
    path('users', views.users, name='users'),

    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),

    path('claims_page', views.claims_page, name='claims'),
    path('create_claim',views.create_claim, name='create_claim'),
    path('claim/<int:claim_id>',views.claim_details, name='claim_details')

]