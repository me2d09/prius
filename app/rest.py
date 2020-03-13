from django.contrib.auth.models import User
from django.db.models import Q

from app.models import Proposals

from rest_framework import generics, permissions, serializers
from rest_framework.response import Response


class WithEmailField(serializers.RelatedField):
    def to_representation(self, value):
        if len(value.all()) > 0:
            first = value.all()[0]
            return '%s <%s>' % (first.name, first.email)
        return ''

class ManyToString(serializers.RelatedField):
    def to_representation(self, value):
        if len(value.all()) > 0:
            return ', '.join([v.name for v in value.all()])
        return ''

class NameForUser(serializers.RelatedField):
    def to_representation(self, value):
        if value.contact:
            return value.contact.name
        return value.name


# first we define the serializers
class ProposalSerializer(serializers.ModelSerializer):
    local_contacts = WithEmailField(read_only=True)
    coproposers = ManyToString(read_only=True)
    proposer = NameForUser(read_only=True)

    class Meta:
        model = Proposals
        fields = ('pid', 'name', 'proposaltype', 'proposer', 'local_contacts', 'coproposers')


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