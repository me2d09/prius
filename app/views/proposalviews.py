"""
Definition of proposal relatated views.

Means also reports and logs
"""


from app.tables import ProposalTable, ProposalFilter, LogTable, LogSumTable, UsedResourcesTable
from app.models import Proposals, Status, Report, Log, Resource
from app.forms import ProposalsForm, StatusForm, ReportForm

from django.contrib.auth.models import User, Group
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.views.generic import DetailView, ListView, UpdateView, CreateView, DeleteView, TemplateView
from django.urls import reverse, reverse_lazy
from django.db.models import Q, Sum, Count

from django_tables2.views import SingleTableView, SingleTableMixin, MultiTableMixin
from django_filters.views import FilterView


class ProposalsListView(LoginRequiredMixin, SingleTableMixin, FilterView):
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
                if self.request.user.has_perm('app.view_panel_proposals'):
                    queryset = queryset.exclude(last_status__in='PSU').exclude(proposaltype='T').exclude(review_process='B')
                elif self.request.user.has_perm('app.view_board_proposals'):
                    queryset = queryset.exclude(last_status__in='PSU').exclude(proposaltype='T').exclude(review_process='P')
                else:
                    queryset = queryset.filter(Q(proposer=self.request.user) | 
                                       Q(coproposers__uid__exact=self.request.user) | 
                                       Q(local_contacts__uid__exact=self.request.user))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filtering'] = self.kwargs['filtering']
        return context

class StatusCreateView(LoginRequiredMixin, CreateView):
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
        if self.request.user.has_perm('app.view_panel_proposals') or self.request.user.has_perm('app.view_board_proposals'):
            return reverse('app_proposals_list_all') # in case of board/panel
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


class ProposalsDetailView(LoginRequiredMixin, DetailView):
    model = Proposals
    template_name = "proposal/detail.html"

    def get_queryset(self):
        # check permission
        if self.request.user.has_perm('app.view_proposals'):
            qs = super(ProposalsDetailView, self).get_queryset().distinct()
        elif self.request.user.has_perm('app.view_panel_proposals') or self.request.user.has_perm('app.view_board_proposals'):
            qs = super(ProposalsDetailView, self).get_queryset().exclude(last_status__in='P').exclude(proposaltype='T').distinct()
        else: # can view only if it is part of the team
            qs = super(ProposalsDetailView, self).get_queryset().filter(Q(proposer=self.request.user) | 
                                       Q(coproposers__uid__exact=self.request.user) | 
                                       Q(local_contacts__uid__exact=self.request.user)).distinct()
        return qs

    def get_context_data(self, *args, **kwargs):
        context = super(ProposalsDetailView, self).get_context_data(*args, **kwargs)
        context['status_history'] = Status.objects.filter(proposal=self.object)
        return context


class ProposalsUpdateView(LoginRequiredMixin, UpdateView):
    model = Proposals
    form_class = ProposalsForm
    template_name = "proposal/form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({ 'user': self.request.user})
        kwargs.update({ 'status': super().get_object().last_status})
        kwargs.update({ 'local_contacts': super().get_object().local_contacts})
        kwargs.update({ 'proposer': super().get_object().proposer})
        return kwargs

class ProposalsDelete(LoginRequiredMixin, DeleteView):
    model = Proposals
    success_url = reverse_lazy('app_proposals_list')
    template_name = "proposal/delete.html"

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(ProposalsDelete, self).get_object()
        if not obj.proposer == self.request.user and obj.last_status == "P":
            raise Http404
        return obj




class ReportCreateView(PermissionRequiredMixin, CreateView):
    model = Report
    form_class = ReportForm
    template_name = "proposal/report_form.html"
    permission_required = 'app.change_status'
    permission_denied_message = 'You are not allowed to create report requests.'
    
    def get_initial(self):
        initial = super().get_initial()
        self.current_proposal = Proposals.objects.get(slug=self.kwargs["proposal_slug"])
        if "proposal_slug" in self.kwargs:
            initial.update({"proposal": self.current_proposal})
        else:
            raise Http404
        return initial

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


class ReportDetailView(DetailView):
    model = Report
    template_name = "proposal/report_detail.html" 


class ReportUpdateView(UpdateView):
    model = Report
    form_class = ReportForm
    template_name = "proposal/report_form.html"

    def get_success_url(self):
        return reverse('app_proposals_detail', args={ self.object.proposal.slug})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({ 'user': self.request.user})
        return kwargs


class LogsListView(LoginRequiredMixin, MultiTableMixin, TemplateView):
    table_pagination = {
        "per_page": 25
    }
    template_name = "proposal/log_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = Proposals.objects.get(slug=self.kwargs["proposal_slug"])
        return context

    def get_tables(self):
        qs_logs = Log.objects.filter(proposal__slug = self.kwargs["proposal_slug"])
        qs_sum = qs_logs.values('instrument__name').annotate(sumduration=Sum('duration')).order_by()

        qs_resources = Resource.objects.filter(log__proposal__slug = self.kwargs["proposal_slug"]).values('name', 'unit').annotate(sumamount=Sum('usage__amount'))
        return [
            LogSumTable(qs_sum),
            UsedResourcesTable(qs_resources),
            LogTable(qs_logs),            
        ]

