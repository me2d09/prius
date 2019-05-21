from django.contrib import admin
from django import forms
from .models import Proposals, Instruments, Contacts, Affiliations, Countries, InstrumentRequest, Options, SharedOptions, InstrumentParameterSets, InstrumentParameters, ParameterValues, Samples, SamplePhotos, SampleRemarks, Publications, Experiments, Slots, Status

class StatusAdminForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = '__all__'

class StatusAdmin(admin.ModelAdmin):
    form = StatusAdminForm
    list_display = ['date', 'status', 'remark', 'hiddenremark', 'proposal', 'user']
    readonly_fields = ['date']

admin.site.register(Status, StatusAdmin)


class ProposalsAdminForm(forms.ModelForm):

    class Meta:
        model = Proposals
        fields = '__all__'


class ProposalsAdmin(admin.ModelAdmin):
    form = ProposalsAdminForm
    list_display = ['pid', 'slug', 'created', 'proposer', 'last_updated', 'name', 'abstract', 'scientific_bg', 'student', 'supervisor']
    readonly_fields = ['slug', 'created', 'last_updated']

admin.site.register(Proposals, ProposalsAdmin)


class InstrumentsAdminForm(forms.ModelForm):

    class Meta:
        model = Instruments
        fields = '__all__'


class InstrumentsAdmin(admin.ModelAdmin):
    form = InstrumentsAdminForm
    list_display = ['name', 'slug', 'created', 'last_updated', 'public', 'active', 'description', 'time_to_schedule']
    readonly_fields = ['slug', 'created', 'last_updated']

admin.site.register(Instruments, InstrumentsAdmin)


class ContactsAdminForm(forms.ModelForm):

    class Meta:
        model = Contacts
        fields = '__all__'


class ContactsAdmin(admin.ModelAdmin):
    form = ContactsAdminForm
    list_display = ['name', 'created', 'last_updated', 'email', 'orcid', 'description']
    readonly_fields = ['created', 'last_updated']

admin.site.register(Contacts, ContactsAdmin)


class AffiliationsAdminForm(forms.ModelForm):

    class Meta:
        model = Affiliations
        fields = '__all__'


class AffiliationsAdmin(admin.ModelAdmin):
    form = AffiliationsAdminForm
    list_display = ['created', 'last_updated', 'department', 'institution', 'address1', 'address2', 'city']
    readonly_fields = ['created', 'last_updated']

admin.site.register(Affiliations, AffiliationsAdmin)


class CountriesAdminForm(forms.ModelForm):

    class Meta:
        model = Countries
        fields = '__all__'


class CountriesAdmin(admin.ModelAdmin):
    form = CountriesAdminForm
    list_display = ['name', 'iso']

admin.site.register(Countries, CountriesAdmin)


class InstrumentRequestAdminForm(forms.ModelForm):

    class Meta:
        model = InstrumentRequest
        fields = '__all__'


class InstrumentRequestAdmin(admin.ModelAdmin):
    form = InstrumentRequestAdminForm
    list_display = ['requested', 'granted']
    readonly_fields = ['requested', 'granted']

admin.site.register(InstrumentRequest, InstrumentRequestAdmin)


class OptionsAdminForm(forms.ModelForm):

    class Meta:
        model = Options
        fields = '__all__'


class OptionsAdmin(admin.ModelAdmin):
    form = OptionsAdminForm
    list_display = ['name', 'slug', 'created', 'last_updated', 'active']
    readonly_fields = ['name', 'slug', 'created', 'last_updated', 'active']

admin.site.register(Options, OptionsAdmin)


class SharedOptionsAdminForm(forms.ModelForm):

    class Meta:
        model = SharedOptions
        fields = '__all__'


class SharedOptionsAdmin(admin.ModelAdmin):
    form = SharedOptionsAdminForm
    list_display = ['name', 'slug', 'created', 'last_updated', 'active']
    readonly_fields = ['name', 'slug', 'created', 'last_updated', 'active']

admin.site.register(SharedOptions, SharedOptionsAdmin)


class InstrumentParameterSetsAdminForm(forms.ModelForm):

    class Meta:
        model = InstrumentParameterSets
        fields = '__all__'


class InstrumentParameterSetsAdmin(admin.ModelAdmin):
    form = InstrumentParameterSetsAdminForm
    list_display = ['name']

admin.site.register(InstrumentParameterSets, InstrumentParameterSetsAdmin)


class InstrumentParametersAdminForm(forms.ModelForm):

    class Meta:
        model = InstrumentParameters
        fields = '__all__'


class InstrumentParametersAdmin(admin.ModelAdmin):
    form = InstrumentParametersAdminForm
    list_display = ['name', 'description', 'required']
    readonly_fields = ['name', 'description', 'required']

admin.site.register(InstrumentParameters, InstrumentParametersAdmin)


class ParameterValuesAdminForm(forms.ModelForm):

    class Meta:
        model = ParameterValues
        fields = '__all__'


class ParameterValuesAdmin(admin.ModelAdmin):
    form = ParameterValuesAdminForm
    list_display = ['value']
    readonly_fields = ['value']

admin.site.register(ParameterValues, ParameterValuesAdmin)


class SamplesAdminForm(forms.ModelForm):

    class Meta:
        model = Samples
        fields = '__all__'


class SamplesAdmin(admin.ModelAdmin):
    form = SamplesAdminForm
    list_display = ['name', 'created', 'last_updated', 'formula', 'mass', 'volume', 'description', 'type']
    readonly_fields = ['name', 'created', 'last_updated', 'formula', 'mass', 'volume', 'description', 'type']

admin.site.register(Samples, SamplesAdmin)


class SamplePhotosAdminForm(forms.ModelForm):

    class Meta:
        model = SamplePhotos
        fields = '__all__'


class SamplePhotosAdmin(admin.ModelAdmin):
    form = SamplePhotosAdminForm
    list_display = ['created', 'last_updated', 'url']
    readonly_fields = ['created', 'last_updated', 'url']

admin.site.register(SamplePhotos, SamplePhotosAdmin)


class SampleRemarksAdminForm(forms.ModelForm):

    class Meta:
        model = SampleRemarks
        fields = '__all__'


class SampleRemarksAdmin(admin.ModelAdmin):
    form = SampleRemarksAdminForm
    list_display = ['remark', 'created', 'last_updated']
    readonly_fields = ['remark', 'created', 'last_updated']

admin.site.register(SampleRemarks, SampleRemarksAdmin)


class PublicationsAdminForm(forms.ModelForm):

    class Meta:
        model = Publications
        fields = '__all__'


class PublicationsAdmin(admin.ModelAdmin):
    form = PublicationsAdminForm
    list_display = ['created', 'last_updated', 'link', 'year']
    readonly_fields = ['created', 'last_updated', 'link', 'year']

admin.site.register(Publications, PublicationsAdmin)


class ExperimentsAdminForm(forms.ModelForm):

    class Meta:
        model = Experiments
        fields = '__all__'


class ExperimentsAdmin(admin.ModelAdmin):
    form = ExperimentsAdminForm
    list_display = ['created', 'last_updated', 'start', 'end', 'duration', 'finalized']
    readonly_fields = ['created', 'last_updated', 'start', 'end', 'duration', 'finalized']

admin.site.register(Experiments, ExperimentsAdmin)


class SlotsAdminForm(forms.ModelForm):

    class Meta:
        model = Slots
        fields = '__all__'


class SlotsAdmin(admin.ModelAdmin):
    form = SlotsAdminForm
    list_display = ['created', 'last_updated', 'start', 'end', 'type']
    readonly_fields = ['created', 'last_updated', 'start', 'end', 'type']

admin.site.register(Slots, SlotsAdmin)


