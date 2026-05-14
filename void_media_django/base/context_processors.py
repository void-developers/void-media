from .models import notifications
from .models import messages as MessagesModel

def notification_count(request):

    if request.user.is_authenticated:
        count = notifications.objects.filter(
            receiver=request.user,
            is_read=False
        ).count()
    else:
        count = 0

    return {'new_notification': count}

def unread_count(request):
    if request.user.is_authenticated:
        msg_count = MessagesModel.objects.filter(
            receiver = request.user,
            is_read = False
        ).count
    else:
        msg_count = 0
    return {'msg_count': msg_count}