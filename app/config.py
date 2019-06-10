from django.apps import AppConfig
from django.conf import settings

from django.db.models.signals import post_save
from django.db.models.signals import post_migrate


def add_to_default_group(sender, **kwargs):
    from django.contrib.auth.models import User, Group
    user = kwargs["instance"]
    if kwargs["created"]:
        group = Group.objects.get(name='allusers')
        user.groups.add(group)

def create_notice_types(sender, **kwargs): 
    if "pinax.notifications" in settings.INSTALLED_APPS:
        from pinax.notifications.models import NoticeType
        NoticeType.create("X_proposal_accepted", "Proposal Accepted", "The proposal you have submitted (or you are part of the team) was accepted.")
        NoticeType.create("X_proposal_returned", "Proposal Returned", "The proposal you have submitted (or you are part of the team) was returned.")
        NoticeType.create("X_proposal_rejected", "Proposal Rejected", "The proposal you have submitted (or you are part of the team) was rejected.")
        NoticeType.create("X_proposal_status_changed", "Proposal status changed", "The proposal you have submitted changed the status.", 1)
        NoticeType.create("L_request_technical", "Technical review requested (LC)", "You (as a local contact) need to perform technical check of the proposal.")
        NoticeType.create("l_accepted", "Proposal accepted (LC)", "Proposal, where you are local contact was accepted and can be scheduled.", 1)
        NoticeType.create("P_request_review", "Panel review requested (P)", "You (as a panel member) need to perform review of the proposal.")
        NoticeType.create("H_new_proposal", "Reporter selection requested (PH)", "You (as a panel head) need to assign reporter to the proposal.")
        NoticeType.create("D_accepted", "Director approval needed (D)", "You (as a director) need approve or reject accepted proposal by the panel.")
        NoticeType.create("d_rejected", "Proposal rejected by the panel (D)", "Inform about any rejection of the proposal.", 1)
        NoticeType.create("d_returned", "Proposal returned to user (D)", "Inform about any return of the proposal to the user.", 1)
        NoticeType.create("U_submited", "New proposal submitted (UO)", "New proposal was submitted and user office need to check it.")
        NoticeType.create("a_submited", "New proposal submitted (A)", "Inform about any new submitted proposal.")
        NoticeType.create("a_accepted", "Proposal accepted (A)", "Inform about all proposals accepted by the director.")


class PriusConfig(AppConfig):
    name = "app"
    def ready(self):
        from django.contrib.auth.models import User
        post_save.connect(add_to_default_group, sender=User)
        post_migrate.connect(create_notice_types, sender=self)
