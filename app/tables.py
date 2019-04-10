# app/tables.py
import django_tables2 as tables
from .models import Proposals, Contacts, User
from django_tables2.utils import A  # alias for Accessor
import django_filters

class ProposalTable(tables.Table):

    name = tables.LinkColumn('app_proposals_detail', args=[A('slug')])
    proposer  = tables.LinkColumn('app_contacts_detail', args=[A('proposer.contact.pk')], text=lambda record: record.proposer.contact.name)
    pid = tables.Column(attrs={'td': {'class': 'font-weight-bold'}})

    def render_supervisor(self, record):
        if record.student:
            return "✔ (%s)" % record.supervisor
        return "✘"

    class Meta:
        model = Proposals
        template_name = 'django_tables2/bootstrap4.html'
        exclude = ('id', 'abstract', 'slug', 'student') 
        sequence = ('pid', 'name', '...')
        attrs  = { 'class': 'table table-striped table-sm table-hover'}
        

def localcontacts(request):
    if request is None or not request.user.is_authenticated:
        return Contacts.objects.none()

    qs = Contacts.objects.filter(uid__in = User.objects.filter(groups__name__in=['localcontacts']))
    return qs

class ProposalFilter(django_filters.FilterSet):

    #owner = django_filters.filters.ChoiceFilter(choices=('mine', 'all'))
    local_contact = django_filters.ModelChoiceFilter(queryset=localcontacts, empty_label='local contact')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'filtering' in self.request.resolver_match.kwargs and self.request.resolver_match.kwargs['filtering']  == "mine":
            self.filters.pop("local_contact")

    class Meta:
        model = Proposals
        fields = ['proposaltype', 'last_status'] #, 'owner']