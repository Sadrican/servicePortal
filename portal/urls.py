"""URL routes for the portal app.

Stick to Django defaults; keep simple, readable URL names and view bindings.
"""

from django.urls import path

from . import views

app_name = 'portal'
urlpatterns = [
    # Pages
    path('', views.home, name='home'),
    path('customers', views.customers, name='customers'),
    path('users', views.users, name='users'),

    # Auth
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),

    # Claims
    path('claims_page', views.claims_page, name='claims'),
    path('create_claim', views.create_claim, name='create_claim'),
    path('claim/<int:claim_id>', views.claim_details, name='claim_details'),
    path('claim/<int:claim_id>/update', views.update_claim, name='update_claim'),

    # AJAX APIs
    path('api/part-info', views.part_info, name='part_info'),
    path('api/labour-info', views.labour_info, name='labour_info'),
]