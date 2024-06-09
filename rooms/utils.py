from django.urls import register_converter

class UserChatConverter:
    regex = '[^/]+-[^/]+'

    def to_python(self, value):
        user1, user2 = value.split('-')
        return sorted([user1, user2])

    def to_url(self, value):
        user1, user2 = sorted(value)
        return f'{user1}-{user2}'

register_converter(UserChatConverter, 'userchat')
