from . import models

from rest_framework import serializers


class ProposalsSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Proposals
        fields = (
            'slug', 
            'created', 
            'last_updated', 
            'name', 
            'abstract', 
            'scientific_bg', 
        )


class InstrumentsSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Instruments
        fields = (
            'slug', 
            'name', 
            'created', 
            'last_updated', 
            'public', 
            'active', 
            'description', 
            'time_to_schedule', 
        )


class ContactsSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Contacts
        fields = (
            'pk', 
            'name', 
            'created', 
            'last_updated', 
            'email', 
            'orcid', 
        )


class AffiliationsSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Affiliations
        fields = (
            'pk', 
            'created', 
            'last_updated', 
            'department', 
            'institution', 
            'address1', 
            'address2', 
            'city', 
        )


class CountriesSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Countries
        fields = (
            'pk', 
            'name', 
            'iso', 
        )


class OptionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Options
        fields = (
            'slug', 
            'name', 
            'created', 
            'last_updated', 
            'active', 
        )


class SharedOptionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.SharedOptions
        fields = (
            'slug', 
            'name', 
            'created', 
            'last_updated', 
            'active', 
        )



class SamplesSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Samples
        fields = (
            'pk', 
            'name', 
            'created', 
            'last_updated', 
            'formula', 
            'mass', 
            'volume', 
            'description', 
            'type', 
        )


class SamplePhotosSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.SamplePhotos
        fields = (
            'pk', 
            'created', 
            'last_updated', 
            'url', 
        )


class SampleRemarksSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.SampleRemarks
        fields = (
            'pk', 
            'remark', 
            'created', 
            'last_updated', 
        )


class PublicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Publication
        fields = (
            'pk', 
            'created', 
            'last_updated', 
            'link', 
            'year', 
        )


class ExperimentsSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Experiments
        fields = (
            'pk', 
            'created', 
            'last_updated', 
            'start', 
            'end', 
            'duration', 
            'finalized', 
        )
