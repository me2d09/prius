# app/tables.py
import django_tables2 as tables
from .models import Proposals, Contacts, User, Status
from django_tables2.utils import A  # alias for Accessor
import django_filters
from django.db.models import Q

class ProposalTable(tables.Table):

    name = tables.Column(linkify=True)
    proposer  = tables.LinkColumn('app_contacts_detail', args=[A('proposer.contact.pk')], text=lambda record: record.proposer.contact.name, order_by = A('proposer.contact.name'))
    pid = tables.Column(attrs={'td': {'class': 'font-weight-bold'}})
    pdf = tables.LinkColumn('proposal_pdf_detail_view', args=[A('pid')], text="PDF",  attrs={'a': {'target': '_blank'}}, orderable = False)

    def render_supervisor(self, record):
        if record.student:
            return "✔ (%s)" % record.supervisor
        return "✘"

    class Meta:
        model = Proposals
        template_name = 'django_tables2/bootstrap4.html'
        exclude = ('id', 'abstract', 'slug', 'student', 'scientific_bg') 
        sequence = ('pid', 'name', 'pdf', '...')
        attrs  = { 'class': 'table table-striped table-sm table-hover'}
        

def localcontacts(request):
    if request is None or not request.user.is_authenticated:
        return Contacts.objects.none()

    qs = Contacts.objects.filter(uid__in = User.objects.filter(groups__name__in=['localcontacts']))
    return qs

class ProposalFilter(django_filters.FilterSet):

    #owner = django_filters.filters.ChoiceFilter(choices=('mine', 'all'))
    proposaltype = django_filters.ChoiceFilter(choices=Proposals.PROPOSAL_TYPE, empty_label='all proposals')
    last_status = django_filters.ChoiceFilter(choices=Status.STATUS_TYPES, empty_label='all statuses')
    local_contact = django_filters.ModelChoiceFilter(queryset=localcontacts, empty_label='all local contacts')
    search_all = django_filters.CharFilter(method='filter_search_all', label='search proposals')


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'filtering' in self.request.resolver_match.kwargs and self.request.resolver_match.kwargs['filtering']  == "mine":
            self.filters.pop("local_contact")
            self.filters.pop("search_all")

    def filter_search_all(self, queryset, name, value):
        return queryset.filter(
            Q(pid__icontains=value) | Q(name__icontains=value) | Q(proposer__contact__name__icontains=value) | Q(supervisor__name__icontains=value)
        )

    class Meta:
        model = Proposals
        fields = ['proposaltype', 'last_status'] #, 'owner']