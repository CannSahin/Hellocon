import uuid

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.utils.text import slugify

from .models import Message, Room, RoomMembership
from django.core.exceptions import ObjectDoesNotExist
from .models import UserMessages,User
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import send_notification


# Create your views here.
    
@login_required
def room(request, slug):
    print(f"room: {slug} accessed")
    user_name = request.session.get("username")
    user_id = User.objects.get(username=user_name).id
    room = Room.objects.get(slug=slug)
    rooms = RoomMembership.objects.filter(user=user_id) 
    participants = RoomMembership.objects.filter(room=room)
    users= User.objects.exclude(id=user_id)
    is_participant_of_room = True if len(RoomMembership.objects.filter(room=room).filter(user=user_id))>0 else False
    
    #join room because have access, pvt or public doesn't matter
    if is_participant_of_room:
        messages = Message.objects.filter(room=room)
        print("public room accessed by participant")
        return render(request, "rooms/room.html", context={ 
            "room":room,
            "messages":messages,
            "rooms":rooms,
            "has_permission":True,
            "participants":participants,
            "is_participant":is_participant_of_room,
            "friends":users
        })
    
    #room is public but user is not participant
    elif room.is_public and not is_participant_of_room:
        messages = Message.objects.filter(room=room)
        return render(request, "rooms/room.html", context={
            "room":room,
            "messages":messages,
            "rooms":rooms,
            "has_permission":True,
            "participants":participants,
            "is_participant":is_participant_of_room,
            "friends":users
        })
        
    #room is pvt and user is not participant
    return render(request, "rooms/room.html", status=403, context={
        "room":room,
        "rooms":rooms,
        "has_permission":True,
        "is_participant":is_participant_of_room,
        "friends":users
    })
    
    
@login_required
def create_room(request):
    if request.method=="POST":
        print("new room create view called")
        room_name = request.POST.get("room_name")
        description = request.POST.get("room_desc")
        is_public = True if request.POST.get("is_public")=="on" else False
        
        username = request.session.get('username')
        active_user = User.objects.get(username=username)
        room_id = uuid.uuid4()
        room_slug = slugify(f"{room_name}-{str(room_id)}")
        new_room = Room(name=room_name, created_by=active_user, slug=room_slug, description=description, is_public=is_public)
        new_room.save()
        
        new_room_membership = RoomMembership(user=active_user, room=new_room)
        new_room_membership.save()
        
        return redirect(f"/rooms/room/{room_slug}")


@login_required
def join_chat_room(request, slug):
    active_user = request.session.get("username")
    active_user_obj = User.objects.get(username=active_user)
    active_room = Room.objects.get(slug=slug)
    new_membership = RoomMembership(user=active_user_obj, room=active_room)
    new_membership.save()
    print(f"user {active_user} added to room id: {slug}")
    
    return redirect(request.META['HTTP_REFERER'])


@login_required
def add_participant_to_room(request, slug):
    if request.method=="POST":
        participant = request.POST.get("add-participant-name")
        active_room = Room.objects.get(slug=slug)
        print(f"adding participant {participant} to room {active_room}")
        try:
            active_user_obj = User.objects.get(username=participant)
            if not RoomMembership.objects.filter(user=active_user_obj, room=active_room).exists():
                new_member = RoomMembership(user=active_user_obj, room=active_room)
                new_member.save()
            else:
                print(f"User: {participant} already present.")
        except ObjectDoesNotExist:
            print("User not found!")
        
        return redirect(request.META['HTTP_REFERER'])

@login_required
def userchat(request, username):
    current_user = request.user
    other_user = get_object_or_404(User, username=username)
    users= User.objects.exclude(id=current_user.id)
    rooms = RoomMembership.objects.filter(user=current_user.id) 
    # İki kullanıcı arasındaki mesajları çek
    messages = UserMessages.objects.filter(
        Q(sender_name=current_user, receiver_name=other_user) |
        Q(sender_name=other_user, receiver_name=current_user)
    ).order_by('timestamp')

    UserMessages.objects.filter(sender_name=other_user, receiver_name=current_user, seen=False).update(seen=True)
  
    if request.method == 'POST':
        message_text = request.POST.get('message')
        if message_text:
            UserMessages.objects.create(
                description=message_text,
                sender_name=current_user,
                receiver_name=other_user
            )
            send_notification(other_user)
    
    return render(request, "rooms/userchat.html", context={
        "other_user": other_user,
        "messages": messages,
        "friends":users,
        "rooms":rooms,
    })

@csrf_exempt
def get_unseen_message_count(request):
    if request.user.is_authenticated:
        unseen_message_count = UserMessages.objects.filter(receiver_name=request.user, seen=False).count()
        return JsonResponse({'unseen_message_count': unseen_message_count})
    else:
        return JsonResponse({'unseen_message_count': 0})  # Kullanıcı giriş yapmamışsa 0 döndür

@login_required
def chat_with_user(request, username):
    
    ...


@login_required
def add_friend(request):
    
    ...