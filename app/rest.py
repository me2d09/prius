from django.contrib.auth.models import User
from django.db.models import Q

from app.models import Proposals, Publication, Log, Usage, Resource

from rest_framework import generics, permissions, serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view


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
        userlist = [{ 'name': obj.proposer.contact.name,
                      'email': obj.proposer.contact.email,
                      'affiliation': str(obj.proposer.contact.affiliation),
                   }]
        for u in obj.coproposers.all():
            userlist.append({
                    'name': u.name,
                    'email': u.email,
                    'affiliation': str(u.affiliation),
                })
        if obj.supervisor:
            userlist.append({
                    'name': obj.supervisor.name,
                    'email': obj.supervisor.email,
                    'affiliation': str(obj.supervisor.affiliation),
                })
        return userlist

    def get_localcontacts(self, obj):
        lclist = []
        for u in obj.local_contacts.all():
            lclist.append({
                    'name': u.name,
                    'email': u.email,
                    'affiliation': str(u.affiliation),
                })
        return lclist


# API views:
class MyProposalList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        proposals = Proposals.objects.filter(Q(last_status='A') & ( 
                                       Q(proposer=request.user) | 
                                       Q(coproposers__uid__exact=request.user) | 
                                       Q(local_contacts__uid__exact=request.user))).distinct()
        serializer = ProposalSerializer(proposals, many=True)
        return Response(serializer.data)
    
    #queryset = User.objects.all()
    #serializer_class = UserSerializer


class PublicationSerializer(serializers.ModelSerializer):
    year = serializers.SerializerMethodField()

    def get_year(self, obj):
        if obj.issued:
            return int(obj.issued.year)
        return None

    class Meta:
        model = Publication
        fields = (
            'created', 'last_updated', 'link', 
            'name', 'journal', 'citations', 'year', 'issued',
            'full_citation', 
        )

class PublicationsList(generics.ListAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = PublicationSerializer
    queryset = Publication.objects.all()


class UsageSerializer(serializers.ModelSerializer):
    resource = serializers.CharField()
    class Meta:
        model = Usage
        fields =('resource', 'amount')

class LogSerializer(serializers.ModelSerializer):
    usage_set = UsageSerializer(many=True)
    proposal = serializers.CharField()

    class Meta:
        model = Log
        fields = (
            'start', 'end', 'instrument', 'localcontact', 'creator', 'proposal', 'usage_set'
        )
        write_only_fields = ['usage_set']
        read_only_fields = ['creator']

    def validate(self, attrs):
        attrs['creator'] = self.context['request'].user.contact
        return attrs

    def create(self, validated_data):
        used_data = validated_data.pop('usage_set')
        proposal = validated_data.pop('proposal')
        validated_data['proposal'] = Proposals.objects.get(pid=proposal)
        log = super().create(validated_data)
        for u in used_data:
            resource = u.pop('resource')
            u['resource'] = Resource.objects.get(name=resource)
            Usage.objects.create(log=log, **u)
        return log

class LogCreate(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    serializer_class = LogSerializer
