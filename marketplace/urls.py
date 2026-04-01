from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('create/', views.create_listing, name='create_listing'),

    # 🔥 USE ONLY ONE VERSION
    path('listing/<int:listing_id>/', views.listing_detail, name='listing_detail'),

    path('edit/<int:id>/', views.edit_listing, name='edit_listing'),
    path('delete/<int:id>/', views.delete_listing, name='delete_listing'),

    path('my-listings/', views.my_listings, name='my_listings'),

    path('review/<int:listing_id>/', views.add_review, name='add_review'),

    path('favorite/<int:listing_id>/', views.toggle_favorite, name='toggle_favorite'),

    path('message/<int:listing_id>/', views.send_message, name='send_message'),

    # 🔥 NEW INBOX PAGE
    path('inbox/', views.inbox, name='inbox'),
]