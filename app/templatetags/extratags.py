from django import template
from app.models import Status

register = template.Library() 

def get_full_group(short):
    if short == "L": return "localcontacts"
    elif short == "P": return "panel"
    elif short == "H": return "panelhead"
    elif short == "D": return "director"
    elif short == "U": return "useroffice"
    elif short == "A": return "admins"
    else: return short


@register.filter(name='has_group') 
def has_group(user, group_name):
    if len(group_name) > 1 and group_name[1] == "_": group_name = get_full_group(group_name[0].upper())
    return user.groups.filter(name=group_name).exists() 

@register.filter(name='get_status_action')
def get_status_action(obj):
    return Status.getActionFromStatus(obj)