from django.conf.urls.defaults import patterns, url
from django.views.generic import ListView
from memopol2 import utils

from meps.models import Country, Group, Committee, Delegation, Organization, Building, MEP
from reps.models import Party, Opinion
from votes.models import Proposal

from views import BuildingDetailView, MEPView, MEPsFromView, MEPList, PartyView

urlpatterns = patterns('meps.views',
    # those view are *very* expansive. we cache them in RAM for a week
    url(r'^names/$', utils.cached(3600*24*7)(MEPList.as_view()), name='index_names'),
    url(r'^inactive/$', utils.cached(3600*24*7)(MEPList.as_view(active=False)), name='index_inactive'),
    url(r'^score/$', MEPList.as_view(queryset=MEP.objects.filter(active=True).exclude(total_score__isnull=True).order_by('position'), score_listing=True), name='scores'),

    url(r'^opinion/$', ListView.as_view(model=Opinion), name='index_opinions'),
    url(r'^opinion/(?P<pk>[0-9]+)/$', MEPsFromView.as_view(model=Opinion, named_header="reps/opinion_header.html"), name='index_by_opinions'),
    url(r'^organization/$', ListView.as_view(model=Organization), name='index_organizations'),
    url(r'^organization/(?P<pk>[0-9]+)/$', MEPsFromView.as_view(model=Organization, organization_role=True), name='index_by_organization'),
    url(r'^country/$', ListView.as_view(model=Country), name='index_countries'),
    url(r'^country/(?P<slug>[a-zA-Z][a-zA-Z])/$', MEPsFromView.as_view(model=Country, slug_field='code', hidden_fields=['country'], named_header="meps/country_header.html"), name='index_by_country'),
    url(r'^group/$', ListView.as_view(model=Group), name='index_groups'),
    url(r'^group/(?P<slug>[a-zA-Z/-]+)/$', MEPsFromView.as_view(model=Group, hidden_fields=['group'], slug_field="abbreviation", named_header="meps/group_header.html", group_role=True),  name='index_by_group'),
    url(r'^committee/$', ListView.as_view(queryset=Committee.ordered_by_meps_count()), name='index_committees'),
    url(r'^committee/(?P<slug>[A-Z]+)/$', MEPsFromView.as_view(model=Committee, slug_field="abbreviation", committee_role=True), name='index_by_committee'),
    url(r'^delegation/$', ListView.as_view(model=Delegation), name='index_delegations'),
    url(r'^delegation/(?P<pk>[0-9]+)/$', MEPsFromView.as_view(model=Delegation, delegation_role=True), name='index_by_delegation'),
    url(r'^party/$', ListView.as_view(model=Party), name='index_parties'),
    url(r'^party/(?P<pk>[0-9]+)-(?P<slugified_name>[0-9a-z\-]*)/$', PartyView.as_view(),  name='index_by_party'),
    url(r'^floor/$', ListView.as_view(queryset=Building.objects.order_by('postcode')), name='index_floor'),
    url(r'^floor/brussels/(?P<pk>\w+)/(?P<floor>\w+)/$', BuildingDetailView.as_view(), name='bxl_floor'),
    url(r'^floor/strasbourg/(?P<pk>\w+)/(?P<floor>\w+)/$', BuildingDetailView.as_view(), name='stg_floor'),

    url(r'^votes/$', ListView.as_view(queryset=Proposal.objects.filter(institution="EU")), name='index_votes'),

    url(r'^deputy/(?P<pk>\w+)/$', MEPView.as_view(), name='mep'),
    url(r'^deputy/(?P<pk>\w+)/dataporn/$', MEPView.as_view(template_name="meps/dataporn.html"), name='mep_dataporn'),
    url(r'^deputy/(?P<pk>\w+)/contact$', MEPView.as_view(template_name="meps/mep_contact.html"), name='mep_contact'),
)

urlpatterns += patterns('meps.views',
    url(r'^mep/(?P<ep_id>[0-9]+)/picture.jpg$', 'get_mep_picture',
        name='mep-picture'),
)
