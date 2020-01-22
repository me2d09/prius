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
from app.models import Experiments, Instruments, Proposals, SharedOptions, SharedOptionSlot
from app.forms import ExperimentsForm, SharedOptionSlotForm
from app.tables import ExperimentTable, ExperimentFilter
from django.core.exceptions import PermissionDenied
from django_tables2.views import SingleTableView, SingleTableMixin
from django_filters.views import FilterView
from django.db.models import Q

class ExperimentsListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    template_name = "booking/experiments_list.html"
    model = Experiments
    table_class = ExperimentTable
    filterset_class = ExperimentFilter
    paginate_by = 25
    

    def get_queryset(self):
        queryset = Experiments.objects.distinct()

        if self.kwargs['filtering'] == "mine":
            queryset = queryset.filter( 
                                       Q(responsible=self.request.user.contact) | 
                                       Q(proposal__coproposers=self.request.user.contact) | 
                                       Q(proposal__proposer=self.request.user) | 
                                       Q(proposal__local_contacts=self.request.user.contact) | 
                                       Q(proposal__supervisor=self.request.user.contact)).distinct()
        else:
            #check permissions
            if not self.request.user.has_perm('app.view_slots'):
                queryset = queryset.filter( 
                                       Q(responsible=self.request.user.contact) | 
                                       Q(proposal__coproposers=self.request.user.contact) | 
                                       Q(proposal__proposer=self.request.user) | 
                                       Q(proposal__local_contacts=self.request.user.contact) | 
                                       Q(proposal__supervisor=self.request.user.contact)).distinct()
        return queryset.order_by('start')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filtering'] = self.kwargs['filtering']
        return context


class ExperimentsCalendarView(LoginRequiredMixin, ListView):
    template_name = "booking/experiments_calendar.html"
    model = Experiments

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['instruments'] = Instruments.objects.all()
        context['sharedoptions'] = SharedOptions.objects.all()
        return context


class ExperimentsCreateView(LoginRequiredMixin, CreateView):
    template_name = "booking/experiments_form.html"
    model = Experiments
    form_class = ExperimentsForm


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({ 'user': self.request.user})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['timebooking'] = [x.id for x in Instruments.objects.filter(book_by_hour=True)]
        return context

    def form_valid(self, form):
        form.instance.creator = self.request.user.contact
        if not form.instance.responsible:
            form.instance.responsible = self.request.user.contact
        return super().form_valid(form)


class ExperimentsDetailView(LoginRequiredMixin, DetailView):
    template_name = "booking/experiments_detail.html"
    model = Experiments



class ExperimentsUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "booking/experiments_form.html"
    model = Experiments
    form_class = ExperimentsForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({ 'user': self.request.user})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['timebooking'] = [x.id for x in Instruments.objects.filter(book_by_hour=True)]
        return context

class ExperimentsDeleteView(LoginRequiredMixin, DeleteView):
    model = Experiments
    success_url = reverse_lazy('app_experiments_calendar')
    template_name = "booking/experiments_delete.html"

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super().get_object()
        if not obj.responsible == self.request.user.contact:
            raise Http404
        return obj

class SharedOptionSlotDetailView(LoginRequiredMixin, DetailView):
    template_name = "booking/sos_detail.html"
    model = SharedOptionSlot


class SharedOptionSlotUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "booking/sos_form.html"
    model = SharedOptionSlot
    form_class = SharedOptionSlotForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({ 'user': self.request.user})
        return kwargs

class SharedOptionSlotDelete(LoginRequiredMixin, DeleteView):
    model = SharedOptionSlot
    success_url = reverse_lazy('app_experiments_calendar')
    template_name = "booking/experiments_delete.html"

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super().get_object()
        if not obj.proposer == self.request.user and obj.last_status == "P":
            raise Http404
        return obj