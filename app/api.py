from . import models
from . import serializers
from rest_framework import viewsets, permissions


class ProposalsViewSet(viewsets.ModelViewSet):
    """ViewSet for the Proposals class"""

    queryset = models.Proposals.objects.all()
    serializer_class = serializers.ProposalsSerializer
    permission_classes = [permissions.IsAuthenticated]


class InstrumentsViewSet(viewsets.ModelViewSet):
    """ViewSet for the Instruments class"""

    queryset = models.Instruments.objects.all()
    serializer_class = serializers.InstrumentsSerializer
    permission_classes = [permissions.IsAuthenticated]


class ContactsViewSet(viewsets.ModelViewSet):
    """ViewSet for the Contacts class"""

    queryset = models.Contacts.objects.all()
    serializer_class = serializers.ContactsSerializer
    permission_classes = [permissions.IsAuthenticated]


class AffiliationsViewSet(viewsets.ModelViewSet):
    """ViewSet for the Affiliations class"""

    queryset = models.Affiliations.objects.all()
    serializer_class = serializers.AffiliationsSerializer
    permission_classes = [permissions.IsAuthenticated]


class CountriesViewSet(viewsets.ModelViewSet):
    """ViewSet for the Countries class"""

    queryset = models.Countries.objects.all()
    serializer_class = serializers.CountriesSerializer
    permission_classes = [permissions.IsAuthenticated]




class OptionsViewSet(viewsets.ModelViewSet):
    """ViewSet for the Options class"""

    queryset = models.Options.objects.all()
    serializer_class = serializers.OptionsSerializer
    permission_classes = [permissions.IsAuthenticated]


class SharedOptionsViewSet(viewsets.ModelViewSet):
    """ViewSet for the SharedOptions class"""

    queryset = models.SharedOptions.objects.all()
    serializer_class = serializers.SharedOptionsSerializer
    permission_classes = [permissions.IsAuthenticated]


class SamplesViewSet(viewsets.ModelViewSet):
    """ViewSet for the Samples class"""

    queryset = models.Samples.objects.all()
    serializer_class = serializers.SamplesSerializer
    permission_classes = [permissions.IsAuthenticated]


class SamplePhotosViewSet(viewsets.ModelViewSet):
    """ViewSet for the SamplePhotos class"""

    queryset = models.SamplePhotos.objects.all()
    serializer_class = serializers.SamplePhotosSerializer
    permission_classes = [permissions.IsAuthenticated]


class SampleRemarksViewSet(viewsets.ModelViewSet):
    """ViewSet for the SampleRemarks class"""

    queryset = models.SampleRemarks.objects.all()
    serializer_class = serializers.SampleRemarksSerializer
    permission_classes = [permissions.IsAuthenticated]


class PublicationsViewSet(viewsets.ModelViewSet):
    """ViewSet for the Publications class"""

    queryset = models.Publications.objects.all()
    serializer_class = serializers.PublicationsSerializer
    permission_classes = [permissions.IsAuthenticated]


class ExperimentsViewSet(viewsets.ModelViewSet):
    """ViewSet for the Experiments class"""

    queryset = models.Experiments.objects.all()
    serializer_class = serializers.ExperimentsSerializer
    permission_classes = [permissions.IsAuthenticated]
