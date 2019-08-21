"""
Definition of forms.
"""

from django import forms
from django.template.loader import render_to_string
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from .models import Proposals, Instruments, Contacts, Affiliations, Countries, Options, SharedOptions
from .models import Samples, SamplePhotos, SampleRemarks
from .models import Publications, Experiments, Status
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, HTML, Fieldset, Div, ButtonHolder, Field
from dal import autocomplete
from django.http import Http404
from django.db.models import Q
 

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
            if prop.last_status == 'P': 
                if prop.proposaltype == 'T':
                    allowed.append('A')  # will be accepted
                else:
                    allowed.append('S')  # will be waiting user office
            if prop.last_status == 'A': allowed.append('F')  # will be finished
        if self.user.has_perm('app.change_status'):
            showRemark = showHidden = True
            if prop.last_status == 'S': allowed.append('U')  # will be waiting for panel
            if prop.last_status == 'U': allowed.append('P')  # will be returned
            if prop.last_status == 'U': allowed.append('T')  # will be waiting for local contact
            #if prop.last_status == 'T': allowed.append('P')  # go back to preparation
            if prop.last_status == 'T': 
                if prop.proposaltype == 'P':
                    allowed.append('D')  # will be waiting for director
                else:
                    allowed.append('W')  # will be waiting for panel
            if prop.last_status == 'W': allowed.append('R')  # will be in panel
            if prop.last_status == 'A': allowed.append('F')  # will be finished
        if self.user.has_perm('app.approve_technical') and self.user.contact in prop.local_contacts.all(): 
            if prop.last_status == 'T': 
                allowed.append('T')  # stay in technical review
                if prop.proposaltype == 'P':
                    allowed.append('D')  # will be waiting for director
                else:
                    allowed.append('W')  # will be waiting for panel
                showRemark = showHidden = True
        if self.user.has_perm('app.takeover_panel') and prop.last_status == 'W': 
                allowed.append('R')     # will be in panel
                showRemark = showHidden = False
        if  self.user.has_perm('app.takeover_panel') or (self.user.has_perm('app.approve_panel') and prop.reporter.uid == self.user): 
            if prop.last_status == 'R':
                allowed.append('D')      # will be by director
                allowed.append('X')      # will be rejected permanently
                allowed.append('P')      # will be in preparation
                self.info = """Please, fill-in panel report and select your decision. You can accept proposal (new status "by director"), 
                return it to user (status "in preparation") or you can completelly reject it (status "rejected").
The panel report has two parts - visible and hidden to the user."""
                self.fields["remark"].label = "Panel report (user will see)"
                self.fields["hiddenremark"].label = "Hidden panel report (user won't see)"
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
                self.fields["hiddenremark"].label = "Technical Review (user won't see)"
                self.info = """Please, fill-in comments (about the feasibility of given proposal from the point of view of instrumentation, technology and expertise of the
team) for the panel to the 'Technical Review' field, user will not see this.
Also, you can optionally write some comments to the "Remarks to user" 
section and user (and panel) will see it (e.g. to improve next proposals). Proposal will go immediately for the review to the Panel after pressing Submit.
"""
            if c[0][0] == "R": 
                self.ConfirmText = "Takeover proposal"
                self.fields['reporter'] = forms.ModelChoiceField(queryset=Contacts.objects.filter(uid__groups__name="panel"))
                # TODO: do selection of referees
        if not showRemark: self.fields.pop("remark")
        if not showHidden: self.fields.pop("hiddenremark")

    def save(self, *args, **kwargs):
       kwargs['commit']=False
       obj = super(StatusForm, self).save(*args, **kwargs)
       obj.proposal = self.initial['proposal']
       if "reporter" in self.cleaned_data:
           obj.proposal.reporter = self.cleaned_data["reporter"]
       obj.proposal.save()
       obj.save()
       return obj

    class Meta:
        model = Status
        fields = ['status', 'remark', 'hiddenremark']
        labels = {
            "status": "New status",
            "hiddenremark": "Hidden Remark (user won't see)",
            "remark": "Remarks to user (user will see)"
        }


class ProposalsForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.user = kwargs.pop('user', None)
        self.status = kwargs.pop('status', None)
        self.local_contacts = kwargs.pop('local_contacts', None)

        super(ProposalsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.field_class = 'col-sm-10'
        self.helper.label_class = 'col-sm-2'
        if self.status:
            cancelbuttoncode = """<a role="button" class="btn btn-default"
                        href="{% url "app_proposals_detail" object.slug %}">Cancel</a>"""
        else:
            cancelbuttoncode = """<a role="button" class="btn btn-default"
                        href="{% url "home" %}">Cancel</a>"""

        self.helper.layout = Layout(
            Fieldset(
                None, 'name', 'abstract', 'scientific_bg', 'proposaltype', 'student', 'thesis_topic', 'supervisor', 'grants', 'local_contacts', 'coproposers'
            ),
            ButtonHolder(
                Submit('submit', 'Save', css_class='button white'),
                HTML(cancelbuttoncode),
            )
        )
        self.fields['name'].help_text = "Enter the name of the proposal, maximum length is 500 characters, however we recommend shorter."
        self.fields['abstract'].help_text = "Mandatory abstract, maximumn length 5000 characters."
        self.fields['proposaltype'].help_text = "Select type of proposal. See <a href=""/how-to/proposal"" target=""_blank"">help</a> for description and how to choose the correct one."
        
        self.fields['local_contacts'].widget.attrs = {
            'data-theme': 'bootstrap4',
        }
        self.fields['local_contacts'].help_text = "You need to select at least one local contact. He/she will do feasibility check of your proposal. More local contacts can be added later if needed."
        self.fields['coproposers'].widget.attrs = {
            'data-theme': 'bootstrap4',
        }
        self.fields['coproposers'].help_text = "You can (optionally) add coporposers to your team. They will see the proposal and will be able to book measurement for it. If the proposal is connected with any funding, <b>PI of the grant MUST be part of the team</b>."
        self.fields['supervisor'].widget.attrs = {
            'data-theme': 'bootstrap4',
        }
        self.fields['grants'].help_text = "If the proposal is connected with any funding, add its abbreviation and/or number. In case of more fundings, separate by comma. Example: <i>'GAČR 19-000123S, ERC BoBEK 123456'</i>."
        self.fields['student'].help_text = "Student proposals needs to mention supervisor and thesis topic."
        self.fields['student'].widget.attrs['onclick'] = "javascript:toggleDivs();"
        if not self.user.groups.filter(name='localcontacts').exists():
            self.fields["proposaltype"].choices = [t for t in self.fields["proposaltype"].choices if t[0] != 'T']  #remove test proposal
        if self.status and self.status != "P":
            for f in self.fields.values():
                f.disabled = True
            # user office can change some stuff
            if self.user.has_perm('app.change_status') and self.status in "SU":
                self.fields['local_contacts'].disabled = False
                self.fields['proposaltype'].disabled = False
            if self.user.has_perm('app.approve_technical') and self.status == "T" and self.user.contact in self.local_contacts.all():
                self.fields['local_contacts'].disabled = False
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
        fields = ['name', 'abstract', 'scientific_bg', 'proposaltype', 'student', 'supervisor', 'thesis_topic', 'local_contacts', 'grants', 'coproposers']
        labels = {
            "name": "Proposal name",
            "proposaltype": "Type of proposal",
            "coproposers": "Experimental team",
            "scientific_bg": "Scientific background",
            "local_contacts": "Local contacts",
            "student": "Student proposal",
        }
        widgets = {
            'scientific_bg': forms.FileInput(attrs={'accept':'.pdf, application/pdf'}),
            'local_contacts': autocomplete.ModelSelect2Multiple(url='localcontacts-autocomplete',
                                                       attrs={
                                                            'data-placeholder': 'Choose local contact',
                                                            'data-minimum-input-length': 1,
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
        fields = ['name', 'public', 'active', 'description']

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



class OptionsForm(forms.ModelForm):
    class Meta:
        model = Options
        fields = ['name', 'active', 'instrument']


class SharedOptionsForm(forms.ModelForm):
    class Meta:
        model = SharedOptions
        fields = ['name', 'active', 'instruments']



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

class DateRangeField(Fieldset):
    template = 'custom_daterange.html'

    def render(self, form, form_style, context, template_pack, **kwargs):
        if len(self.fields) != 2:
            raise ValueError("There needs to be legend and two fields for daterange.")
        return render_to_string(
            self.template,
            {'fieldset': self, 'legend': self.legend, 
             'field1': form[self.fields[0]], 'field2': form[self.fields[1]], 
             'form_style': form_style}
)



class ExperimentsForm(forms.ModelForm):
    start = forms.DateField(widget=forms.DateInput(format = '%d.%m.%Y'), 
                                input_formats=('%d.%m.%Y',))
    end = forms.DateField(widget=forms.DateInput(format = '%d.%m.%Y'), 
                                input_formats=('%d.%m.%Y',))
    class Meta:
        model = Experiments
        fields = ['start', 'end', 'proposal', 'instrument', 'option', 'shared_options', 'local_contact']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.user = kwargs.pop('user', None)
        self.local_contacts = kwargs.pop('local_contacts', None)

        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.field_class = 'col-sm-10'
        self.helper.label_class = 'col-sm-2'

        self.fields['instrument'].queryset = Instruments.objects.filter(group__in = self.user.contact.trained_instrumentgroups.all())

        self.fields['proposal'].queryset = Proposals.objects.filter(Q(last_status='A') & ( 
                                       Q(proposer=self.user) | 
                                       Q(coproposers__uid__exact=self.user) | 
                                       Q(local_contacts__uid__exact=self.user))).distinct()
        
       
        self.fields['local_contact'].queryset = Contacts.objects.none()
        if 'instrument' in self.data and 'proposal' in self.data:
            try:
                instrument_id = int(self.data.get('instrument'))
                proposal_id = int(self.data.get('proposal'))
                involved = Proposals.objects.get(pk=proposal_id).people
                self.fields['local_contact'].queryset = Contacts.objects.filter(uid__groups__name = 'localcontacts', pk__in = [x.pk for x in involved], 
                                             trained_instrumentgroups__instruments__pk = instrument_id) 
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty
        elif self.instance.pk:
            involved = self.instance.proposal.people
            self.fields['local_contact'].queryset = Contacts.objects.filter(uid__groups__name = 'localcontacts', pk__in = [x.pk for x in involved], 
                                             trained_instrumentgroups__instruments = self.instance.instrument)       
        
        self.fields['option'].queryset = Options.objects.none()
        if 'instrument' in self.data:
            try:
                instrument_id = int(self.data.get('instrument'))
                self.fields['option'].queryset = Options.objects.filter(instrument=instrument_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty
        elif self.instance.pk:
            self.fields['option'].queryset = self.instance.instrument.options_set.order_by('name')

        # help texts:
        self.fields['proposal'].help_text = "You can only book measurement time for accepted proposals, where you are part of the experimental team."
        self.fields['instrument'].help_text = "You can only book slot on instruments, where you are trained (see <a href='/profile'>your profile</a> for details)."
        self.fields['option'].help_text = "Select one or more options which you want to use during measurement."
        self.fields['shared_options'].help_text = "Select shared options which you want to use. They will be booked for same time as you select below. You can optionally change it later."
        self.fields['local_contact'].help_text = "Select local contact who will be your contact person during measurement. Local contact must be claimed in your proposal and must be responsible for selected instrument."
        
        self.helper.layout = Layout(
            Fieldset(
                None, 'proposal',  'instrument', 
            ),
            Div(
                Field('option', wrapper_class='col-md-6'),
                Field('shared_options', wrapper_class='col-md-6'),  
            css_class='form-row'),
            Fieldset(
                None, 'local_contact',
            ),
            DateRangeField('Date', 'start', 'end'),
            ButtonHolder(
                Submit('submit', 'Save', css_class='button white'),
                HTML("""<a role="button" class="btn btn-default"
                        href="{% url "app_experiments_calendar" %}">Cancel</a>"""),
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start")
        end = cleaned_data.get("end")
        instrument = cleaned_data.get("instrument")

        colision = Experiments.objects.filter(end__gt = start, start__lt = end, instrument = instrument).count()
        if colision > 0:
            raise forms.ValidationError(
                "Your data colide with another experiment on the same instrument. "
                "Maybe someone was faster then you in booking the slot. "
                "Select different dates."
            )
