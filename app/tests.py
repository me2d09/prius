"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".
"""

import django
from django.test import TestCase
import unittest
from django.urls import reverse
from django.test import Client
from .models import Proposals, Instruments, Contacts, Affiliations, Countries, InstrumentRequest, Options, SharedOptions, InstrumentParameterSets, InstrumentParameters, ParameterValues, Samples, SamplePhotos, SampleRemarks, Publication, Experiments, Slots
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType

# TODO: Configure your database in settings.py and sync before running tests.

class ViewTest(TestCase):
    """Tests for the application views."""

    if django.VERSION[:2] >= (1, 7):
        # Django 1.7 requires an explicit setup() when running tests in PTVS
        @classmethod
        def setUpClass(cls):
            super(ViewTest, cls).setUpClass()
            django.setup()

    def test_home(self):
        """Tests the home page."""
        response = self.client.get('/')
        self.assertContains(response, 'Home Page', 1, 200)

    def test_contact(self):
        """Tests the contact page."""
        response = self.client.get('/contact')
        self.assertContains(response, 'Contact', 3, 200)

    def test_about(self):
        """Tests the about page."""
        response = self.client.get('/about')
        self.assertContains(response, 'About', 3, 200)


def create_django_contrib_auth_models_user(**kwargs):
    defaults = {}
    defaults["username"] = "username"
    defaults["email"] = "username@tempurl.com"
    defaults.update(**kwargs)
    return User.objects.create(**defaults)


def create_django_contrib_auth_models_group(**kwargs):
    defaults = {}
    defaults["name"] = "group"
    defaults.update(**kwargs)
    return Group.objects.create(**defaults)


def create_django_contrib_contenttypes_models_contenttype(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return ContentType.objects.create(**defaults)


def create_proposals(**kwargs):
    defaults = {}
    defaults["name"] = "name"
    defaults["abstract"] = "abstract"
    defaults["scientific_bg"] = "scientific_bg"
    defaults.update(**kwargs)
    if "proposer" not in defaults:
        defaults["proposer"] = create_contacts()
    if "samples" not in defaults:
        defaults["samples"] = create_samples()
    if "local_contact" not in defaults:
        defaults["local_contact"] = create_contacts()
    if "coproposers" not in defaults:
        defaults["coproposers"] = create_contacts()
    if "publications" not in defaults:
        defaults["publications"] = create_publications()
    return Proposals.objects.create(**defaults)


def create_instruments(**kwargs):
    defaults = {}
    defaults["name"] = "name"
    defaults["public"] = "public"
    defaults["active"] = "active"
    defaults["description"] = "description"
    defaults["time_to_schedule"] = "time_to_schedule"
    defaults.update(**kwargs)
    if "local_contacts" not in defaults:
        defaults["local_contacts"] = create_contacts()
    if "admins" not in defaults:
        defaults["admins"] = create_contacts()
    if "parameter_set" not in defaults:
        defaults["parameter_set"] = create_instrumentparametersets()
    return Instruments.objects.create(**defaults)


def create_contacts(**kwargs):
    defaults = {}
    defaults["name"] = "name"
    defaults["email"] = "email"
    defaults["orcid"] = "orcid"
    defaults.update(**kwargs)
    if "uid" not in defaults:
        defaults["uid"] = create_settings_auth_user_model()
    if "affiliation" not in defaults:
        defaults["affiliation"] = create_affiliations()
    return Contacts.objects.create(**defaults)


def create_affiliations(**kwargs):
    defaults = {}
    defaults["department"] = "department"
    defaults["institution"] = "institution"
    defaults["address1"] = "address1"
    defaults["address2"] = "address2"
    defaults["city"] = "city"
    defaults.update(**kwargs)
    if "country" not in defaults:
        defaults["country"] = create_countries()
    return Affiliations.objects.create(**defaults)


def create_countries(**kwargs):
    defaults = {}
    defaults["name"] = "name"
    defaults["iso"] = "iso"
    defaults.update(**kwargs)
    return Countries.objects.create(**defaults)


def create_instrumentrequest(**kwargs):
    defaults = {}
    defaults["requested"] = "requested"
    defaults["granted"] = "granted"
    defaults.update(**kwargs)
    if "instrument" not in defaults:
        defaults["instrument"] = create_instruments()
    if "propsal" not in defaults:
        defaults["propsal"] = create_proposals()
    if "option" not in defaults:
        defaults["option"] = create_options()
    if "shared_options" not in defaults:
        defaults["shared_options"] = create_sharedoptions()
    return InstrumentRequest.objects.create(**defaults)


def create_options(**kwargs):
    defaults = {}
    defaults["name"] = "name"
    defaults["slug"] = "slug"
    defaults["active"] = "active"
    defaults.update(**kwargs)
    if "instrument" not in defaults:
        defaults["instrument"] = create_instruments()
    return Options.objects.create(**defaults)


def create_sharedoptions(**kwargs):
    defaults = {}
    defaults["name"] = "name"
    defaults["slug"] = "slug"
    defaults["active"] = "active"
    defaults.update(**kwargs)
    if "instruments" not in defaults:
        defaults["instruments"] = create_instruments()
    return SharedOptions.objects.create(**defaults)


def create_instrumentparametersets(**kwargs):
    defaults = {}
    defaults["name"] = "name"
    defaults.update(**kwargs)
    return InstrumentParameterSets.objects.create(**defaults)


def create_instrumentparameters(**kwargs):
    defaults = {}
    defaults["name"] = "name"
    defaults["description"] = "description"
    defaults["required"] = "required"
    defaults.update(**kwargs)
    if "set" not in defaults:
        defaults["set"] = create_instrumentparametersets()
    return InstrumentParameters.objects.create(**defaults)


def create_parametervalues(**kwargs):
    defaults = {}
    defaults["value"] = "value"
    defaults.update(**kwargs)
    if "parameter" not in defaults:
        defaults["parameter"] = create_instrumentparameters()
    if "request" not in defaults:
        defaults["request"] = create_instrumentrequest()
    return ParameterValues.objects.create(**defaults)


def create_samples(**kwargs):
    defaults = {}
    defaults["name"] = "name"
    defaults["formula"] = "formula"
    defaults["mass"] = "mass"
    defaults["volume"] = "volume"
    defaults["description"] = "description"
    defaults["type"] = "type"
    defaults.update(**kwargs)
    if "owner" not in defaults:
        defaults["owner"] = create_contacts()
    return Samples.objects.create(**defaults)


def create_samplephotos(**kwargs):
    defaults = {}
    defaults["url"] = "url"
    defaults.update(**kwargs)
    if "sample" not in defaults:
        defaults["sample"] = create_samples()
    return SamplePhotos.objects.create(**defaults)


def create_sampleremarks(**kwargs):
    defaults = {}
    defaults["remark"] = "remark"
    defaults.update(**kwargs)
    if "sample" not in defaults:
        defaults["sample"] = create_samples()
    if "creator" not in defaults:
        defaults["creator"] = create_contacts()
    return SampleRemarks.objects.create(**defaults)


def create_publications(**kwargs):
    defaults = {}
    defaults["link"] = "link"
    defaults["year"] = "year"
    defaults.update(**kwargs)
    if "authors" not in defaults:
        defaults["authors"] = create_contacts()
    return Publication.objects.create(**defaults)


def create_experiments(**kwargs):
    defaults = {}
    defaults["start"] = "start"
    defaults["end"] = "end"
    defaults["duration"] = "duration"
    defaults["finalized"] = "finalized"
    defaults.update(**kwargs)
    if "request" not in defaults:
        defaults["request"] = create_instrumentrequest()
    if "local_contact" not in defaults:
        defaults["local_contact"] = create_contacts()
    if "instrument" not in defaults:
        defaults["instrument"] = create_instruments()
    if "creator" not in defaults:
        defaults["creator"] = create_contacts()
    return Experiments.objects.create(**defaults)


def create_slots(**kwargs):
    defaults = {}
    defaults["start"] = "start"
    defaults["end"] = "end"
    defaults["type"] = "type"
    defaults.update(**kwargs)
    if "instrument" not in defaults:
        defaults["instrument"] = create_instruments()
    if "creator" not in defaults:
        defaults["creator"] = create_contacts()
    return Slots.objects.create(**defaults)


class ProposalsViewTest(unittest.TestCase):
    '''
    Tests for Proposals
    '''
    def setUp(self):
        self.client = Client()

    def test_list_proposals(self):
        url = reverse('app_proposals_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_proposals(self):
        url = reverse('app_proposals_create')
        data = {
            "name": "name",
            "abstract": "abstract",
            "scientific_bg": "scientific_bg",
            "proposer": create_contacts().pk,
            "samples": create_samples().pk,
            "local_contact": create_contacts().pk,
            "coproposers": create_contacts().pk,
            "publications": create_publications().pk,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_detail_proposals(self):
        proposals = create_proposals()
        url = reverse('app_proposals_detail', args=[proposals.slug,])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_proposals(self):
        proposals = create_proposals()
        data = {
            "name": "name",
            "abstract": "abstract",
            "scientific_bg": "scientific_bg",
            "proposer": create_contacts().pk,
            "samples": create_samples().pk,
            "local_contact": create_contacts().pk,
            "coproposers": create_contacts().pk,
            "publications": create_publications().pk,
        }
        url = reverse('app_proposals_update', args=[proposals.slug,])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)


class InstrumentsViewTest(unittest.TestCase):
    '''
    Tests for Instruments
    '''
    def setUp(self):
        self.client = Client()

    def test_list_instruments(self):
        url = reverse('app_instruments_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_instruments(self):
        url = reverse('app_instruments_create')
        data = {
            "name": "name",
            "public": "public",
            "active": "active",
            "description": "description",
            "time_to_schedule": "time_to_schedule",
            "local_contacts": create_contacts().pk,
            "admins": create_contacts().pk,
            "parameter_set": create_instrumentparametersets().pk,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_detail_instruments(self):
        instruments = create_instruments()
        url = reverse('app_instruments_detail', args=[instruments.slug,])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_instruments(self):
        instruments = create_instruments()
        data = {
            "name": "name",
            "public": "public",
            "active": "active",
            "description": "description",
            "time_to_schedule": "time_to_schedule",
            "local_contacts": create_contacts().pk,
            "admins": create_contacts().pk,
            "parameter_set": create_instrumentparametersets().pk,
        }
        url = reverse('app_instruments_update', args=[instruments.slug,])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)


class ContactsViewTest(unittest.TestCase):
    '''
    Tests for Contacts
    '''
    def setUp(self):
        self.client = Client()

    def test_list_contacts(self):
        url = reverse('app_contacts_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_contacts(self):
        url = reverse('app_contacts_create')
        data = {
            "name": "name",
            "email": "email",
            "orcid": "orcid",
            "uid": create_settings_auth_user_model().pk,
            "affiliation": create_affiliations().pk,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_detail_contacts(self):
        contacts = create_contacts()
        url = reverse('app_contacts_detail', args=[contacts.pk,])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_contacts(self):
        contacts = create_contacts()
        data = {
            "name": "name",
            "email": "email",
            "orcid": "orcid",
            "uid": create_settings_auth_user_model().pk,
            "affiliation": create_affiliations().pk,
        }
        url = reverse('app_contacts_update', args=[contacts.pk,])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)


class AffiliationsViewTest(unittest.TestCase):
    '''
    Tests for Affiliations
    '''
    def setUp(self):
        self.client = Client()

    def test_list_affiliations(self):
        url = reverse('app_affiliations_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_affiliations(self):
        url = reverse('app_affiliations_create')
        data = {
            "department": "department",
            "institution": "institution",
            "address1": "address1",
            "address2": "address2",
            "city": "city",
            "country": create_countries().pk,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_detail_affiliations(self):
        affiliations = create_affiliations()
        url = reverse('app_affiliations_detail', args=[affiliations.pk,])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_affiliations(self):
        affiliations = create_affiliations()
        data = {
            "department": "department",
            "institution": "institution",
            "address1": "address1",
            "address2": "address2",
            "city": "city",
            "country": create_countries().pk,
        }
        url = reverse('app_affiliations_update', args=[affiliations.pk,])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)


class CountriesViewTest(unittest.TestCase):
    '''
    Tests for Countries
    '''
    def setUp(self):
        self.client = Client()

    def test_list_countries(self):
        url = reverse('app_countries_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_countries(self):
        url = reverse('app_countries_create')
        data = {
            "name": "name",
            "iso": "iso",
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_detail_countries(self):
        countries = create_countries()
        url = reverse('app_countries_detail', args=[countries.pk,])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_countries(self):
        countries = create_countries()
        data = {
            "name": "name",
            "iso": "iso",
        }
        url = reverse('app_countries_update', args=[countries.pk,])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)


class InstrumentRequestViewTest(unittest.TestCase):
    '''
    Tests for InstrumentRequest
    '''
    def setUp(self):
        self.client = Client()

    def test_list_instrumentrequest(self):
        url = reverse('app_instrumentrequest_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_instrumentrequest(self):
        url = reverse('app_instrumentrequest_create')
        data = {
            "requested": "requested",
            "granted": "granted",
            "instrument": create_instruments().pk,
            "propsal": create_proposals().pk,
            "option": create_options().pk,
            "shared_options": create_sharedoptions().pk,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_detail_instrumentrequest(self):
        instrumentrequest = create_instrumentrequest()
        url = reverse('app_instrumentrequest_detail', args=[instrumentrequest.pk,])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_instrumentrequest(self):
        instrumentrequest = create_instrumentrequest()
        data = {
            "requested": "requested",
            "granted": "granted",
            "instrument": create_instruments().pk,
            "propsal": create_proposals().pk,
            "option": create_options().pk,
            "shared_options": create_sharedoptions().pk,
        }
        url = reverse('app_instrumentrequest_update', args=[instrumentrequest.pk,])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)


class OptionsViewTest(unittest.TestCase):
    '''
    Tests for Options
    '''
    def setUp(self):
        self.client = Client()

    def test_list_options(self):
        url = reverse('app_options_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_options(self):
        url = reverse('app_options_create')
        data = {
            "name": "name",
            "slug": "slug",
            "active": "active",
            "instrument": create_instruments().pk,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_detail_options(self):
        options = create_options()
        url = reverse('app_options_detail', args=[options.slug,])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_options(self):
        options = create_options()
        data = {
            "name": "name",
            "slug": "slug",
            "active": "active",
            "instrument": create_instruments().pk,
        }
        url = reverse('app_options_update', args=[options.slug,])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)


class SharedOptionsViewTest(unittest.TestCase):
    '''
    Tests for SharedOptions
    '''
    def setUp(self):
        self.client = Client()

    def test_list_sharedoptions(self):
        url = reverse('app_sharedoptions_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_sharedoptions(self):
        url = reverse('app_sharedoptions_create')
        data = {
            "name": "name",
            "slug": "slug",
            "active": "active",
            "instruments": create_instruments().pk,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_detail_sharedoptions(self):
        sharedoptions = create_sharedoptions()
        url = reverse('app_sharedoptions_detail', args=[sharedoptions.slug,])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_sharedoptions(self):
        sharedoptions = create_sharedoptions()
        data = {
            "name": "name",
            "slug": "slug",
            "active": "active",
            "instruments": create_instruments().pk,
        }
        url = reverse('app_sharedoptions_update', args=[sharedoptions.slug,])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)


class InstrumentParameterSetsViewTest(unittest.TestCase):
    '''
    Tests for InstrumentParameterSets
    '''
    def setUp(self):
        self.client = Client()

    def test_list_instrumentparametersets(self):
        url = reverse('app_instrumentparametersets_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_instrumentparametersets(self):
        url = reverse('app_instrumentparametersets_create')
        data = {
            "name": "name",
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_detail_instrumentparametersets(self):
        instrumentparametersets = create_instrumentparametersets()
        url = reverse('app_instrumentparametersets_detail', args=[instrumentparametersets.pk,])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_instrumentparametersets(self):
        instrumentparametersets = create_instrumentparametersets()
        data = {
            "name": "name",
        }
        url = reverse('app_instrumentparametersets_update', args=[instrumentparametersets.pk,])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)


class InstrumentParametersViewTest(unittest.TestCase):
    '''
    Tests for InstrumentParameters
    '''
    def setUp(self):
        self.client = Client()

    def test_list_instrumentparameters(self):
        url = reverse('app_instrumentparameters_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_instrumentparameters(self):
        url = reverse('app_instrumentparameters_create')
        data = {
            "name": "name",
            "description": "description",
            "required": "required",
            "set": create_instrumentparametersets().pk,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_detail_instrumentparameters(self):
        instrumentparameters = create_instrumentparameters()
        url = reverse('app_instrumentparameters_detail', args=[instrumentparameters.pk,])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_instrumentparameters(self):
        instrumentparameters = create_instrumentparameters()
        data = {
            "name": "name",
            "description": "description",
            "required": "required",
            "set": create_instrumentparametersets().pk,
        }
        url = reverse('app_instrumentparameters_update', args=[instrumentparameters.pk,])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)


class ParameterValuesViewTest(unittest.TestCase):
    '''
    Tests for ParameterValues
    '''
    def setUp(self):
        self.client = Client()

    def test_list_parametervalues(self):
        url = reverse('app_parametervalues_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_parametervalues(self):
        url = reverse('app_parametervalues_create')
        data = {
            "value": "value",
            "parameter": create_instrumentparameters().pk,
            "request": create_instrumentrequest().pk,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_detail_parametervalues(self):
        parametervalues = create_parametervalues()
        url = reverse('app_parametervalues_detail', args=[parametervalues.pk,])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_parametervalues(self):
        parametervalues = create_parametervalues()
        data = {
            "value": "value",
            "parameter": create_instrumentparameters().pk,
            "request": create_instrumentrequest().pk,
        }
        url = reverse('app_parametervalues_update', args=[parametervalues.pk,])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)


class SamplesViewTest(unittest.TestCase):
    '''
    Tests for Samples
    '''
    def setUp(self):
        self.client = Client()

    def test_list_samples(self):
        url = reverse('app_samples_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_samples(self):
        url = reverse('app_samples_create')
        data = {
            "name": "name",
            "formula": "formula",
            "mass": "mass",
            "volume": "volume",
            "description": "description",
            "type": "type",
            "owner": create_contacts().pk,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_detail_samples(self):
        samples = create_samples()
        url = reverse('app_samples_detail', args=[samples.pk,])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_samples(self):
        samples = create_samples()
        data = {
            "name": "name",
            "formula": "formula",
            "mass": "mass",
            "volume": "volume",
            "description": "description",
            "type": "type",
            "owner": create_contacts().pk,
        }
        url = reverse('app_samples_update', args=[samples.pk,])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)


class SamplePhotosViewTest(unittest.TestCase):
    '''
    Tests for SamplePhotos
    '''
    def setUp(self):
        self.client = Client()

    def test_list_samplephotos(self):
        url = reverse('app_samplephotos_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_samplephotos(self):
        url = reverse('app_samplephotos_create')
        data = {
            "url": "url",
            "sample": create_samples().pk,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_detail_samplephotos(self):
        samplephotos = create_samplephotos()
        url = reverse('app_samplephotos_detail', args=[samplephotos.pk,])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_samplephotos(self):
        samplephotos = create_samplephotos()
        data = {
            "url": "url",
            "sample": create_samples().pk,
        }
        url = reverse('app_samplephotos_update', args=[samplephotos.pk,])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)


class SampleRemarksViewTest(unittest.TestCase):
    '''
    Tests for SampleRemarks
    '''
    def setUp(self):
        self.client = Client()

    def test_list_sampleremarks(self):
        url = reverse('app_sampleremarks_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_sampleremarks(self):
        url = reverse('app_sampleremarks_create')
        data = {
            "remark": "remark",
            "sample": create_samples().pk,
            "creator": create_contacts().pk,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_detail_sampleremarks(self):
        sampleremarks = create_sampleremarks()
        url = reverse('app_sampleremarks_detail', args=[sampleremarks.pk,])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_sampleremarks(self):
        sampleremarks = create_sampleremarks()
        data = {
            "remark": "remark",
            "sample": create_samples().pk,
            "creator": create_contacts().pk,
        }
        url = reverse('app_sampleremarks_update', args=[sampleremarks.pk,])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)


class PublicationViewTest(unittest.TestCase):
    '''
    Tests for Publication
    '''
    def setUp(self):
        self.client = Client()

    def test_list_publication(self):
        url = reverse('app_publication_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_publication(self):
        url = reverse('app_publication_create')
        data = {
            "link": "link",
            "year": "year",
            "authors": create_contacts().pk,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_detail_publication(self):
        publication = create_publication()
        url = reverse('app_publication_detail', args=[publication.pk,])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_publication(self):
        publication = create_publication()
        data = {
            "link": "link",
            "year": "year",
            "authors": create_contacts().pk,
        }
        url = reverse('app_publication_update', args=[publication.pk,])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)


class ExperimentsViewTest(unittest.TestCase):
    '''
    Tests for Experiments
    '''
    def setUp(self):
        self.client = Client()

    def test_list_experiments(self):
        url = reverse('app_experiments_calendar')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_experiments(self):
        url = reverse('app_experiments_create')
        data = {
            "start": "start",
            "end": "end",
            "duration": "duration",
            "finalized": "finalized",
            "request": create_instrumentrequest().pk,
            "local_contact": create_contacts().pk,
            "instrument": create_instruments().pk,
            "creator": create_contacts().pk,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_detail_experiments(self):
        experiments = create_experiments()
        url = reverse('app_experiments_detail', args=[experiments.pk,])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_experiments(self):
        experiments = create_experiments()
        data = {
            "start": "start",
            "end": "end",
            "duration": "duration",
            "finalized": "finalized",
            "request": create_instrumentrequest().pk,
            "local_contact": create_contacts().pk,
            "instrument": create_instruments().pk,
            "creator": create_contacts().pk,
        }
        url = reverse('app_experiments_update', args=[experiments.pk,])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)


class SlotsViewTest(unittest.TestCase):
    '''
    Tests for Slots
    '''
    def setUp(self):
        self.client = Client()

    def test_list_slots(self):
        url = reverse('app_slots_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_slots(self):
        url = reverse('app_slots_create')
        data = {
            "start": "start",
            "end": "end",
            "type": "type",
            "instrument": create_instruments().pk,
            "creator": create_contacts().pk,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_detail_slots(self):
        slots = create_slots()
        url = reverse('app_slots_detail', args=[slots.pk,])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_slots(self):
        slots = create_slots()
        data = {
            "start": "start",
            "end": "end",
            "type": "type",
            "instrument": create_instruments().pk,
            "creator": create_contacts().pk,
        }
        url = reverse('app_slots_update', args=[slots.pk,])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)


