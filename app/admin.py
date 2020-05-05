from django.contrib import admin
from django import forms
from .models import Proposals, Instruments, Contacts, Affiliations, Countries,  Options, SharedOptions, Samples, SamplePhotos, SampleRemarks, Publications, Experiments, Status, InstrumentGroup, SharedOptionSlot, Report

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
    list_display = ['pid', 'name', 'proposer', 'created', 'last_updated', 'grants', 'scientific_bg', 'supervisor', 'review_process']
    readonly_fields = ['slug', 'created', 'last_updated']

admin.site.register(Proposals, ProposalsAdmin)

class ReportAdminForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = '__all__'

class ReportAdmin(admin.ModelAdmin):
    form = ReportAdminForm
    list_display = ['proposal', 'created', 'last_updated', 'deadline', 'pdf']

admin.site.register(Report, ReportAdmin)


class InstrumentsAdminForm(forms.ModelForm):

    class Meta:
        model = Instruments
        fields = '__all__'

class OptionsInline(admin.TabularInline):
        model = Options
        extra = 15

class InstrumentsAdmin(admin.ModelAdmin):
    form = InstrumentsAdminForm
    list_display = ['name', 'slug', 'created', 'last_updated', 'public', 'active', 'description']
    readonly_fields = ['slug', 'created', 'last_updated']
    inlines = [OptionsInline]

admin.site.register(Instruments, InstrumentsAdmin)



class InstrumentGroupAdminForm(forms.ModelForm):

    class Meta:
        model = InstrumentGroup
        fields = '__all__'

class InstrumentGroupAdmin(admin.ModelAdmin):
    form = InstrumentGroupAdminForm
    list_display = ['name', 'created', 'last_updated']
    readonly_fields = ['created', 'last_updated']
    filter_horizontal = ('trained_users','allowed_LC',) 

admin.site.register(InstrumentGroup, InstrumentGroupAdmin)


class ContactsAdminForm(forms.ModelForm):

    class Meta:
        model = Contacts
        fields = '__all__'


class ContactsAdmin(admin.ModelAdmin):
    form = ContactsAdminForm
    list_display = ['name', 'created', 'last_updated', 'email', 'affiliation', 'description']
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



class OptionsAdminForm(forms.ModelForm):

    class Meta:
        model = Options
        fields = '__all__'


class OptionsAdmin(admin.ModelAdmin):
    form = OptionsAdminForm
    list_display = ['name', 'slug', 'created', 'last_updated', 'active']
    readonly_fields = ['slug', 'created', 'last_updated']

admin.site.register(Options, OptionsAdmin)


class SharedOptionsAdminForm(forms.ModelForm):

    class Meta:
        model = SharedOptions
        fields = '__all__'


class SharedOptionsAdmin(admin.ModelAdmin):
    form = SharedOptionsAdminForm
    list_display = ['name', 'slug', 'created', 'last_updated', 'active']
    readonly_fields = ['slug', 'created', 'last_updated']

admin.site.register(SharedOptions, SharedOptionsAdmin)



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
    list_display = ['instrument', 'proposal', 'created', 'start', 'end', 'duration', 'responsible', 'local_contact', 'all_options']
    readonly_fields = ['created', 'last_updated', 'duration']

admin.site.register(Experiments, ExperimentsAdmin)


class SharedOptionSlotAdminForm(forms.ModelForm):
    class Meta:
        model = SharedOptionSlot
        fields = '__all__'

class SharedOptionSlotAdmin(admin.ModelAdmin):
    form = SharedOptionSlotAdminForm
    list_display = ['created', 'last_updated', 'start', 'end', 'duration']
    readonly_fields = ['created', 'last_updated', 'start', 'end', 'duration']

admin.site.register(SharedOptionSlot, SharedOptionSlotAdmin)

