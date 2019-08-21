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
router.register(r'options', api.OptionsViewSet)
router.register(r'sharedoptions', api.SharedOptionsViewSet)
router.register(r'samples', api.SamplesViewSet)
router.register(r'samplephotos', api.SamplePhotosViewSet)
router.register(r'sampleremarks', api.SampleRemarksViewSet)
router.register(r'publications', api.PublicationsViewSet)
router.register(r'experiments', api.ExperimentsViewSet)


urlpatterns = (
    #urls for Django Rest Framework API
    url(r'^api/v1/', include(router.urls)),
)

urlpatterns += (
    # urls for Instruments
    url(r'^instruments/$', views.InstrumentsListView.as_view(), name='app_instruments_list'),
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


