# app/tables.py
import django_tables2 as tables
from .models import Proposals, Contacts, User, Status, Instruments, Experiments, Log, Resource
from django_tables2.utils import A   # alias for Accessor
import django_filters
from django.db.models import Q, Count, Max
from django.utils.timezone import now
from datetime import timedelta, date


class TruncatedTextColumn(tables.Column):
    """A Column to limit to 100 characters and add an ellipsis"""

    def render(self, value):
        if len(value) > 52:
            return value[0:49] + '...'
        return str(value)

class ProposalTable(tables.Table):
    local_contacts_short = TruncatedTextColumn(verbose_name= 'Local contact', orderable = False)
    get_categories = tables.Column(verbose_name= 'Categories') #, order_by = A('categories__count')
    name = TruncatedTextColumn(linkify=True)
    proposaltype = tables.Column(verbose_name='Type')
    supervisor = tables.Column(empty_values=[])
    proposer  = tables.LinkColumn('app_contacts_detail', args=[A('proposer.contact.pk')], text=lambda record: record.proposer.contact.name, order_by = A('proposer.contact.name'))
    pid = tables.Column(attrs={'td': {'class': 'font-weight-bold'}})
    pdf = tables.LinkColumn('proposal_pdf_detail_view', args=[A('pid')], text="PDF",  attrs={'a': {'target': '_blank'}}, orderable = False)

    def __init__(self, *args, **kwargs):
        #if self.request.user.has_perm('app.approve_panel'):
        #    self.Meta.exclude.pop("reporter")
        super().__init__(*args, **kwargs)

    def order_get_categories(self, queryset, is_descending):
        queryset = queryset.annotate(
            countcat=Count('categories'),
            firstcat=Max('categories'),
        ).order_by(("-" if is_descending else "") + "countcat", ("-" if is_descending else "") + "firstcat")
        return (queryset, True)

    def before_render(self, request):
        if request.user.has_perm('app.approve_panel') or request.user.has_perm('app.approve_board'):
            self.columns.show('reporter')
        else:
            self.columns.hide('reporter')
        if request.user.has_perm('app.view_proposals'):  # typically user office
            self.columns.show('grants')
        else:
            self.columns.hide('grants')

    def render_supervisor(self, record):
        if record.student:
            return "✓ (%s)" % record.supervisor
        return "✗"

    class Meta:
        model = Proposals
        template_name = 'django_tables2/bootstrap4.html'
        exclude = ('id', 'abstract', 'slug', 'student', 'scientific_bg', 'thesis_topic') #, 'reporter') 
        sequence = ('pid', 'name', 'pdf', '...')
        attrs  = { 'class': 'table table-striped table-sm table-hover'}

def localcontacts(request):
    if request is None or not request.user.is_authenticated:
        return Contacts.objects.none()

    qs = Contacts.objects.filter(uid__in = User.objects.filter(groups__name__in=['localcontacts']))
    return qs

def reporters(request):
    qs = Contacts.objects.none()
    if request is None or not request.user.is_authenticated:
        return qs
    if request.user.has_perm('app.approve_panel') or request.user.has_perm('app.approve_board'):
        qs = Contacts.objects.filter(uid__in = User.objects.filter(groups__name__in=['panel', 'board']))
    elif request.user.has_perm('app.approve_panel'): 
        qs = Contacts.objects.filter(uid__in = User.objects.filter(groups__name__in=['panel']))
    elif request.user.has_perm('app.approve_board'):
        qs = Contacts.objects.filter(uid__in = User.objects.filter(groups__name__in=['board']))
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
        elif not (self.request.user.has_perm('app.approve_panel') or self.request.user.has_perm('app.approve_board')):
            self.filters.pop("reporter")

    def filter_search_all(self, queryset, name, value):
        return queryset.filter(
            Q(pid__icontains=value) | Q(name__icontains=value) | Q(proposer__contact__name__icontains=value) | Q(supervisor__name__icontains=value)
        )

    class Meta:
        model = Proposals
        fields = ['proposaltype', 'last_status'] #, 'owner']



class ExperimentTable(tables.Table):
    real_start = tables.DateTimeColumn(verbose_name= 'Start',order_by=("start"))
    real_end = tables.DateTimeColumn(verbose_name= 'End',order_by=("end"))
    all_options = tables.Column(verbose_name= 'Options', orderable=False)
    proposal  = tables.LinkColumn('app_experiments_detail', args=[A('pk')], verbose_name='Slot')

    def __init__(self, *args, **kwargs):
        #if self.request.user.has_perm('app.approve_panel'):
        #    self.Meta.exclude.pop("reporter")
        super().__init__(*args, **kwargs)


    class Meta:
        model = Experiments
        template_name = 'django_tables2/bootstrap4.html'
        fields = ('proposal', 'duration', 'instrument', 'responsible', 'local_contact', 'all_options')
        sequence = ('proposal', 'instrument', 'all_options', 'real_start', 'real_end', 'duration',  'responsible', 'local_contact')
        attrs  = { 'class': 'table table-striped table-sm table-hover'}
        row_attrs = {
            'running': lambda record: record.running
        }
 
class ExperimentFilter(django_filters.FilterSet):

    end = django_filters.DateRangeFilter(label='Ends in: ', empty_label = "All",  choices = [
        ('future', 'Future'),
        ('past', 'Past'),
    ], filters = {
        'future': lambda qs, name: qs.filter(Q(end__gte = now(), instrument__book_by_hour = True) | Q(Q(end = date.today() + timedelta(days=-1), instrument__start_hour__gt = now().hour) | Q(end__gte = date.today()), instrument__book_by_hour = False)),
        'past': lambda qs, name: qs.filter(Q(end__lte = now(), instrument__book_by_hour = True) | Q(Q(end = date.today() + timedelta(days=-1), instrument__start_hour__lte = now().hour) | Q(end__lt = date.today() + timedelta(days=-1)), instrument__book_by_hour = False)),
    })
    instrument = django_filters.ModelChoiceFilter(label = 'Instrument: ', empty_label = "All", queryset=Instruments.objects.all())
    local_contact = django_filters.ModelChoiceFilter(label = 'Local Contact: ', empty_label = "All", queryset=localcontacts)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'filtering' in self.request.resolver_match.kwargs and self.request.resolver_match.kwargs['filtering']  == "mine":
            self.filters.pop("local_contact")

    class Meta:
        model = Experiments
        fields = ['instrument', 'end', 'local_contact'] #, 'owner']



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


class LogTable(tables.Table):
    usage_set = tables.ManyToManyColumn(transform=lambda r: f'{r.resource.name}={r.amount}{r.resource.unit}', verbose_name='Used Resources')

    class Meta:
        model = Log
        template_name = 'django_tables2/bootstrap4.html'
        exclude = ('created', 'last_updated', 'id', 'proposal') 
        sequence = ('instrument', '...')
        attrs  = { 'class': 'table table-striped table-sm table-hover'}

class LogSumTable(tables.Table):
    instrument__name = tables.Column('Instrument')
    sumduration = tables.Column(verbose_name='Summed duration')
    

    class Meta:
        template_name = 'django_tables2/bootstrap4.html'
        attrs  = { 'class': 'table table-striped table-sm table-hover'}

class UsedResourcesTable(tables.Table):
    name = tables.Column()
    sumamount = tables.Column(verbose_name='Summed amount')

    def render_sumamount(self, value, record):
        return f"{value} {record['unit']}"
    
    class Meta:
        template_name = 'django_tables2/bootstrap4.html'
        attrs  = { 'class': 'table table-striped table-sm table-hover'}
