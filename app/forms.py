"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from .models import Proposals, Instruments, Contacts, Affiliations, Countries, InstrumentRequest, Options, SharedOptions, InstrumentParameterSets, InstrumentParameters, ParameterValues, Samples, SamplePhotos, SampleRemarks, Publications, Experiments, Slots
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from dal import autocomplete
 

class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""

    def __init__(self, *args, **kwargs):
        super(BootstrapAuthenticationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field('username', placeholder="username"),
            Field('username', placeholder="username"),
            Field('password', placeholder="password"),
        )
        self.helper.add_input(Submit('submit', 'Submit'))


class SignupForm(UserCreationForm):

    email = forms.EmailField(max_length=200, help_text='Required')


    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        # and then the rest as usual:
        self.helper.form_show_labels = False
        self.helper.add_input(Submit('signup', 'Sign Up'))


    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if email and User.objects.filter(email=email).exclude(username=username).exists():
            raise forms.ValidationError(u'This email address is already used. Email addresses must be unique.')
        return email

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        

class ProposalsForm(forms.ModelForm):



    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ProposalsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.field_class = 'col-sm-10'
        self.helper.label_class = 'col-sm-2'

        self.helper.add_input(Submit('submit', 'Submit'))

        self.fields['local_contact'].widget.attrs = {
            'data-theme': 'bootstrap4',
        }
        self.fields['coproposers'].widget.attrs = {
            'data-theme': 'bootstrap4',
        }
      
    def save(self, *args, **kwargs):
       kwargs['commit']=False
       obj = super(ProposalsForm, self).save(*args, **kwargs)
       if self.request:
           obj.user = self.request.user
       obj.save()
       return obj

    class Meta:
        model = Proposals
        fields = ['name', 'abstract', 'scientific_bg', 'proposaltype', 'local_contact', 'coproposers']
        widgets = {
            'scientific_bg': forms.FileInput(attrs={'accept':'.pdf, application/pdf'}),
            'local_contact': autocomplete.ModelSelect2(url='localcontacts-autocomplete',
                                                       attrs={
                                                            'data-placeholder': 'Choose local contact',
                                                            'width': 'resolve',
                                                       }
                                                       ),
            'coproposers': autocomplete.ModelSelect2Multiple(url='contacts-autocomplete',
                                                             attrs={
                                                                'data-placeholder': 'Choose your team',
                                                                'data-minimum-input-length': 1,
                                                                'width': 'resolve',
                                                             }
                                                             )
        }


class InstrumentsForm(forms.ModelForm):
    class Meta:
        model = Instruments
        fields = ['name', 'public', 'active', 'description', 'time_to_schedule', 'local_contacts', 'admins', 'parameter_set']

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if email and (email != self.initial.get('email')) and User.objects.filter(email=email).exclude(username=username).exists():
            raise forms.ValidationError(u'This email address is already used by account %s. Email addresses must be unique.' % User.objects.filter(email=email).exclude(username=username)[0])
        return email


class ProfileForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.field_class = 'col-sm-10'
        self.helper.label_class = 'col-sm-2'

        self.helper.add_input(Submit('submit', 'Submit'))
      
    def save(self, *args, **kwargs):
       kwargs['commit']=False
       obj = super(ProfileForm, self).save(*args, **kwargs)
       if self.request:
           obj.uid = self.request.user
       obj.save()
       return obj

    class Meta:
        model = Contacts
        fields = ['name', 'orcid', 'affiliation']

class ContactsForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ContactsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.field_class = 'col-sm-10'
        self.helper.label_class = 'col-sm-2'

        self.helper.add_input(Submit('submit', 'Submit'))

        self.fields['affiliation'].widget.attrs = {
            'data-theme': 'bootstrap4',
        }

    class Meta:
        model = Contacts
        fields = ['name', 'orcid', 'email', 'affiliation']
        widgets = {
            'affiliation': autocomplete.ModelSelect2(url='affil-autocomplete',
                                                       attrs={
                                                            'data-placeholder': 'Choose institution',
                                                            'width': 'resolve',
                                                       }
                                                       )
        }


class AffiliationsForm(forms.ModelForm):
    class Meta:
        model = Affiliations
        fields = ['department', 'institution', 'address1', 'address2', 'city', 'country']


class CountriesForm(forms.ModelForm):
    class Meta:
        model = Countries
        fields = ['name', 'iso']


class InstrumentRequestForm(forms.ModelForm):
    class Meta:
        model = InstrumentRequest
        fields = ['requested', 'granted', 'instrument', 'propsal', 'option', 'shared_options']


class OptionsForm(forms.ModelForm):
    class Meta:
        model = Options
        fields = ['name', 'active', 'instrument']


class SharedOptionsForm(forms.ModelForm):
    class Meta:
        model = SharedOptions
        fields = ['name', 'active', 'instruments']


class InstrumentParameterSetsForm(forms.ModelForm):
    class Meta:
        model = InstrumentParameterSets
        fields = ['name']


class InstrumentParametersForm(forms.ModelForm):
    class Meta:
        model = InstrumentParameters
        fields = ['name', 'description', 'required', 'set']


class ParameterValuesForm(forms.ModelForm):
    class Meta:
        model = ParameterValues
        fields = ['value', 'parameter', 'request']


class SamplesForm(forms.ModelForm):
    class Meta:
        model = Samples
        fields = ['name', 'formula', 'mass', 'volume', 'description', 'type', 'owner']


class SamplePhotosForm(forms.ModelForm):
    class Meta:
        model = SamplePhotos
        fields = ['url', 'sample']


class SampleRemarksForm(forms.ModelForm):
    class Meta:
        model = SampleRemarks
        fields = ['remark', 'sample', 'creator']


class PublicationsForm(forms.ModelForm):
    class Meta:
        model = Publications
        fields = ['link', 'year', 'authors']


class ExperimentsForm(forms.ModelForm):
    class Meta:
        model = Experiments
        fields = ['start', 'end', 'duration', 'finalized', 'request', 'local_contact', 'instrument', 'creator']


class SlotsForm(forms.ModelForm):
    class Meta:
        model = Slots
        fields = ['start', 'end', 'type', 'instrument', 'creator']


