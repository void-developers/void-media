from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.Login, name='login'),
    path('logout/', views.Logout, name='logout'),
    path('register/', views.Register, name='register'),
    path('comment/<int:pk>/', views.comment, name='comment'),
    path('like/<int:pk>/', views.like, name='like'),
    path('comment-like/<int:pk>/', views.comments_like, name='comments_like'),
    path('liked-users/<int:pk>/', views.likedusers, name='liked_users'),
    path('profile/<int:pk>/', views.profile, name='profile'),
    path('edit-post/<int:pk>/', views.edit_post, name='edit_post'),
    path('search/', views.search, name='search'),
    path('notifications/', views.notification, name='notifications'),
    path('notification_counter/', views.notification_counter, name='notification_counter'),
    path('delete_notification/<int:pk>', views.delete_notification, name='delete_notification'),
    path('friend_request/<int:pk>', views.friend_request, name='friend_request'),
    path('accept_request/<int:pk>', views.accept_request, name='accept_request'),
    path('unfriend/<int:user_id>', views.unfreind, name='unfriend'),
    path('friends_list', views.friends_list, name="friends_list"),
    path('chat/<int:user_id>', views.chat, name='chat'),
    ]