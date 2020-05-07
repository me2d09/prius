"""
Definition of views accesible by admins and user office
"""

from django.contrib.auth.models import User, Group
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic import DetailView, ListView, UpdateView, CreateView, DeleteView
from app.models import Publication
from app.forms import PublicationForm

class PublicationListView(PermissionRequiredMixin, ListView):
    template_name = "useroffice/publication_list.html"
    permission_required = 'app.view_proposal'
    permission_denied_message = 'You are not allowed to invite users. You need to to fill your <a href="/profile">profile</a> first.' 

    model = Publication


class PublicationCreateView(PermissionRequiredMixin, CreateView):
    template_name = "useroffice/publication_form.html"
    model = Publication
    form_class = PublicationForm


class PublicationDetailView(PermissionRequiredMixin, DetailView):
    template_name = "useroffice/publication_details.html"
    model = Publication


class PublicationUpdateView(PermissionRequiredMixin, UpdateView):
    template_name = "useroffice/publication_form.html"
    model = Publication
    form_class = PublicationForm

