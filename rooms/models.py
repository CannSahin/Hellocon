from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
import uuid

# Create your models here.

class RoomManager(models.Manager):
    def users_allowed(self, room):
        return self.get(name=room).memberships.filter(is_allowed=True).select_related('user')

    
class Room(models.Model):
    name = models.CharField(max_length=20)
    slug = models.SlugField(unique=True, db_index=True, default="", null=False) 
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    room_id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, null=False)
    is_public = models.BooleanField(default=False)
    description = models.CharField(max_length=200, null=True, blank=True)
    
    objects = RoomManager()
    
    def __str__(self) -> str:
        return f"{self.name} created by {self.created_by}"


class RoomMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    is_allowed = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('user', 'room',)
        
    def __str__(self):
        return f"{self.user} present in {self.room}"
    

class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="messages")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    message_text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ('date_added', )



class UserChat(models.Model):
    name = models.CharField(max_length=100)
    room_id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, null=False)
    slug = models.SlugField(unique=True, db_index=True, default="", null=False)
    
    def __str__(self):
        return self.name
    
class UserMessages(models.Model):

    description = models.TextField()
    sender_name = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    receiver_name = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    time = models.TimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"To: {self.receiver_name} From: {self.sender_name}"

    class Meta:
        ordering = ('timestamp',)