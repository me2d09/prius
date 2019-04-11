"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from .models import Proposals, Instruments, Contacts, Affiliations, Countries, InstrumentRequest, Options, SharedOptions
from .models import InstrumentParameterSets, InstrumentParameters, ParameterValues, Samples, SamplePhotos, SampleRemarks
from .models import Publications, Experiments, Slots, Status
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from dal import autocomplete
from django.http import Http404
 

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

class CrispyPasswordReset(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(CrispyPasswordReset, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Request password reset'))
        
class CrispySetPassword(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(CrispySetPassword, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Set new password'))
        


class StatusForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(StatusForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.field_class = 'col-sm-10'
        self.helper.label_class = 'col-sm-2'

        #restrict possible statuses

        prop = self.initial['proposal']
        
        allowed = []
        showRemark = False
        showHidden = False
        if self.user.has_perm('app.add_proposals') and prop.proposer == self.user:
            if prop.last_status == 'P': allowed.append('S')  # will be waiting user office
            if prop.last_status == 'A': allowed.append('F')  # will be finished
        if self.user.has_perm('app.change_status'):
            showRemark = showHidden = True
            if prop.last_status == 'S': allowed.append('U')  # will be waiting for panel
            if prop.last_status == 'U': allowed.append('P')  # will be returned
            if prop.last_status == 'U': allowed.append('T')  # will be waiting for local contact
            #if prop.last_status == 'T': allowed.append('P')  # go back to preparation
            if prop.last_status == 'T': allowed.append('W')  # will wait for panel
            if prop.last_status == 'W': allowed.append('R')  # will be in panel
            if prop.last_status == 'A': allowed.append('F')  # will be finished
        if self.user.has_perm('app.approve_technical'): 
            if prop.last_status == 'T': 
                allowed.append('W')  # will be waiting for panel
                showRemark = showHidden = True
        if self.user.has_perm('app.takeover_panel'): 
            if prop.last_status == 'W': allowed.append('R')     # will be in panel
        if self.user.has_perm('app.approve_panel'): 
            if prop.last_status == 'R': 
                allowed.append('D')      # will be by director
                allowed.append('X')      # will be rejected permanently
                allowed.append('P')      # will be in preparation
                self.info = "Please fill-in remark (visible to user) and optionaly hidden remark (for internal purposes)."
                showRemark = showHidden = True
        if self.user.has_perm('app.approve_director'): 
            if prop.last_status == 'D': 
                allowed.append('A')   # will be accepted
                allowed.append('X')   # will be rejected permanently
                self.info = "This is the last step in proposal evaluation. It is possible (but not needed) to fill-in remark (visible to user) and optionaly hidden remark (for internal purposes)."
                showRemark = showHidden = True
        if self.user.has_perm('app.finish_proposal'): 
            if prop.last_status == 'A': 
                allowed.append('F')  # will be finished
                showRemark = True

        self.fields["status"].choices = [c for c in self.fields["status"].choices if c[0] in allowed]
        c = self.fields["status"].choices
        self.ConfirmText = "Confirm"
        if len(c) == 0: raise Http404
        if len(c) == 1:
            if c[0][0] == "S": 
                self.ConfirmText = "Submit proposal"
                self.info = "Do you really want to submit this proposal? You will not be able to edit it anymore."
            if c[0][0] == "F": 
                self.ConfirmText = "Finish proposal"
                self.info = "Do you really want to finish this proposal? It will be archived and you will not be able to book measurements for it anymore."
            if c[0][0] == "U": self.ConfirmText = "Takeover proposal"
            if c[0][0] == "W": 
                self.ConfirmText = "Submit technical remarks"
                self.info = """Please, fill-in comments for the panel to the 'Hidden Remark' field, user will not see this. You can optionally also write some comments to the Remark section and user (and panel) will see it, but it is not necessary.
               Proposal will go immediatelly for review to the panel after pressing Submit."""
            if c[0][0] == "R": 
                self.ConfirmText = "Takeover proposal"
                # TODO: do selection of referees
        if not showRemark: self.fields.pop("remark")
        if not showHidden: self.fields.pop("hiddenremark")

    def save(self, *args, **kwargs):
       kwargs['commit']=False
       obj = super(StatusForm, self).save(*args, **kwargs)
       obj.proposal = self.initial['proposal']
       obj.save()
       return obj

    class Meta:
        model = Status
        fields = ['status', 'remark', 'hiddenremark']
        labels = {
            "status": "New status",
            "hiddenremark": "Hidden Remark",
        }


class ProposalsForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.user = kwargs.pop('user', None)
        self.status = kwargs.pop('status', None)

        super(ProposalsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.field_class = 'col-sm-10'
        self.helper.label_class = 'col-sm-2'

        self.helper.add_input(Submit('submit', 'Save'))
        
        self.fields['local_contact'].widget.attrs = {
            'data-theme': 'bootstrap4',
        }
        self.fields['coproposers'].widget.attrs = {
            'data-theme': 'bootstrap4',
        }
        self.fields['supervisor'].widget.attrs = {
            'data-theme': 'bootstrap4',
        }
        self.fields['student'].widget.attrs['onclick'] = "javascript:toggleDiv('div_id_supervisor');"
        if not self.user.groups.filter(name='localcontacts').exists():
            self.fields["proposaltype"].choices = [t for t in self.fields["proposaltype"].choices if t[0] != 'T']  #remove test proposal
        if self.status and self.status != "P":
            for f in self.fields.values():
                f.disabled = True
            # user office can change some stuff
            if self.user.has_perm('change_status') and self.status in "SU":
                self.fields['local_contact'].disabled = False
                self.fields['proposaltype'].disabled = False
            if self.user.has_perm('approve_technical') and self.status == "T":
                self.fields['local_contact'].disabled = False
            if self.status == "A":
                self.fields['coproposers'].disabled = False

      
    def save(self, *args, **kwargs):
       kwargs['commit']=False
       obj = super(ProposalsForm, self).save(*args, **kwargs)
       if self.request:
           obj.user = self.request.user
       obj.save()
       self.save_m2m()
       return obj

    class Meta:
        model = Proposals
        fields = ['name', 'abstract', 'scientific_bg', 'proposaltype', 'student', 'supervisor', 'local_contact', 'coproposers']
        labels = {
            "name": "Proposal name",
            "proposaltype": "Type of proposal",
            "coproposers": "Experimental team",
            "scientific_bg": "Scientific background",
            "local_contact": "Local contact",
            "student": "Student proposal",
        }
        widgets = {
            'scientific_bg': forms.FileInput(attrs={'accept':'.pdf, application/pdf'}),
            'local_contact': autocomplete.ModelSelect2(url='localcontacts-autocomplete',
                                                       attrs={
                                                            'data-placeholder': 'Choose local contact',
                                                            'width': 'resolve',
                                                       }
                                                       ),
            'supervisor': autocomplete.ModelSelect2(url='contacts-autocomplete',
                                                       attrs={
                                                            'data-placeholder': 'Choose supervisor',
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

class ProfileForm(ContactsForm):
    class Meta(ContactsForm.Meta):
        fields = ['name', 'orcid', 'affiliation']


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


