"""
Definition of views.
"""

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User, Group
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, Http404
from django.urls import reverse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from datetime import datetime
from django.views.generic import DetailView, ListView, UpdateView, CreateView
from .models import Proposals, Instruments, Contacts, Affiliations, Countries, InstrumentRequest, Options, SharedOptions, InstrumentParameterSets, InstrumentParameters, ParameterValues, Samples, SamplePhotos, SampleRemarks, Publications, Experiments, Slots
from .forms import ProposalsForm, InstrumentsForm, ContactsForm, AffiliationsForm, CountriesForm, InstrumentRequestForm
from .forms import OptionsForm, SharedOptionsForm, InstrumentParameterSetsForm, InstrumentParametersForm, ParameterValuesForm, SamplesForm 
from .forms import SamplePhotosForm, SampleRemarksForm, PublicationsForm, ExperimentsForm, SlotsForm, SignupForm, ProfileForm, UserForm
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.db.models import Q
from .token import account_activation_token

from dal import autocomplete
from app.models import Contacts


class ContactAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Contacts.objects.none()

        qs = Contacts.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs

class LocalContactAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Contacts.objects.none()

        qs = Contacts.objects.filter(uid__in = User.objects.filter(groups__name__in=['localcontacts']))
        
        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs

class AffilAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Affiliations.objects.none()

        qs = Affiliations.objects.all()

        if self.q:
            qs = qs.filter(Q(institution__icontains=self.q) | Q(department__icontains=self.q) | Q(city__icontains=self.q))

        return qs


@login_required
def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
        }
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Contact',
            'message':'Your contact page.',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        }
    )

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            #form.save()
            #username = form.cleaned_data.get('username')
            #raw_password = form.cleaned_data.get('password1')
            #user = authenticate(username=username, password=raw_password)
            #login(request, user)
            #return redirect('home')
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your MGML account.'
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)).decode('utf-8'),
                'token':account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.send()
            return HttpResponse('Please confirm your email address to complete the registration')
    else:
        form = SignupForm()
    return render(request, 'registration/signup.html', {'form': form})

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('home')
        return render(
            request,
            'registration/message.html',
            {
                'text':'Thank you for your email confirmation. Now you can login your account.',
            }
        )
    else:
        return render(
            request,
            'registration/message.html',
            {
                'text':'Activation link is invalid!',
            }
        )

class ProfileView(DetailView):
    model = Contacts
    template_name = "app/user_profile.html"
    context_object_name = "contact"

    user = None

    def get_object(self):
        username = self.kwargs.get('username')
        if not username:
            self.user = self.request.user
        else:
            try:
                self.user = User.objects.get(username=username)
            except:
                raise Http404()
        obj = self.model.objects.filter(uid=self.user)
        if len(obj) > 0:
            return obj[0]
        if not username:
            return "redir"
        else:
            return None

    def get(self, *args, **kwargs):
        # Make sure to use the canonical URL
        self.object = self.get_object()
        if self.object == "redir":
            return redirect("/create-profile")
        elif self.object is None:
            raise Http404()
        return super(ProfileView, self).get(*args, **kwargs);

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        context['userprofile'] = self.user
        return context



class ProfileEditView(UpdateView):
    model = Contacts
    form_class = ProfileForm
    template_name = "app/user_profile_update.html"
    
    def get_object(self):
        # Use a custom queryset if provided; this is required for subclasses
        # like DateDetailView
        queryset = self.get_queryset()
        uid = self.request.user
        if uid is not None:
            queryset = queryset.filter(uid=uid)
        else:
            raise AttributeError(u"Profile edit view %s must be called by "
                                 u"logged in user."
                                 % self.__class__.__name__)
        try:
            obj = queryset.get()
        except ObjectDoesNotExist:
            raise Http404(_(u"No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj

    def form_valid(self, form):
        form.instance.uid = self.request.user
        #add user to users group
        usergroup = Group.objects.get(name='Users') 
        usergroup.user_set.add(self.request.user)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('profile')


class ProfileCreateView(CreateView):
    model = Contacts
    form_class = ProfileForm

    def form_valid(self, form):
        form.instance.uid = self.request.user
        #add user to users group
        usergroup = Group.objects.get(name='Users') 
        usergroup.user_set.add(self.request.user)

        return super().form_valid(form)

class UserUpdateView(UpdateView):
    form_class = UserForm
    model = User
    template_name = 'app/user_profile_update.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('profile')


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {
        'form': form
    })

class ProposalsListView(ListView):
    model = Proposals

    def get_queryset(self):
        queryset = Proposals.objects.all()

        if self.kwargs['filtering'] == "mine":
            queryset = queryset.filter(proposer=self.request.user)
        else:
            raise NotImplementedError
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filtering'] = self.kwargs['filtering']
        return context


class ProposalsCreateView(CreateView):
    model = Proposals
    form_class = ProposalsForm

    def form_valid(self, form):
        form.instance.proposer = self.request.user
        return super().form_valid(form)


class ProposalsDetailView(DetailView):
    model = Proposals


class ProposalsUpdateView(UpdateView):
    model = Proposals
    form_class = ProposalsForm


class InstrumentsListView(ListView):
    model = Instruments


class InstrumentsCreateView(CreateView):
    model = Instruments
    form_class = InstrumentsForm


class InstrumentsDetailView(DetailView):
    model = Instruments


class InstrumentsUpdateView(UpdateView):
    model = Instruments
    form_class = InstrumentsForm


class ContactsListView(ListView):
    model = Contacts


class ContactsCreateView(CreateView):
    model = Contacts
    form_class = ContactsForm


class ContactsDetailView(DetailView):
    model = Contacts


class ContactsUpdateView(UpdateView):
    model = Contacts
    form_class = ContactsForm


class AffiliationsListView(ListView):
    model = Affiliations


class AffiliationsCreateView(CreateView):
    model = Affiliations
    form_class = AffiliationsForm


class AffiliationsDetailView(DetailView):
    model = Affiliations


class AffiliationsUpdateView(UpdateView):
    model = Affiliations
    form_class = AffiliationsForm


class CountriesListView(ListView):
    model = Countries


class CountriesCreateView(CreateView):
    model = Countries
    form_class = CountriesForm


class CountriesDetailView(DetailView):
    model = Countries


class CountriesUpdateView(UpdateView):
    model = Countries
    form_class = CountriesForm


class InstrumentRequestListView(ListView):
    model = InstrumentRequest


class InstrumentRequestCreateView(CreateView):
    model = InstrumentRequest
    form_class = InstrumentRequestForm


class InstrumentRequestDetailView(DetailView):
    model = InstrumentRequest


class InstrumentRequestUpdateView(UpdateView):
    model = InstrumentRequest
    form_class = InstrumentRequestForm


class OptionsListView(ListView):
    model = Options


class OptionsCreateView(CreateView):
    model = Options
    form_class = OptionsForm


class OptionsDetailView(DetailView):
    model = Options


class OptionsUpdateView(UpdateView):
    model = Options
    form_class = OptionsForm


class SharedOptionsListView(ListView):
    model = SharedOptions


class SharedOptionsCreateView(CreateView):
    model = SharedOptions
    form_class = SharedOptionsForm


class SharedOptionsDetailView(DetailView):
    model = SharedOptions


class SharedOptionsUpdateView(UpdateView):
    model = SharedOptions
    form_class = SharedOptionsForm


class InstrumentParameterSetsListView(ListView):
    model = InstrumentParameterSets


class InstrumentParameterSetsCreateView(CreateView):
    model = InstrumentParameterSets
    form_class = InstrumentParameterSetsForm


class InstrumentParameterSetsDetailView(DetailView):
    model = InstrumentParameterSets


class InstrumentParameterSetsUpdateView(UpdateView):
    model = InstrumentParameterSets
    form_class = InstrumentParameterSetsForm


class InstrumentParametersListView(ListView):
    model = InstrumentParameters


class InstrumentParametersCreateView(CreateView):
    model = InstrumentParameters
    form_class = InstrumentParametersForm


class InstrumentParametersDetailView(DetailView):
    model = InstrumentParameters


class InstrumentParametersUpdateView(UpdateView):
    model = InstrumentParameters
    form_class = InstrumentParametersForm


class ParameterValuesListView(ListView):
    model = ParameterValues


class ParameterValuesCreateView(CreateView):
    model = ParameterValues
    form_class = ParameterValuesForm


class ParameterValuesDetailView(DetailView):
    model = ParameterValues


class ParameterValuesUpdateView(UpdateView):
    model = ParameterValues
    form_class = ParameterValuesForm


class SamplesListView(ListView):
    model = Samples


class SamplesCreateView(CreateView):
    model = Samples
    form_class = SamplesForm


class SamplesDetailView(DetailView):
    model = Samples


class SamplesUpdateView(UpdateView):
    model = Samples
    form_class = SamplesForm


class SamplePhotosListView(ListView):
    model = SamplePhotos


class SamplePhotosCreateView(CreateView):
    model = SamplePhotos
    form_class = SamplePhotosForm


class SamplePhotosDetailView(DetailView):
    model = SamplePhotos


class SamplePhotosUpdateView(UpdateView):
    model = SamplePhotos
    form_class = SamplePhotosForm


class SampleRemarksListView(ListView):
    model = SampleRemarks


class SampleRemarksCreateView(CreateView):
    model = SampleRemarks
    form_class = SampleRemarksForm


class SampleRemarksDetailView(DetailView):
    model = SampleRemarks


class SampleRemarksUpdateView(UpdateView):
    model = SampleRemarks
    form_class = SampleRemarksForm


class PublicationsListView(ListView):
    model = Publications


class PublicationsCreateView(CreateView):
    model = Publications
    form_class = PublicationsForm


class PublicationsDetailView(DetailView):
    model = Publications


class PublicationsUpdateView(UpdateView):
    model = Publications
    form_class = PublicationsForm


class ExperimentsListView(ListView):
    model = Experiments


class ExperimentsCreateView(CreateView):
    model = Experiments
    form_class = ExperimentsForm


class ExperimentsDetailView(DetailView):
    model = Experiments


class ExperimentsUpdateView(UpdateView):
    model = Experiments
    form_class = ExperimentsForm


class SlotsListView(ListView):
    model = Slots


class SlotsCreateView(CreateView):
    model = Slots
    form_class = SlotsForm


class SlotsDetailView(DetailView):
    model = Slots


class SlotsUpdateView(UpdateView):
    model = Slots
    form_class = SlotsForm

