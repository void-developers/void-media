from django.contrib import admin
from .models import Posts, comments, likes, friends, friend_requests, messages, notifications, Groups, Group_chat_isread ,Group_chat, User

# Register your models here.
admin.site.register(Posts)
admin.site.register(comments)
admin.site.register(likes)
admin.site.register(friends)
admin.site.register(friend_requests)
admin.site.register(messages)
admin.site.register(notifications)
admin.site.register(Groups)
admin.site.register(Group_chat)
admin.site.register(Group_chat_isread)
admin.site.register(User)





