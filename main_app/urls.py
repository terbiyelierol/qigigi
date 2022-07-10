from django import urls
from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('listings/', views.listings, name='listings'), 
    path('listings/new/', views.listings_new, name='listings_new'),
    path('listings/create/', views.listings_create, name='listings_create'),
    path('listings/<int:listing_id>/', views.listings_detail, name='listings_detail'),
    path('listings/<int:listing_id>/delete', views.listings_delete, name='listings_delete'),
    path('listings/<int:listing_id>/edit/', views.listings_edit, name='listings_edit'),
    path('listings/<int:listing_id>/update/', views.listings_update, name='listings_update'),
    path('listings/user/<int:user_id>/', views.user_listings, name='user_listings'),
    path('accounts/signup/', views.signup, name='signup'),
    path('accounts/password_reset/', include('django.contrib.auth.urls')),
    path('accounts/password_reset/done/', include('django.contrib.auth.urls')),
    path('accounts/reset/<uidb64>/<token>/', include('django.contrib.auth.urls')),
    path('accounts/reset/done/', include('django.contrib.auth.urls'))
]