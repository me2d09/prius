# app/tables.py
import django_tables2 as tables
from .models import Proposals
from django_tables2.utils import A  # alias for Accessor
import django_filters

class ProposalTable(tables.Table):

    name = tables.LinkColumn('app_proposals_detail', args=[A('slug')])
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
        


class ProposalFilter(django_filters.FilterSet):

    #owner = django_filters.filters.ChoiceFilter(choices=('mine', 'all'))

    class Meta:
        model = Proposals
        fields = ['proposaltype', 'last_status'] #, 'owner']