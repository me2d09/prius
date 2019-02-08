from django.apps import AppConfig

from django.db.models.signals import post_save

def add_to_default_group(sender, **kwargs):
    from django.contrib.auth.models import User, Group
    user = kwargs["instance"]
    if kwargs["created"]:
        group = Group.objects.get(name='allusers')
        user.groups.add(group)


class PriusConfig(AppConfig):
    name = "app"
    def ready(self):
        from django.contrib.auth.models import User
        post_save.connect(add_to_default_group, sender=User)
