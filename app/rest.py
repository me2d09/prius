from django.contrib.auth.models import User
from django.db.models import Q

from app.models import Proposals

from rest_framework import generics, permissions, serializers
from rest_framework.response import Response


# first we define the serializers
class ProposalSerializer(serializers.ModelSerializer):
    proposal = serializers.CharField(source='pid')
    title = serializers.CharField(source='name')
    users = serializers.SerializerMethodField()
    localcontacts = serializers.SerializerMethodField()

    class Meta:
        model = Proposals
        fields = ('proposal', 'title', 'users', 'localcontacts')

    def get_users(self, obj):
        userlist = [{ 'id': obj.proposer.contact.pk,
                      'name': obj.proposer.contact.name,
                      'email': obj.proposer.contact.email,
                      'affiliation': str(obj.proposer.contact.affiliation),
                   }]
        for u in obj.coproposers.all():
            userlist.append({
                    'id': u.pk,
                    'name': u.name,
                    'email': u.email,
                    'affiliation': str(u.affiliation),
                })
        if obj.supervisor:
            userlist.append({
                    'id': obj.supervisor.pk,
                    'name': obj.supervisor.name,
                    'email': obj.supervisor.email,
                    'affiliation': str(obj.supervisor.affiliation),
                })
        return userlist

    def get_localcontacts(self, obj):
        lclist = []
        for u in obj.local_contacts.all():
            lclist.append({
                    'id': u.pk,
                    'name': u.name,
                    'email': u.email,
                    'affiliation': str(u.affiliation),
                })
        return lclist


# API views:
class MyProposalList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        proposals = Proposals.objects.filter(Q(last_status='A') & ( 
                                       Q(proposer=request.user) | 
                                       Q(coproposers__uid__exact=request.user) | 
                                       Q(local_contacts__uid__exact=request.user))).distinct()
        serializer = ProposalSerializer(proposals, many=True)
        return Response(serializer.data)
    
    queryset = Proposals.objects.all()
