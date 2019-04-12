from django import template
from app.models import Status

register = template.Library() 

@register.filter(name='has_group') 
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists() 

@register.filter(name='get_status_action')
def get_status_action(obj):
    return Status.getActionFromStatus(obj)