"""
Definition of views.
"""

from django.contrib import messages
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User, Group
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from datetime import datetime
from django.views.generic import DetailView, ListView, UpdateView, CreateView, DeleteView
from app.models import Proposals, Instruments, Contacts, Affiliations, Countries, Options, SharedOptions, Samples, SamplePhotos, SampleRemarks, Publications, Experiments, Status
from app.forms import ProposalsForm, InstrumentsForm, ContactsForm, StatusForm, SamplesForm 
from app.forms import SamplePhotosForm, SampleRemarksForm, PublicationsForm, ExperimentsForm, SignupForm, ProfileForm, UserForm
from django.contrib.auth.decorators import login_required, permission_required
from django.core.mail import EmailMessage
from django.db.models import Q
from app.token import account_activation_token
from app.tables import ProposalTable, ProposalFilter, ContactsTable

from django_tables2.views import SingleTableView, SingleTableMixin
from django_filters.views import FilterView

from django.core.exceptions import PermissionDenied

from dal import autocomplete


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

    def get_result_label(self, item):
        return "%s (%s)" % (item.name, item.description)

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Contacts.objects.none()

        qs = Contacts.objects.filter(uid__in = User.objects.filter(groups__name__in=['localcontacts']))

        if not self.request.user.groups.filter(name='admins').exists():
            qs = qs.exclude(description__isnull=True).exclude(description__exact='')
        
        if self.q:
            qs = qs.filter(Q(name__icontains=self.q) | Q(description__icontains=self.q))

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
            'proposals_todo': Proposals.objects.filter(proposer=request.user, last_status='P').count(),
            'proposals_accepted': Proposals.objects.filter(Q(last_status='A') & ( 
                                       Q(proposer=request.user) | 
                                       Q(coproposers__uid__exact=request.user) | 
                                       Q(local_contacts__uid__exact=request.user))).distinct().count(),
            'proposals_director': Proposals.objects.filter(last_status='D').count(),
            'proposals_userofficeS': Proposals.objects.filter(last_status__in='S').count(),
            'proposals_userofficeU': Proposals.objects.filter(last_status__in='U').count(),
            'proposals_localcontact': Proposals.objects.filter(local_contacts__uid__exact=request.user, last_status='T').count(),
            'proposals_panel': Proposals.objects.filter(last_status='W').count(),
            'proposals_my_panel': Proposals.objects.filter(reporter__uid=request.user, last_status='R').count(),
        }
    )

@login_required
def proposal_howto(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'static/proposal-howto.html',
    )

def sendActivationMail(user, current_site):

    mail_subject = 'Activate your MGML account'
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    try:
        uid = uid.decode('utf-8')
    except:
        pass
    message = render_to_string('mails/activation.html', {
        'user': user,
        'domain': current_site.domain,
        'uid':uid,
        'token':account_activation_token.make_token(user),
    })
    to_email = user.email
    email = EmailMessage(
                mail_subject, message, to=[to_email]
    )
    email.send()
    
                


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            try:
                sendActivationMail(user, get_current_site(request))
            except:
                return render(
                    request,
                    'registration/message.html',
                    {
                        'text':'System was not able to send you email with activation link. ' + 
                                'Please try again or contact support.',
                    }
                )

            return render(
                request,
                'registration/message.html',
                {
                    'text':'Registration was successful and activation e-mail was send to you. ' + 
                           'Please check your mailbox (and possibly spam folder) and activate your account.',
                }
            )
    else:
        form = SignupForm()
    return render(request, 'registration/signup.html', {'form': form})

@permission_required('auth.can_add_user')
def resend(request, userpk):
    user = User.objects.get(pk=userpk)
    user.is_active = False
    user.save()
    try:
        sendActivationMail(user, get_current_site(request))
    except:
        return render(
            request,
            'registration/message.html',
            {
                'text':'System was not able to send you email with activation link. ' + 
                        'Please try again or contact support.',
            }
        )             
            
    return render(
        request,
        'registration/message.html',
        {
            'text':'An activation e-mail was send. ' + 
                    'Please check your mailbox (and possibly spam folder) and activate your account.',
        }
    )

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

class ProfileView(LoginRequiredMixin, DetailView):
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



class ProfileEditView(LoginRequiredMixin, UpdateView):
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
        usergroup = Group.objects.get(name='users') 
        usergroup.user_set.add(self.request.user)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('profile')


class ProfileCreateView(LoginRequiredMixin, CreateView):
    model = Contacts
    form_class = ProfileForm

    def form_valid(self, form):
        form.instance.uid = self.request.user
        form.instance.email = self.request.user.email
        #add user to users group
        usergroup = Group.objects.get(name='users') 
        usergroup.user_set.add(self.request.user)

        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = True
        return context

class UserUpdateView(LoginRequiredMixin, UpdateView):
    form_class = UserForm
    model = User
    template_name = 'app/user_profile_update.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('profile')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {
        'form': form
    })

class ProposalsListView(SingleTableMixin, FilterView):
    model = Proposals
    table_class = ProposalTable
    paginate_by = 25
    template_name = "proposal/list.html"

    filterset_class = ProposalFilter

    def get_queryset(self):
        queryset = Proposals.objects.distinct()

        if self.kwargs['filtering'] == "mine":
            queryset = queryset.filter( 
                                       Q(proposer=self.request.user) | 
                                       Q(coproposers__uid__exact=self.request.user) | 
                                       Q(local_contacts__uid__exact=self.request.user)).distinct()


        else:
            #check permissions
            if not self.request.user.has_perm('app.view_proposals'):
                queryset = queryset.filter(Q(proposer=self.request.user) | 
                                       Q(coproposers__uid__exact=self.request.user) | 
                                       Q(local_contacts__uid__exact=self.request.user))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filtering'] = self.kwargs['filtering']
        return context

class StatusCreateView(CreateView):
    model = Status
    form_class = StatusForm
    template_name = "proposal/status.html"
    current_proposal = None

    def get_initial(self):
        initial = super(StatusCreateView, self).get_initial()
        if "proposal_slug" in self.kwargs:
            self.current_proposal = Proposals.objects.get(slug=self.kwargs["proposal_slug"])
            initial.update({"proposal": self.current_proposal})
        else:
            raise Http404
        if "new_status" in self.kwargs:
            initial.update({"status": self.kwargs["new_status"]})
        return initial

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['proposal'] = self.current_proposal
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({ 'user': self.request.user})
        return kwargs

    def get_success_url(self):
        return reverse('app_proposals_detail', args={ self.kwargs["proposal_slug"]})

class ProposalsCreateView(PermissionRequiredMixin, CreateView):
    model = Proposals
    form_class = ProposalsForm
    template_name = "proposal/form.html"
    permission_required = 'app.add_proposals'
    permission_denied_message = 'You are not allowed to create proposals. You need to to fill your <a href="/profile">profile</a> first.' 

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({ 'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        form.instance.proposer = self.request.user
        return super().form_valid(form)


class ProposalsDetailView(DetailView):
    model = Proposals
    template_name = "proposal/detail.html"

    def get_queryset(self):
        # check permission
        if self.request.user.has_perm('app.view_proposals'):
            qs = super(ProposalsDetailView, self).get_queryset().distinct()
        else: # can view only if it is part of the team
            qs = super(ProposalsDetailView, self).get_queryset().filter(Q(proposer=self.request.user) | 
                                       Q(coproposers__uid__exact=self.request.user) | 
                                       Q(local_contacts__uid__exact=self.request.user)).distinct()
        return qs

    def get_context_data(self, *args, **kwargs):
        context = super(ProposalsDetailView, self).get_context_data(*args, **kwargs)
        context['status_history'] = Status.objects.filter(proposal=self.object)
        return context


class ProposalsUpdateView(UpdateView):
    model = Proposals
    form_class = ProposalsForm
    template_name = "proposal/form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({ 'user': self.request.user})
        kwargs.update({ 'status': super().get_object().last_status})
        kwargs.update({ 'local_contacts': super().get_object().local_contacts})
        return kwargs

class ProposalsDelete(DeleteView):
    model = Proposals
    success_url = reverse_lazy('app_proposals_list')
    template_name = "proposal/delete.html"

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(ProposalsDelete, self).get_object()
        if not obj.proposer == self.request.user and obj.last_status == "P":
            raise Http404
        return obj

class InstrumentsListView(ListView):
    model = Instruments


class ContactsListView(SingleTableMixin, PermissionRequiredMixin, ListView):
    permission_required = 'app.view_contacts'
    model = Contacts
    table_class = ContactsTable
    paginate_by = 25


class ContactsCreateView(PermissionRequiredMixin, CreateView):
    model = Contacts
    form_class = ContactsForm
    permission_required = 'app.add_contacts'
    permission_denied_message = 'You are not allowed to invite users. You need to to fill your <a href="/profile">profile</a> first.' 


    def form_valid(self, form):
        self.object = form.save()
        
        current_site = get_current_site(self.request)
        mail_subject = 'Invitation to use MGML user portal'
        message = render_to_string('mails/invitation.html', {
            'newuser': self.object,
            'user': self.request.user,
        })
        to_email = form.cleaned_data.get('email')
        email = EmailMessage(
                    mail_subject, message, to=[to_email]
        )
        try:
            email.send()
        except :
            return render(
                self.request,
                'registration/message.html',
                {
                    'text':'New contact has been created, but we failed to send him email about it. ' + 
                            'Please, contact MGML support.',
                }
            )
        return HttpResponseRedirect(self.get_success_url())
        


class ContactsDetailView(DetailView):
    model = Contacts


class ContactsUpdateView(UpdateView):
    model = Contacts
    form_class = ContactsForm


class AffiliationsListView(ListView):
    model = Affiliations



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

