from django.contrib.auth.models import User
from ..models import Content

def create_user(username='test@example.com', password='test'):
    u = User(username=username)
    u.set_password(password)
    u.save()
    return u

def login(client):
    """
    Login as normal user (not admin or staff)
    """
    create_user()
    return client.login(username='test@example.com', password='test')

def create_content(title='test', filepath='http://example.com/something.mp4', thumb=False):
    c = Content(title=title, filepath=filepath, thumb=thumb)
    c.save()
    return c
