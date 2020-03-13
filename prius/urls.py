"""
Definition of urls for prius.
"""

from datetime import datetime
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.urls import path

from django.contrib.auth import views as auth_views

import app.forms
import app.views as views
from app.rest import MyProposalList

# Uncomment the next lines to enable the admin:
from django.contrib import admin

from django.contrib.auth.decorators import user_passes_test
import oauth2_provider.views as oauth2_views

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
    url(r'^password_reset/$', auth_views.PasswordResetView.as_view(form_class=app.forms.CrispyPasswordReset), name='password_reset'),
    url(r'^password_reset/done/$', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(form_class=app.forms.CrispySetPassword), name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    url(r'^login',
        auth_views.LoginView.as_view(),
        {
            'template_name': 'app/login.html',
            'authentication_form': app.forms.BootstrapAuthenticationForm,
        },
        name='login'),
    url(r'^logout',
        auth_views.LogoutView.as_view(),
        {
            'next_page': '/login/',
        },
        name='logout'),
    url(r'^signup/$', app.views.signup, name='signup'),
    url(r'^resend/(?P<userpk>\S+)/$', app.views.resend, name='resend'),
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
    url(r'^proposals/(?P<proposal_slug>\S+)/report/create/$', views.ReportCreateView.as_view(), name='app_report_create'),
    url(r'^proposals/report/detail/(?P<pk>\S+)/$', views.ReportDetailView.as_view(), name='app_report_detail'),
    url(r'^proposals/report/update/(?P<pk>\S+)/$', views.ReportUpdateView.as_view(), name='app_report_update'),
)

urlpatterns += (
    # urls for Contacts
    url(r'^contacts/$', views.ContactsListView.as_view(), name='app_contacts_list'),
    url(r'^contacts/create/$', views.ContactsCreateView.as_view(), name='app_contacts_create'),
    url(r'^contacts/detail/(?P<pk>\S+)/$', views.ContactsDetailView.as_view(), name='app_contacts_detail'),
    url(r'^contacts/update/(?P<pk>\S+)/$', views.ContactsUpdateView.as_view(), name='app_contacts_update'),
)

urlpatterns += (
    # urls for PDF
    url(r'^proposal_pdf/(?P<pid>\S+)/', views.ProposalPdfDetailView.as_view(), name='proposal_pdf_detail_view',),
)

urlpatterns += (
    # other urls
    url(r"^notifications/", include("pinax.notifications.urls", namespace="pinax_notifications")),
)


urlpatterns += (
    # urls for Experiments
    url(r'^experiments/calendar/$', views.ExperimentsCalendarView.as_view(), name='app_experiments_calendar'),
    url(r'^experiments/myslots/$', views.ExperimentsListView.as_view(), {'filtering':'mine'}, name='app_experiments_mylist'),
    url(r'^experiments/LC/$', views.ExperimentsListView.as_view(), {'filtering':'all'}, name='app_experiments_mylist'),
    url(r'^experiments/create/$', views.ExperimentsCreateView.as_view(), name='app_experiments_create'),
    url(r'^experiments/detail/(?P<pk>\S+)/$', views.ExperimentsDetailView.as_view(), name='app_experiments_detail'),
    url(r'^experiments/update/(?P<pk>\S+)/$', views.ExperimentsUpdateView.as_view(), name='app_experiments_update'),
    url(r'^experiments/delete/(?P<pk>\S+)/$', views.ExperimentsDeleteView.as_view(), name='app_experiments_delete'),
    url(r'^sharedslots/detail/(?P<pk>\S+)/$', views.SharedOptionSlotDetailView.as_view(), name='app_sharedoptionslot_detail'),
    url(r'^sharedslots/update/(?P<pk>\S+)/$', views.SharedOptionSlotUpdateView.as_view(), name='app_sharedoptionslot_update'),

    path('ajax/load-options/', views.load_options, name='ajax_load_options'), 
    path('ajax/load-shared-options/', views.load_shared_options, name='ajax_shared_load_options'), 
    path('ajax/load-lc/', views.load_lc, name='ajax_load_lc'), 
    path('ajax/get-fulldays/', views.get_fulldays, name='ajax_full_days'), 
    path('ajax/get-events/', views.get_events, name='ajax_get_events'), 
)



## oauth2 implementation
def is_super(user):
    return user.is_superuser and user.is_active

# OAuth2 provider endpoints
oauth2_endpoint_views = [
    path('authorize/', oauth2_views.AuthorizationView.as_view(), name="authorize"),
    path('token/', oauth2_views.TokenView.as_view(), name="token"),
    path('revoke-token/', oauth2_views.RevokeTokenView.as_view(), name="revoke-token"),
]
# the above are public but we restrict the following:
# OAuth2 Application Management endpoints
oauth2_endpoint_views += [
    path('applications/', user_passes_test(is_super)(oauth2_views.ApplicationList.as_view()), name="list"),
    path('applications/register/', user_passes_test(is_super)(oauth2_views.ApplicationRegistration.as_view()), name="register"),
    path('applications/<pk>/', user_passes_test(is_super)(oauth2_views.ApplicationDetail.as_view()), name="detail"),
    path('applications/<pk>/delete/', user_passes_test(is_super)(oauth2_views.ApplicationDelete.as_view()), name="delete"),
    path('applications/<pk>/update/', user_passes_test(is_super)(oauth2_views.ApplicationUpdate.as_view()), name="update"),
]
oauth2_endpoint_views += [
    path('authorized-tokens/', user_passes_test(is_super)(oauth2_views.AuthorizedTokensListView.as_view()), name="authorized-token-list"),
    path('authorized-tokens/<pk>/delete/', user_passes_test(is_super)(oauth2_views.AuthorizedTokenDeleteView.as_view()),
        name="authorized-token-delete"),
]

oauth2_patterns = (oauth2_endpoint_views, "oauth2_provider")

urlpatterns += (
    # OAuth 2 endpoints:
    path("o/", include(oauth2_patterns)),
)

# REST API
urlpatterns += [
    path('rest/activeproposals/', MyProposalList.as_view()),
]