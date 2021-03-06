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
from app.models import Experiments, Options, SharedOptions, Contacts, Proposals, SharedOptionSlot
from app.forms import ExperimentsForm
from django.core.exceptions import PermissionDenied
from datetime import datetime, timedelta
from backports.datetime_fromisoformat import MonkeyPatch
MonkeyPatch.patch_fromisoformat()


def load_options(request):
    instrument = request.GET.get('instrument')
    if instrument:
        options = Options.objects.filter(instrument=instrument).order_by('name')
    else:
        options = Options.objects.none()
    return render(request, 'dropdown_list_options.html', {'obj': options})

def load_shared_options(request):
    instrument = request.GET.get('instrument')
    if instrument:
        options = SharedOptions.objects.filter(instruments=instrument).order_by('name')
    else:
        options = SharedOptions.objects.none()
    return render(request, 'dropdown_list_options.html', {'obj': options})

def load_lc(request):
    instrument = request.GET.get('instrument')
    proposal = request.GET.get('proposal')
    if instrument and proposal:
        involved = Proposals.objects.get(pk=proposal).people
        lc = Contacts.objects.filter(pk__in = [x.pk for x in involved], responsible_for_instrumentgroups__instruments__pk = instrument) 
    else:
        lc = Contacts.objects.none()
    return render(request, 'dropdown_list_options.html', {'obj': lc})

def get_events(request):
    resource = request.GET.get('resource')
    start = datetime.fromisoformat(request.GET.get('start')).replace(tzinfo=None)
    end = datetime.fromisoformat(request.GET.get('end')).replace(tzinfo=None)
    if resource[0] == 'I' and resource[1:]:
        events = Experiments.objects.filter(instrument=resource[1:],start__lt=end, end__gt=start)
    elif resource[0] == 'R' and resource[1:]:
        events = SharedOptionSlot.objects.filter(shared_option=resource[1:],start__lt=end, end__gt=start)
    else:
        events = Experiments.objects.none()
    return render(request, 'ajax/events.html', {'events': events}, content_type='application/json')

def get_fulldays(request):
    resource = request.GET.get('resource')
    except_res = request.GET.get('except')
    start = datetime.today()
    if resource[0] == 'I' and resource[1:]:
        events = Experiments.objects.filter(instrument=resource[1:], end__gt=start).exclude(pk = except_res)
    elif resource[0] == 'R' and resource[1:]:  # TODO
        events = SharedOptionSlot.objects.filter(shared_option=resource[1:], end__gt=start).exclude(pk = except_res)
    else:
        events = Experiments.objects.none()
    fdays = set([])
    for event in events:
        for i in range(event.duration.days):
            fdays.add(event.start + timedelta(days=i))
    return render(request, 'ajax/fulldays.html', {'fulldays': fdays}, content_type='application/json')