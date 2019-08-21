"""
Definition of views.
"""

from django.contrib.auth.models import User, Group
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.template import RequestContext
from django.template.loader import render_to_string
from datetime import datetime
from django.views.generic import DetailView, ListView, UpdateView, CreateView, DeleteView
from app.models import Experiments, Instruments, Proposals
from app.forms import ExperimentsForm
from app.tables import ExperimentTable
from django.core.exceptions import PermissionDenied
from django_tables2.views import SingleTableView, SingleTableMixin
from django_filters.views import FilterView

class ExperimentsListView(SingleTableMixin, FilterView):
    template_name = "booking/experiments_list.html"
    model = Experiments
    table_class = ExperimentTable
    paginate_by = 25


class ExperimentsCalendarView(ListView):
    template_name = "booking/experiments_calendar.html"
    model = Experiments

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['instruments'] = Instruments.objects.all()
        return context


class ExperimentsCreateView(CreateView):
    template_name = "booking/experiments_form.html"
    model = Experiments
    form_class = ExperimentsForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({ 'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        form.instance.creator = self.request.user.contact
        if not form.instance.responsible:
            form.instance.responsible = self.request.user.contact
        return super().form_valid(form)


class ExperimentsDetailView(DetailView):
    template_name = "booking/experiments_detail.html"
    model = Experiments


class ExperimentsUpdateView(UpdateView):
    template_name = "booking/experiments_form.html"
    model = Experiments
    form_class = ExperimentsForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({ 'user': self.request.user})
        return kwargs

