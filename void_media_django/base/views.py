from django.contrib import messages
from django.shortcuts import redirect, render
from .models import Posts, comments, likes, notifications , friend_requests, friends
from .models import messages as MassageModel
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login , logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
import re
from django.db.models import Q

def handle_mentions(content, sender , post=None, comment=None):
    mentions = re.findall(r'@(\w+)', content )

    for username in mentions:
        try:
            user = User.objects.get(username=username)
            profile_url = f'/profile/{user.id}/'

            content = content.replace(
            f'@{username}',
            f'<a href="{profile_url}">@{username}</a>'
            )
        except User.DoesNotExist:
            pass

    mentioned_users = User.objects.filter(username__in=mentions)

    for user in mentioned_users:
        if user != sender:
            if comment is not None:
                notif_type = 'comment mention'
            elif post is not None:
                notif_type = 'post mention'
            else:
                notif_type = 'mention'
            notifications.objects.create(
            sender = sender,
            receiver = user,
            post = post,
            comment = comment,
            type = notif_type
            )
    return content

# Create your views here.
def home(request):
    post = Posts.objects.all()
    comment_counter = comments.post

    user = request.user

    for pos in post:
        if user.is_authenticated:
            pos.is_liked = pos.likes.filter(username=user).exists()
        else:
            pos.is_liked = False
    

    if request.POST:
        if user.is_authenticated:
            content = request.POST.get('content')
            
            if content:
                post = Posts.objects.create(username=request.user, content=content)
                post.content = handle_mentions(
                    content=content,
                    sender = request.user,
                    post = post,
                )
                post.save()
                    
                return redirect('home')
            else:
                messages.error(request, 'Content cannot be empty.')
        else:
            return HttpResponse('YOU ARE NOT ALLOWED TO SHARE A POST!!!!!!!!!!')
    return render(request, 'base/home.html', {'posts': post})

def profile(request,pk):
    profile_user = User.objects.get(id=pk)
    post = Posts.objects.filter(username=profile_user)

    current_user = request.user

    for pos in post:
        if current_user.is_authenticated:
            pos.is_liked = pos.likes.filter(username=current_user).exists()
        else:
            pos.is_liked = False

    liked_posts = Posts.objects.filter(likes__username=profile_user)

    for pos in liked_posts:
        if current_user.is_authenticated:
            pos.is_liked = pos.likes.filter(username=current_user).exists()
        else:
            pos.is_liked = False

    liked_comments = comments.objects.filter(likes__username=profile_user)
    for comment in liked_comments:
        if current_user.is_authenticated:
            comment.is_liked = comment.likes.filter(username=current_user).exists()
        else:
            comment.is_liked = False

    incomming_request = friend_requests.objects.filter(
        sender = profile_user,
        receiver = request.user
    ).first()

    outgoing_request = friend_requests.objects.filter(
        sender = request.user,
        receiver = profile_user
    ).first()


    is_friend = friends.objects.filter(
        user1=request.user,
        user2=profile_user
    ).exists() or friends.objects.filter(
        user1=profile_user,
        user2=request.user
    ).exists()
    
    return render(request, 'base/profile.html', {'profile_user': profile_user, 'posts': post, 'liked_posts': liked_posts, 'comments': liked_comments, 'incomming_request':incomming_request, 'outgoing_request': outgoing_request ,'is_friend':is_friend})

def Login(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'User does not exist.')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'base/sign_log.html', {'page': page})

def Logout(request):
    logout(request)
    return redirect('home')

def Register(request):
    page = 'register'
    form = UserCreationForm()
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')
            return redirect('home')
    return render(request , 'base/sign_log.html', {'page': page, 'form': form})
    
    
def comment(request ,pk):
    post = Posts.objects.get(id=pk)
    
    current_user = request.user
    if current_user.is_authenticated:
        post.is_liked = post.likes.filter(username=current_user).exists()
    else:
        post.is_liked = False

    show_post = post.content
    post_comments = post.comments.all()

    current_user = request.user
    for comment in post_comments:
        if current_user.is_authenticated:
            comment.is_liked = comment.likes.filter(username=current_user).exists()
        else:
            comment.is_liked = False

    if request.method == 'POST':
        content = request.POST.get('content')
        
        if content:
            comment = comments.objects.create(post=post, username=request.user, content=content)
            comment.content = handle_mentions(
                content=content,
                sender = request.user,
                post = post,
                comment = comment
            )

            if request.user != post.username:
                notifications.objects.create(
                    sender = request.user,
                    receiver = post.username,
                    comment = comment,
                    type = 'comment'
                )
            comment.save()
            return redirect('comment', pk=pk)
        else:
            messages.error(request, 'Comment cannot be empty.')
    return render(request, 'base/comments.html', {'comments': post_comments, 'show_post': show_post, 'post':post})

def like(request, pk):
    post = Posts.objects.get(id=pk)
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST':
        like = likes.objects.filter(post=post, username=request.user)
        if like.exists():
            like.delete()
            return redirect(request.META.get('HTTP_REFERER'))
        else:
            like = likes.objects.create(post=post, username=request.user)
            like.save()

            if request.user != post.username:
                notifications.objects.create(
                    sender = request.user,
                    receiver = post.username,
                    post = post,
                    type = 'post like'
                )
            return redirect(request.META.get('HTTP_REFERER'))
    return render(request, 'base/home.html', {'post': post})

def comments_like(request, pk):
    comment = comments.objects.get(id=pk)
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST':
        like = likes.objects.filter(comments=comment, username=request.user)
        if like.exists():
            like.delete()
            return redirect('comment', pk=comment.post.id)
        else:
            like = likes.objects.create(comments=comment, username=request.user)
            like.save()
            if request.user != comment.username:
                notifications.objects.create(
                    sender = request.user,
                    receiver = comment.username,
                    comment = comment,
                    type = 'comment like'
                )
            return redirect('comment', pk=comment.post.id)
    return render(request, 'base/comments.html', {'comment': comment})

def likedusers(request, pk):
    type = request.GET.get('type')
    if type == 'post':
        post = get_object_or_404(Posts, id=pk)
        liked_users = post.likes.values_list('username__username', flat=True)
        return render(request, 'base/likes.html', {'liked_users': liked_users})
    elif type == 'comment':
        comment = get_object_or_404(comments, id=pk)
        liked_users = comment.likes.values_list('username__username', flat=True)
        return render(request, 'base/likes.html', {'liked_users': liked_users})
    else:
        messages.error(request, 'Invalid type specified.')
        return redirect('home')


def edit_post(request, pk):
    post = Posts.objects.get(id=pk)
    if request.user != post.username:
        return HttpResponse('You are not authorized to edit this post.')
    
    clean_content = re.sub(r'<[^>]*>', '', post.content)
    next_url = request.GET.get('next') or request.POST.get('next')
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            if content == clean_content:
                return redirect(next_url, "home")
            post.content = handle_mentions(content, request.user, post=post)
            post.edited = True
            post.save()
            return redirect(next_url, 'home')
        else:
            messages.error(request, 'Content cannot be empty.')

    return render(request, 'base/edit_post.html', {'post': post, 'clean_content':clean_content, 'next_url':next_url})

def search(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    users = User.objects.filter(username__icontains=q)
    return render(request,'base/home.html',{'users':users, 'q':q})

def notification(request):
    notif = notifications.objects.filter(receiver = request.user)

    notif.filter(is_read=False).update(is_read=True)
    friend_request = friend_requests.objects.filter(
        receiver = request.user
    )
    return render(request, 'base/notifications.html',{'notif':notif, 'friend_request':friend_request})

def notification_counter(request):
    count = 0
    if request.user.is_authenticated:
        count = notifications.objects.filter(receiver = request.user, is_read = False).count()
    else:
        count = 0
    return render(request, 'main.html', {'new_notification':count})

def delete_notification(request , pk):
    if not request.user.is_authenticated:
        return redirect('login')
    notification = notifications.objects.get(id=pk)
    if request.user != notification.receiver:
        return HttpResponse('YOU ARE NOT ALLOWED HERE!!!!!!')
    if request.method == 'POST':
        notification.delete()
    return redirect('notifications')


def friend_request(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')
    receiver = User.objects.get(id=pk)
    if request.method =='POST':

        try:
            friend_requests.objects.create(
                sender = request.user,
                receiver = receiver
            )
            notifications.objects.create(
                sender = request.user,
                receiver = receiver,
                type = 'friend request',
            )
            return redirect('profile', pk=receiver.id)
        
        except:
            return HttpResponse('Something Went Wrong!!')
    return render(request,'base/profile.html', {'receiver':receiver})


def accept_request(request,pk):
    the_request = friend_requests.objects.get(id=pk)
    if the_request.receiver != request.user:
        return HttpResponse('You Are Not Allowed To Do This Action!!!')

    if request.method == 'POST':
        try:
            the_request.status = True
            the_request.save()
            friends.objects.create(
                user1 = the_request.sender,
                user2 = the_request.receiver
            )
        except:
            return HttpResponse('Something Went Wrong')
    return redirect(request.META.get('HTTP_REFERER'))

def unfreind(request,user_id):
    if not request.user.is_authenticated:
        return redirect('login')
    profile_user = User.objects.get(id=user_id)
    if request.user == profile_user:
        return HttpResponse('unexpected error!!')
    if request.method == 'POST':
        try:
            friends.objects.filter(
                Q(user1 = profile_user, user2 = request.user) |
                Q(user1 = request.user, user2 = profile_user)
            ).delete()

            friend_requests.objects.filter(
                Q(sender = profile_user, receiver = request.user) |
                Q(sender = request.user, receiver = profile_user)
            ).delete()
            return redirect('profile' ,pk = profile_user.id)
        except:
            return HttpResponse('unexpected error')

    

def friends_list(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    friend = friends.objects.filter(
        Q(user1 = request.user) | Q(user2 = request.user)
    )

    for f in friend:
        if f.user1 == request.user:
            f.other_user = f.user2
        else:
            f.other_user = f.user1

        f.unread_count = MassageModel.objects.filter(
            sender=f.other_user,
            receiver=request.user,
            is_read=False
        ).count()
    return render(request, 'base/friends_list.html', {'friend': friend})

def chat(request, user_id):
    if not request.user.is_authenticated:
        return redirect('login')
    other_user = User.objects.get(id=user_id)
    MassageModel.objects.filter(
                sender = other_user,
                receiver = request.user,
                is_read = False
            ).update(is_read = True)

    message = MassageModel.objects.filter(
        Q(sender = request.user, receiver = other_user) |
        Q(sender = other_user, receiver = request.user)
    ).order_by('created_at')

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            MassageModel.objects.create(
                sender = request.user,
                receiver = other_user,
                content = content,
            )
            
            return redirect('chat' ,user_id=user_id)
        else:
            message.error('can not be empty')
    return render(request,'base/chat.html', {'other_user':other_user, 'message':message})


