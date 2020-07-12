"""
Definition of views accesible by admins and user office
"""

from django.contrib.auth.models import User, Group
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic import DetailView, ListView, UpdateView, CreateView, DeleteView
from app.models import Publication
from app.forms import PublicationForm
from django_tables2.views import SingleTableView, SingleTableMixin
from django_filters.views import FilterView
import django_tables2 as tables
import django_filters


class PublicationTable(tables.Table):
   
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Publication
        template_name = 'django_tables2/bootstrap4.html'
        exclude = {'id', 'full_citation'}
        sequence = ('link', 'name', 'journal')
        attrs  = { 'class': 'table table-striped table-sm table-hover'}

class PublicationFilter(django_filters.FilterSet):
    class Meta:
        model = Publication
        fields = ['issued']

class PublicationListView(PermissionRequiredMixin, SingleTableMixin, FilterView):
    template_name = "useroffice/publication_list.html"
    table_class = PublicationTable
    filterset_class = PublicationFilter

    permission_required = 'app.view_proposal'
    permission_denied_message = 'You are not allowed to view proposals.' 

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

