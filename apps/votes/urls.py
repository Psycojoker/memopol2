from django.conf.urls.defaults import patterns, url
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404, render

from votes.models import Proposal, Vote, Recommendation, RecommendationData
from reps.models import Representative
from views import VoteRecommendation, VoteRecommendationChoice

from votes.feeds import LatestProposalsFeed

# TODO: refactor this function, should probably be moved to class based generic views if possible
def proposal_rep(request, proposal_id, mep_id):
    representative = get_object_or_404(Representative, id=mep_id)
    proposal = get_object_or_404(Proposal, id=proposal_id)
    # dirty query because we don't store absent vote
    votes = [Vote.objects.get(representative=representative, recommendation=r)
             if Vote.objects.filter(representative=representative, recommendation=r)
             else {'choice': 'absent', 'recommendation': r, 'representative': representative}
             for r in proposal.recommendation_set.all()]
    context = {'representative': representative, 'proposal': proposal, 'votes': votes}
    return render(request, 'votes/per_rep.html', context)

urlpatterns = patterns('',
    url(r'^$', ListView.as_view(model=Proposal), name='index'),
    url(r'^import/$', ListView.as_view(model=RecommendationData), name='import'),
    url(r'^import/(?P<pk>\d+)/$', DetailView.as_view(model=RecommendationData), name='import_vote'),
    url(r'^(?P<proposal_id>[a-zA-Z/-_]+)/(?P<pk>\d+)/(?P<recommendation>\w+)/$', VoteRecommendationChoice.as_view(model=Recommendation), name='recommendation_choice'),
    url(r'^(?P<proposal_id>[a-zA-Z/-_]+)/(?P<pk>\d+)/$', VoteRecommendation.as_view(model=Recommendation), name='recommendation'),
    url(r'^(?P<pk>[a-zA-Z/-_]+)/dataporn/$', DetailView.as_view(model=Proposal, context_object_name='vote', template_name="votes/proposal_dataporn.html"), name='detail_dataporn'),
    url(r'^(?P<proposal_id>[a-zA-Z/-_]+)/(?P<mep_id>.+)/$', proposal_rep, name='rep'),
    url(r'^(?P<pk>[a-zA-Z/-_]+)/$', DetailView.as_view(model=Proposal, context_object_name='vote'), name='detail'),
    url(r'^latest/feed', LatestProposalsFeed()),
)
