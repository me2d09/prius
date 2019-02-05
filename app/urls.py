from django.conf.urls import url, include
from rest_framework import routers
from . import api
from . import views

router = routers.DefaultRouter()
router.register(r'proposals', api.ProposalsViewSet)
router.register(r'instruments', api.InstrumentsViewSet)
router.register(r'contacts', api.ContactsViewSet)
router.register(r'affiliations', api.AffiliationsViewSet)
router.register(r'countries', api.CountriesViewSet)
router.register(r'instrumentrequest', api.InstrumentRequestViewSet)
router.register(r'options', api.OptionsViewSet)
router.register(r'sharedoptions', api.SharedOptionsViewSet)
router.register(r'instrumentparametersets', api.InstrumentParameterSetsViewSet)
router.register(r'instrumentparameters', api.InstrumentParametersViewSet)
router.register(r'parametervalues', api.ParameterValuesViewSet)
router.register(r'samples', api.SamplesViewSet)
router.register(r'samplephotos', api.SamplePhotosViewSet)
router.register(r'sampleremarks', api.SampleRemarksViewSet)
router.register(r'publications', api.PublicationsViewSet)
router.register(r'experiments', api.ExperimentsViewSet)
router.register(r'slots', api.SlotsViewSet)


urlpatterns = (
    #urls for Django Rest Framework API
    url(r'^api/v1/', include(router.urls)),
)

urlpatterns += (
    # urls for Instruments
    url(r'^instruments/$', views.InstrumentsListView.as_view(), name='app_instruments_list'),
    url(r'^instruments/create/$', views.InstrumentsCreateView.as_view(), name='app_instruments_create'),
    url(r'^instruments/detail/(?P<slug>\S+)/$', views.InstrumentsDetailView.as_view(), name='app_instruments_detail'),
    url(r'^instruments/update/(?P<slug>\S+)/$', views.InstrumentsUpdateView.as_view(), name='app_instruments_update'),
)

urlpatterns += (
    # urls for Affiliations
    url(r'^affiliations/$', views.AffiliationsListView.as_view(), name='app_affiliations_list'),
    url(r'^affiliations/create/$', views.AffiliationsCreateView.as_view(), name='app_affiliations_create'),
    url(r'^affiliations/detail/(?P<pk>\S+)/$', views.AffiliationsDetailView.as_view(), name='app_affiliations_detail'),
    url(r'^affiliations/update/(?P<pk>\S+)/$', views.AffiliationsUpdateView.as_view(), name='app_affiliations_update'),
)

urlpatterns += (
    # urls for Countries
    url(r'^countries/$', views.CountriesListView.as_view(), name='app_countries_list'),
    url(r'^countries/create/$', views.CountriesCreateView.as_view(), name='app_countries_create'),
    url(r'^countries/detail/(?P<pk>\S+)/$', views.CountriesDetailView.as_view(), name='app_countries_detail'),
    url(r'^countries/update/(?P<pk>\S+)/$', views.CountriesUpdateView.as_view(), name='app_countries_update'),
)

urlpatterns += (
    # urls for InstrumentRequest
    url(r'^instrumentrequest/$', views.InstrumentRequestListView.as_view(), name='app_instrumentrequest_list'),
    url(r'^instrumentrequest/create/$', views.InstrumentRequestCreateView.as_view(), name='app_instrumentrequest_create'),
    url(r'^instrumentrequest/detail/(?P<pk>\S+)/$', views.InstrumentRequestDetailView.as_view(), name='app_instrumentrequest_detail'),
    url(r'^instrumentrequest/update/(?P<pk>\S+)/$', views.InstrumentRequestUpdateView.as_view(), name='app_instrumentrequest_update'),
)

urlpatterns += (
    # urls for Options
    url(r'^options/$', views.OptionsListView.as_view(), name='app_options_list'),
    url(r'^options/create/$', views.OptionsCreateView.as_view(), name='app_options_create'),
    url(r'^options/detail/(?P<slug>\S+)/$', views.OptionsDetailView.as_view(), name='app_options_detail'),
    url(r'^options/update/(?P<slug>\S+)/$', views.OptionsUpdateView.as_view(), name='app_options_update'),
)

urlpatterns += (
    # urls for SharedOptions
    url(r'^sharedoptions/$', views.SharedOptionsListView.as_view(), name='app_sharedoptions_list'),
    url(r'^sharedoptions/create/$', views.SharedOptionsCreateView.as_view(), name='app_sharedoptions_create'),
    url(r'^sharedoptions/detail/(?P<slug>\S+)/$', views.SharedOptionsDetailView.as_view(), name='app_sharedoptions_detail'),
    url(r'^sharedoptions/update/(?P<slug>\S+)/$', views.SharedOptionsUpdateView.as_view(), name='app_sharedoptions_update'),
)

urlpatterns += (
    # urls for InstrumentParameterSets
    url(r'^instrumentparametersets/$', views.InstrumentParameterSetsListView.as_view(), name='app_instrumentparametersets_list'),
    url(r'^instrumentparametersets/create/$', views.InstrumentParameterSetsCreateView.as_view(), name='app_instrumentparametersets_create'),
    url(r'^instrumentparametersets/detail/(?P<pk>\S+)/$', views.InstrumentParameterSetsDetailView.as_view(), name='app_instrumentparametersets_detail'),
    url(r'^instrumentparametersets/update/(?P<pk>\S+)/$', views.InstrumentParameterSetsUpdateView.as_view(), name='app_instrumentparametersets_update'),
)

urlpatterns += (
    # urls for InstrumentParameters
    url(r'^instrumentparameters/$', views.InstrumentParametersListView.as_view(), name='app_instrumentparameters_list'),
    url(r'^instrumentparameters/create/$', views.InstrumentParametersCreateView.as_view(), name='app_instrumentparameters_create'),
    url(r'^instrumentparameters/detail/(?P<pk>\S+)/$', views.InstrumentParametersDetailView.as_view(), name='app_instrumentparameters_detail'),
    url(r'^instrumentparameters/update/(?P<pk>\S+)/$', views.InstrumentParametersUpdateView.as_view(), name='app_instrumentparameters_update'),
)

urlpatterns += (
    # urls for ParameterValues
    url(r'^parametervalues/$', views.ParameterValuesListView.as_view(), name='app_parametervalues_list'),
    url(r'^parametervalues/create/$', views.ParameterValuesCreateView.as_view(), name='app_parametervalues_create'),
    url(r'^parametervalues/detail/(?P<pk>\S+)/$', views.ParameterValuesDetailView.as_view(), name='app_parametervalues_detail'),
    url(r'^parametervalues/update/(?P<pk>\S+)/$', views.ParameterValuesUpdateView.as_view(), name='app_parametervalues_update'),
)

urlpatterns += (
    # urls for Samples
    url(r'^samples/$', views.SamplesListView.as_view(), name='app_samples_list'),
    url(r'^samples/create/$', views.SamplesCreateView.as_view(), name='app_samples_create'),
    url(r'^samples/detail/(?P<pk>\S+)/$', views.SamplesDetailView.as_view(), name='app_samples_detail'),
    url(r'^samples/update/(?P<pk>\S+)/$', views.SamplesUpdateView.as_view(), name='app_samples_update'),
)

urlpatterns += (
    # urls for SamplePhotos
    url(r'^samplephotos/$', views.SamplePhotosListView.as_view(), name='app_samplephotos_list'),
    url(r'^samplephotos/create/$', views.SamplePhotosCreateView.as_view(), name='app_samplephotos_create'),
    url(r'^samplephotos/detail/(?P<pk>\S+)/$', views.SamplePhotosDetailView.as_view(), name='app_samplephotos_detail'),
    url(r'^samplephotos/update/(?P<pk>\S+)/$', views.SamplePhotosUpdateView.as_view(), name='app_samplephotos_update'),
)

urlpatterns += (
    # urls for SampleRemarks
    url(r'^sampleremarks/$', views.SampleRemarksListView.as_view(), name='app_sampleremarks_list'),
    url(r'^sampleremarks/create/$', views.SampleRemarksCreateView.as_view(), name='app_sampleremarks_create'),
    url(r'^sampleremarks/detail/(?P<pk>\S+)/$', views.SampleRemarksDetailView.as_view(), name='app_sampleremarks_detail'),
    url(r'^sampleremarks/update/(?P<pk>\S+)/$', views.SampleRemarksUpdateView.as_view(), name='app_sampleremarks_update'),
)

urlpatterns += (
    # urls for Publications
    url(r'^publications/$', views.PublicationsListView.as_view(), name='app_publications_list'),
    url(r'^publications/create/$', views.PublicationsCreateView.as_view(), name='app_publications_create'),
    url(r'^publications/detail/(?P<pk>\S+)/$', views.PublicationsDetailView.as_view(), name='app_publications_detail'),
    url(r'^publications/update/(?P<pk>\S+)/$', views.PublicationsUpdateView.as_view(), name='app_publications_update'),
)

urlpatterns += (
    # urls for Experiments
    url(r'^experiments/$', views.ExperimentsListView.as_view(), name='app_experiments_list'),
    url(r'^experiments/create/$', views.ExperimentsCreateView.as_view(), name='app_experiments_create'),
    url(r'^experiments/detail/(?P<pk>\S+)/$', views.ExperimentsDetailView.as_view(), name='app_experiments_detail'),
    url(r'^experiments/update/(?P<pk>\S+)/$', views.ExperimentsUpdateView.as_view(), name='app_experiments_update'),
)

urlpatterns += (
    # urls for Slots
    url(r'^slots/$', views.SlotsListView.as_view(), name='app_slots_list'),
    url(r'^slots/create/$', views.SlotsCreateView.as_view(), name='app_slots_create'),
    url(r'^slots/detail/(?P<pk>\S+)/$', views.SlotsDetailView.as_view(), name='app_slots_detail'),
    url(r'^slots/update/(?P<pk>\S+)/$', views.SlotsUpdateView.as_view(), name='app_slots_update'),
)

