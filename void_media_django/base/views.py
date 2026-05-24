from django.contrib import messages
from django.shortcuts import redirect, render
from .models import Posts, comments, likes, notifications , friend_requests, friends, Groups, Group_chat, Group_chat_isread,User, DEFAULT_PFP
from .models import messages as MassageModel
from django.contrib.auth import authenticate, login , logout
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
import re
from django.db.models import Q

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

import cloudinary.uploader

# Create your views here.

ALLOWED_EXTENSIONS = {"png","jpg","jpeg","gif", "webp"}
ALLOWED_VIDEO_EXTENSIONS = {"mp4", "mov", "webm", "avi", "mkv"}



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
            file = request.FILES.get('file')

            
            
            if content:
                post = Posts.objects.create(username=request.user, content=content)
                if file:
                    extention = file.name.rsplit('.',1)[-1].lower()
                    if extention in  ALLOWED_EXTENSIONS:
                        post.image = file
                    elif extention in ALLOWED_VIDEO_EXTENSIONS:
                        post.video = file
                    else:
                        messages.error(request,'invalid file type')
                        post.delete()
                        return redirect('home')


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
    if request.user.is_authenticated:
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
    else:
        incomming_request = None
        outgoing_request = None
        is_friend = None
    
    return render(request, 'base/profile.html', {'profile_user': profile_user, 'posts': post, 'liked_posts': liked_posts, 'comments': liked_comments, 'incomming_request':incomming_request, 'outgoing_request': outgoing_request ,'is_friend':is_friend})

def editpfp(request, user_id):
    if not request.user.is_authenticated:
        return redirect('login')
    user = User.objects.get(id=user_id)
    if request.user != user:
        return HttpResponse('You are not allowed to make this action!!')
    if request.method == 'POST':
        filename = request.FILES.get('filename')
        if filename:
            extention = filename.name.rsplit('.',1)[-1].lower()
            if extention in ALLOWED_EXTENSIONS:
                old_pfp = user.pfp
                user.pfp = filename
                user.save()
                old_public_id = getattr(old_pfp, 'public_id', None)
                if old_public_id and str(old_pfp) != DEFAULT_PFP:
                    cloudinary.uploader.destroy(old_public_id)
                return redirect('profile', user.id)
            else:
                messages.error(request,'invalid file type.')
        else:
            messages.error(request,'can not be empty.')
    return render(request,'base/editpfp.html',{'user':user})

def editbio(request,user_id):
    if not request.user.is_authenticated:
        return redirect('login')
    user = User.objects.get(id=user_id)
    if request.user != user:
        return HttpResponse('You Are Not Allowed To Make This Action!!!')
    if request.method == 'POST':
        bio = request.POST.get('bio')
        if bio:
            user.bio = bio
            user.save()
            return redirect('profile', user.id)
    return render(request, 'base/editbio.html', {'user':user})

def Login(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'base/sign_log.html', {'page': page})

def Logout(request):
    logout(request)
    return redirect('home')

def Register(request):
    page = 'register'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        has_error = False
        username = request.POST.get('username')
        if not username:
            messages.error(request, 'Username is required.')
            has_error = True
        elif len(username) < 3:
            messages.error(request, 'Username must be at least 3 characters.')
            has_error = True
        elif len(username) > 30:
            messages.error(request, 'Username must be 30 characters or less.')
            has_error = True
        elif not re.match(r'^[a-zA-Z0-9_]+$', username):
            messages.error(request, 'Username can only contain letters, numbers, and underscores.')
            has_error = True
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            has_error = True


        email = request.POST.get('email')
        if not email:
            messages.error(request, 'Email is required.')
            has_error = True
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            has_error = True


        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        else:
            try:
                validate_password(password)
            except ValidationError as errors:
                 for error in errors:
                    messages.error(request, error)
                    has_error = True

        if has_error:
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        login(request, user)
        return redirect('home')
    
    return render(request , 'base/sign_log.html', {'page': page})
    
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

    groups = Groups.objects.filter(
    members=request.user
    )

    for group in groups:

        group.unread_count = Group_chat.objects.filter(
            group=group
        ).exclude(
            reads__user=request.user
        ).exclude(
            sender=request.user
        ).count()
    return render(request, 'base/friends_list.html', {'friend': friend, 'groups':groups})

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
        file = request.FILES.get('file')
        


        if content:
            msg = MassageModel.objects.create(
                sender = request.user,
                receiver = other_user,
                content = content,
            )

            if file:
                extention = file.name.rsplit('.',1)[-1].lower()
                if extention in  ALLOWED_EXTENSIONS:
                    msg.image = file
                elif extention in ALLOWED_VIDEO_EXTENSIONS:
                    msg.video = file
                else:
                    messages.error(request,'invalid file type')
                    msg.delete()
                    return redirect('chat' ,user_id=user_id)

            msg.save()
            
            return redirect('chat' ,user_id=user_id)
        else:
            messages.error(request, 'can not be empty')
    return render(request,'base/chat.html', {'other_user':other_user, 'message':message})

def create_group(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            gpfp = request.FILES.get('gpfp')
            if name:

                group = Groups.objects.create(
                    name = name,
                    created_by = request.user
                )
                if gpfp:
                    extention = gpfp.name.rsplit('.',1)[-1].lower()
                    if extention in ALLOWED_EXTENSIONS:
                        group.gpfp = gpfp
                        group.save()
                    else:
                        group.delete()
                        messages.error(request,'invalid file type')
                        return redirect('create_group')
                group.members.add(request.user)
                members = request.POST.getlist('members')
        

                for m in members:
                    user = User.objects.get(id = m)
                    group.members.add(user)

                return redirect('group_chat', group.id)
            else:
                messages.error(request,'cant be empty')
        except Exception as e:
            return HttpResponse(str(e))
    
    friend = friends.objects.filter(
            Q(user1  = request.user) | Q(user2 = request.user)
        )
    
    friend_list = []

    for f in friend:
        if f.user1 == request.user:
            friend_list.append(f.user2)
        else:
            friend_list.append(f.user1)
    return render(request, 'base/group_form.html',{'friend':friend_list})

def group_chat(request, group_id):
    if not request.user.is_authenticated:
        return redirect('login')
    group = Groups.objects.get(id=group_id)

    if request.user not in group.members.all():
        return HttpResponse('You Are Not Allowed To Make This Action!!!!!')

    group_messages = Group_chat.objects.filter(
        group = group
    )

    for message in group_messages.exclude(sender=request.user):

        Group_chat_isread.objects.get_or_create(
            message=message,
            user=request.user
        )

    if request.method =='POST':
        message = request.POST.get('message')
        file = request.FILES.get('file')
        if message:
            try:
                msg = Group_chat.objects.create(
                    group = group,
                    sender = request.user,
                    message = message
                )
                if file:
                    extention = file.name.rsplit('.',1)[-1].lower()
                    if extention in  ALLOWED_EXTENSIONS:
                        msg.image = file
                    elif extention in ALLOWED_VIDEO_EXTENSIONS:
                        msg.video = file
                    else:
                        messages.error(request,'invalid file type')
                        msg.delete()
                        return redirect('group_chat', group_id)

                msg.save()

                return redirect('group_chat', group.id)
            except:
                return HttpResponse('Something went wrong')
        else:
            messages.error(request,'cant be empty')
            
    return render(request, 'base/group_chat.html', {'group_messages':group_messages, 'group':group})

def group_info(request, group_id):
    group = Groups.objects.get(id=group_id)

    if request.user not in group.members.all():
        return HttpResponse('You Are Not Allowed To Make This Action!!!!!')

    group_members = group.members.all()

    return render(request, 'base/group_info.html', {'group_members':group_members, 'group':group})

def add_member(request, group_id):
    group = Groups.objects.get(id=group_id)

    if group.created_by != request.user:
        return HttpResponse('You Are Not Allowed To Make This Action!!!!!')
    friend = friends.objects.filter(
            Q(user1  = request.user) | Q(user2 = request.user)
        )
    
    friend_list = []

    for f in friend:
        friend_list.append(f.user2 if f.user1 == request.user else f.user1)

    available_friends = [u for u in friend_list if u not in group.members.all()]

    if request.method == 'POST':
        if group.created_by == request.user:
            members = request.POST.getlist('members')
        

            for m in members:
                user = User.objects.get(id = m)
                group.members.add(user)
            return redirect('group_info' , group.id)
        else:
            return HttpResponse('You Are Not Allowed To Make This Action!!!!!')
    return render(request, 'base/add_member.html',{'friend_list':available_friends, 'group':group})

def delete_member(request, user_id, group_id):
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    group = Groups.objects.get(id=group_id)

    if group.created_by != request.user:
        return HttpResponse('You Are Not Allowed To Make This Action!!!!!')
    
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            group.members.remove(user)
            return redirect('group_info' , group.id)
        except:
            return HttpResponse('Something went wrong!')

def editgpfp(request, group_id):
    if not request.user.is_authenticated:
        return redirect('login')
    group = Groups.objects.get(id=group_id)
    if not group.members.filter(id=request.user.id).exists():
        return HttpResponse('You are not allowed to make this action!!')
    if request.method == 'POST':
        filename = request.FILES.get('filename')
        if filename:
            extention = filename.name.rsplit('.',1)[-1].lower()
            if extention in ALLOWED_EXTENSIONS:
                old_gpfp = group.gpfp
                group.gpfp = filename
                group.save()
                old_public_id = getattr(old_gpfp, 'public_id', None)
                if old_public_id and str(old_gpfp) != DEFAULT_PFP:
                    cloudinary.uploader.destroy(old_public_id)
                return redirect('group_info', group.id)
            else:
                messages.error(request,'invalid file type.')
        else:
            messages.error(request,'can not be empty.')
    return render(request,'base/editpfp.html',{'group':group})

def editgbio(request,group_id):
    if not request.user.is_authenticated:
        return redirect('login')
    group = Groups.objects.get(id=group_id)
    if not group.members.filter(id=request.user.id).exists():
        return HttpResponse('You Are Not Allowed To Make This Action!!!')
    if request.method == 'POST':
        bio = request.POST.get('bio')
        if bio:
            group.bio = bio
            group.save()
            return redirect('group_info', group.id)
    return render(request, 'base/editbio.html', {'group':group})
