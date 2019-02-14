"""
Definition of urls for prius.
"""

from datetime import datetime
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static

import django.contrib.auth.views

import app.forms
import app.views as views

# Uncomment the next lines to enable the admin:
from django.contrib import admin

admin.autodiscover()


urlpatterns = [
    url(r'^$', app.views.home, name='home'),
    url(r'^how-to/proposal$', app.views.proposal_howto, name='proposal-howto'),

    url(r'^profile$', views.ProfileView.as_view(), name='profile'),
    url(r'^profile/(?P<username>[a-zA-Z0-9]*)$', views.ProfileView.as_view()),
    url(r'^create-profile', views.ProfileCreateView.as_view(), name='app_create_profile'),
    url(r'^edit-profile/$', views.ProfileEditView.as_view(), name='app_edit_profile'),
    url(r'^edit-user/$', views.UserUpdateView.as_view(), name='app_edit_user'),
    url(r'^password/$', views.change_password, name='change_password'),
    url(r'^login',
        django.contrib.auth.views.LoginView.as_view(),
        {
            'template_name': 'app/login.html',
            'authentication_form': app.forms.BootstrapAuthenticationForm,
        },
        name='login'),
    url(r'^logout',
        django.contrib.auth.views.LogoutView.as_view(),
        {
            'next_page': '/login/',
        },
        name='logout'),
    url(r'^signup/$', app.views.signup, name='signup'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        app.views.activate, name='activate'),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', admin.site.urls),

    # app urls
    url(r'^app/', include('app.urls')),

    #autocomplete urls
    url(
        r'^contacts-autocomplete/$', views.ContactAutocomplete.as_view(), name='contacts-autocomplete',
    ),
    url(
        r'^localcontacts-autocomplete/$', views.LocalContactAutocomplete.as_view(), name='localcontacts-autocomplete',
    ),
    url(
        r'^affil-autocomplete/$', views.AffilAutocomplete.as_view(create_field='institution'), name='affil-autocomplete',
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += (
    # urls for Proposals
    url(r'^proposals/$', views.ProposalsListView.as_view(), {'filtering':'mine'}, name='app_proposals_list'),
    url(r'^proposals/all/$', views.ProposalsListView.as_view(), {'filtering':'all'}, name='app_proposals_list_all'),
    url(r'^proposals/(?P<pk>\S+)/statushistory/$', views.ProposalsDetailView.as_view(), name='app_proposals_status'),
    url(r'^proposals/create/$', views.ProposalsCreateView.as_view(), name='app_proposals_create'),
    url(r'^proposals/detail/(?P<slug>\S+)/$', views.ProposalsDetailView.as_view(), name='app_proposals_detail'),
    url(r'^proposals/update/(?P<slug>\S+)/$', views.ProposalsUpdateView.as_view(), name='app_proposals_update'),
    url(r'^proposals/delete/(?P<slug>\S+)/$', views.ProposalsDelete.as_view(), name='app_proposals_delete'),
    url(r'^proposals/changestatus/(?P<proposal_slug>\S+)/(?P<new_status>\S+)/$', views.StatusCreateView.as_view(), name='app_status_change'),
    url(r'^proposals/changestatus/(?P<proposal_slug>\S+)/$', views.StatusCreateView.as_view(), name='app_status_new'),
)

urlpatterns += (
    # urls for Contacts
    url(r'^contacts/$', views.ContactsListView.as_view(), name='app_contacts_list'),
    url(r'^contacts/create/$', views.ContactsCreateView.as_view(), name='app_contacts_create'),
    url(r'^contacts/detail/(?P<pk>\S+)/$', views.ContactsDetailView.as_view(), name='app_contacts_detail'),
    url(r'^contacts/update/(?P<pk>\S+)/$', views.ContactsUpdateView.as_view(), name='app_contacts_update'),
)