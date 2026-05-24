from django.db import models
from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField

# Create your models here.

DEFAULT_PFP = 'https://res.cloudinary.com/do8c7jwpb/image/upload/v1779531900/default-profile-picture-avatar-photo-placeholder-vector-illustration-default-profile-picture-avatar-photo-placeholder-vector-189495158_vt4mtz.webp'

class User(AbstractUser):
    email = models.EmailField(unique=True)
    bio = models.TextField(null=True)
    pfp = CloudinaryField('image', default = DEFAULT_PFP)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f'{self.username}'

class Posts(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    image = CloudinaryField('image', null=True, blank=True)
    video = CloudinaryField('video', resource_type='video', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.username} - {self.created_at}'
    
class comments(models.Model):
    post = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name='comments')
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.username} - {self.created_at}'
    
class likes(models.Model):
    post = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name='likes' ,null=True, blank=True)
    comments = models.ForeignKey(comments, on_delete=models.CASCADE, related_name='likes', null=True, blank=True)
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.username} - {self.created_at}'
    
class friends(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friends')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_of')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.user1} - {self.user2}'
    
class friend_requests(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.sender} - {self.receiver} -> {self.status}'
    
class notifications(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(User,on_delete=models.CASCADE , related_name='receiver')
    type = models.CharField(max_length=50)
    post = models.ForeignKey(Posts, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(comments, on_delete=models.CASCADE, null=True, blank=True)

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.sender} -> {self.receiver}'  
      
class messages(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    image = CloudinaryField('image', null=True, blank=True)
    video = CloudinaryField('video', resource_type='video', null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.sender} - {self.receiver} - {self.created_at}'
    

class Groups(models.Model):
    name = models.CharField(max_length=100)
    gpfp = CloudinaryField('image', default = DEFAULT_PFP)
    bio = models.TextField(null=True)
    members = models.ManyToManyField(User, related_name='chat_group')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_by')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name}'
    
class Group_chat(models.Model):
    group = models.ForeignKey(Groups, on_delete=models.CASCADE, related_name='group_messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    image = CloudinaryField('image', null=True, blank=True)
    video = CloudinaryField('video', resource_type='video', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.sender} -> {self.message}'
    

class Group_chat_isread(models.Model):
    message = models.ForeignKey(Group_chat, on_delete=models.CASCADE, related_name='reads')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.message} - {self.user}'
