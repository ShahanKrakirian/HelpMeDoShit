from django import template
register = template.Library()
from ..models import *

@register.filter(name='has_bid')
def has_bid(user_id, task_id):
    user = User.objects.get(id=user_id)
    task = Task.objects.get(id=task_id)
    return True if user in task.users_bidded.all() else False
