from django.conf.urls import url, include
from . import views

urlpatterns = (
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



