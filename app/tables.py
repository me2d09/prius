# app/tables.py
import django_tables2 as tables
from .models import Proposals, Contacts, User, Status, Instruments, Experiments
from django_tables2.utils import A  # alias for Accessor
import django_filters
from django.db.models import Q


class TruncatedTextColumn(tables.Column):
    """A Column to limit to 100 characters and add an ellipsis"""

    def render(self, value):
        if len(value) > 52:
            return value[0:49] + '...'
        return str(value)

class ProposalTable(tables.Table):
    local_contacts_short = TruncatedTextColumn(verbose_name= 'Local contact', orderable = False)
    name = TruncatedTextColumn(linkify=True)
    proposer  = tables.LinkColumn('app_contacts_detail', args=[A('proposer.contact.pk')], text=lambda record: record.proposer.contact.name, order_by = A('proposer.contact.name'))
    pid = tables.Column(attrs={'td': {'class': 'font-weight-bold'}})
    pdf = tables.LinkColumn('proposal_pdf_detail_view', args=[A('pid')], text="PDF",  attrs={'a': {'target': '_blank'}}, orderable = False)

    def __init__(self, *args, **kwargs):
        #if self.request.user.has_perm('app.approve_panel'):
        #    self.Meta.exclude.pop("reporter")
        super().__init__(*args, **kwargs)

    def before_render(self, request):
        if request.user.has_perm('app.approve_panel'):
            self.columns.show('reporter')
        else:
            self.columns.hide('reporter')

    def render_supervisor(self, record):
        if record.student:
            return "? (%s)" % record.supervisor
        return "?"

    class Meta:
        model = Proposals
        template_name = 'django_tables2/bootstrap4.html'
        exclude = ('id', 'abstract', 'slug', 'student', 'scientific_bg', 'thesis_topic', 'grants') #, 'reporter') 
        sequence = ('pid', 'name', 'pdf', '...')
        attrs  = { 'class': 'table table-striped table-sm table-hover'}

class ExperimentTable(tables.Table):

    def __init__(self, *args, **kwargs):
        #if self.request.user.has_perm('app.approve_panel'):
        #    self.Meta.exclude.pop("reporter")
        super().__init__(*args, **kwargs)


    class Meta:
        model = Experiments
        template_name = 'django_tables2/bootstrap4.html'
        #exclude = ('id', 'abstract', 'slug', 'student', 'scientific_bg', 'thesis_topic', 'grants') #, 'reporter') 
        #sequence = ('pid', 'name', 'pdf', '...')
        attrs  = { 'class': 'table table-striped table-sm table-hover'}
        

def localcontacts(request):
    if request is None or not request.user.is_authenticated:
        return Contacts.objects.none()

    qs = Contacts.objects.filter(uid__in = User.objects.filter(groups__name__in=['localcontacts']))
    return qs

def reporters(request):
    if request is None or not request.user.is_authenticated:
        return Contacts.objects.none()

    qs = Contacts.objects.filter(uid__in = User.objects.filter(groups__name__in=['panel']))
    return qs

class ProposalFilter(django_filters.FilterSet):

    #owner = django_filters.filters.ChoiceFilter(choices=('mine', 'all'))
    proposaltype = django_filters.ChoiceFilter(choices=Proposals.PROPOSAL_TYPE, empty_label='all proposals')
    last_status = django_filters.ChoiceFilter(choices=Status.STATUS_TYPES, empty_label='all statuses')
    local_contacts = django_filters.ModelChoiceFilter(queryset=localcontacts) #, empty_label='all local contacts')
    reporter = django_filters.ModelChoiceFilter(queryset=reporters, empty_label='all reporters')
    search_all = django_filters.CharFilter(method='filter_search_all', label='search proposals')


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'filtering' in self.request.resolver_match.kwargs and self.request.resolver_match.kwargs['filtering']  == "mine":
            self.filters.pop("local_contacts")
            self.filters.pop("search_all")
            self.filters.pop("reporter")
        elif not self.request.user.has_perm('app.approve_panel'):
            self.filters.pop("reporter")

    def filter_search_all(self, queryset, name, value):
        return queryset.filter(
            Q(pid__icontains=value) | Q(name__icontains=value) | Q(proposer__contact__name__icontains=value) | Q(supervisor__name__icontains=value)
        )

    class Meta:
        model = Proposals
        fields = ['proposaltype', 'last_status'] #, 'owner']



class ContactsTable(tables.Table):
    
    name = tables.Column(linkify=True)
    uid = tables.Column(default='---', verbose_name="Username")
    
    class Meta:
        model = Contacts
        template_name = 'django_tables2/bootstrap4.html'
        exclude = ('created', 'last_updated', 'orcid', 'description', 'id') 
        #sequence = ('pid', 'name', 'pdf', '...')
        attrs  = { 'class': 'table table-striped table-sm table-hover'}
   
def instruments(request):
    if request is None or not request.user.is_authenticated:
        return Instruments.objects.none()

    qs = Instruments.objects.filter(active=True, public=True)
    return qs

class ExperimentFilter(django_filters.FilterSet):

    #owner = django_filters.filters.ChoiceFilter(choices=('mine', 'all'))
    instrument1 = django_filters.ModelChoiceFilter(queryset=instruments, empty_label='---')
    instrument2 = django_filters.ModelChoiceFilter(queryset=instruments, empty_label='---')
    instrument3 = django_filters.ModelChoiceFilter(queryset=instruments, empty_label='---')
    instrument4 = django_filters.ModelChoiceFilter(queryset=instruments, empty_label='---')
    

    class Meta:
        model = Experiments
        fields = ['instrument'] #, 'owner']
