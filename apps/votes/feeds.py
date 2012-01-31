"""
    This file stores several RSS/Atom feeds :
        - LatestProposalsFeed

    Django doc: https://docs.djangoproject.com/en/dev/ref/contrib/syndication/
    Related issue: https://projets.lqdn.fr/issues/304
"""
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.syndication.views import Feed

from votes.models import Proposal


ITEMS_PER_FEED = 10


class LatestProposalsFeed(Feed):
    title = "Latest Proposals"
    link = settings.ROOT_URL
    description = "This feed provides the latest tracked proposals of %s." % link

    def items(self):
        """
        Return the last ITEMS_PER_FEED proposals.
        """
        # Thanks to http://stackoverflow.com/questions/981375
        sorted_proposals = sorted(Proposal.objects.all(), key=lambda a: a.date)
        return sorted_proposals[-ITEMS_PER_FEED:]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return ""

    def item_link(self, item):
        return reverse('votes:detail', args=[item.id])
