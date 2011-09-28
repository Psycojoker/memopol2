from datetime import date
from django.db import models
from django.db.models import Count
from django.contrib.comments.moderation import CommentModerator, moderator
from django.core.urlresolvers import reverse
from memopol2.utils import reify
from snippets import snippet
import search

from reps.models import Representative, Party

class MepsContainerManager(models.Manager):
    """ Manager for models to which the MEP model has a foreign key"""
    def with_counts(self):
        """ Return the models with a count property, with the count of active meps """
        # FIXME don't work as expected now, show historical count instead of current count
        return self.get_query_set().filter(mep__active=True).annotate(count=models.Count('mep'))


class Country(models.Model):
    code = models.CharField(max_length=2, unique=True)
    name = models.CharField(max_length=30, unique=True)

    objects = MepsContainerManager()

    def __unicode__(self):
        return u"%s - %s" % (self.code, self.name)

    @property
    def meps(self):
        return self.mep_set.filter(active=True, countrymep__end=date(9999, 12, 31)).distinct()

    def meps_on_date(self, date):
        return self.mep_set.filter(groupmep__end__gte=date, groupmep__begin__lte=date).distinct()

    class Meta:
        ordering = ["code"]


@search.searchable
class Group(models.Model):
    abbreviation = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100, unique=True)

    objects = MepsContainerManager()

    def __unicode__(self):
        return u"%s - %s" % (self.abbreviation, self.name)
    content = __unicode__

    def get_absolute_url(self):
        return reverse('meps:index_by_group', args=(self.abbreviation,))

    @property
    def meps(self):
        return self.mep_set.filter(active=True, groupmep__end=date(9999, 12, 31)).distinct()

    def meps_on_date(self, date):
        return self.mep_set.filter(groupmep__end__gte=date, groupmep__begin__lte=date).distinct()



@search.searchable
class Delegation(models.Model):
    name = models.CharField(max_length=255, unique=True)

    objects = MepsContainerManager()

    def __unicode__(self):
        return self.name
    content = __unicode__

    def get_absolute_url(self):
        return reverse('meps:index_by_delegation', args=(self.id,))

    @property
    def meps(self):
        return self.mep_set.filter(active=True, delegationrole__end=date(9999, 12, 31)).distinct()


@search.searchable
class Committee(models.Model):
    name = models.CharField(max_length=255, unique=True)
    abbreviation = models.CharField(max_length=30, unique=True)

    objects = MepsContainerManager()

    def __unicode__(self):
        return u"%s: %s" % (self.abbreviation, self.name)
    content = __unicode__

    def get_absolute_url(self):
        return reverse('meps:index_by_committee', args=(self.abbreviation,))

    @property
    def meps(self):
        return self.mep_set.filter(active=True, committeerole__end=date(9999, 12, 31)).distinct()

    @classmethod
    def ordered_by_meps_count(cls):
        return cls.objects.distinct().filter(committeerole__mep__active=True, committeerole__end=date(9999, 12, 31)).annotate(meps_count=Count('committeerole__mep', distinct=True)).order_by('-meps_count')


class Building(models.Model):
    """ A building of the European Parliament"""
    name = models.CharField(max_length=255)
    id = models.CharField('Abbreviation', max_length=255, primary_key=True)
    street = models.CharField(max_length=255)
    postcode = models.CharField(max_length=255)

    @reify
    def _town(self):
        return "bxl" if self.postcode == "1047" else "stg"

    @reify
    def floors(self):
        floors = []
        def add(x):
            if getattr(x, "%s_floor" % self._town) not in floors:
                floors.append(getattr(x, "%s_floor" % self._town))
        map(add, MEP.objects.filter(active=True, **{'%s_building' % self._town: self}).order_by("%s_floor" % self._town))
        return floors

    @reify
    def meps(self):
        return MEP.objects.filter(active=True, **{'%s_building' % self._town: self})

@search.searchable
class Organization(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.name
    content = __unicode__

    def get_absolute_url(self):
        return reverse('meps:index_by_organization', args=(self.id,))

    @property
    def meps(self):
        return self.mep_set.filter(active=True, organizationmep__end=date(9999, 12, 31)).distinct()



@search.searchable
class MEP(Representative):
    active = models.BooleanField()
    ep_id = models.IntegerField(unique=True)
    ep_opinions = models.URLField()
    ep_debates = models.URLField()
    ep_questions = models.URLField()
    ep_declarations = models.URLField()
    ep_reports = models.URLField()
    ep_motions = models.URLField()
    ep_webpage = models.URLField()
    bxl_building = models.ForeignKey(Building, related_name="bxl_building")
    bxl_floor = models.CharField(max_length=255)
    bxl_office_number = models.CharField(max_length=255)
    bxl_fax = models.CharField(max_length=255)
    bxl_phone1 = models.CharField(max_length=255)
    bxl_phone2 = models.CharField(max_length=255)
    stg_building = models.ForeignKey(Building, related_name="stg_building")
    stg_floor = models.CharField(max_length=255)
    stg_office_number = models.CharField(max_length=255)
    stg_fax = models.CharField(max_length=255)
    stg_phone1 = models.CharField(max_length=255)
    stg_phone2 = models.CharField(max_length=255)
    groups = models.ManyToManyField(Group, through='GroupMEP')
    countries = models.ManyToManyField(Country, through='CountryMEP')
    delegations = models.ManyToManyField(Delegation, through='DelegationRole')
    committees = models.ManyToManyField(Committee, through='CommitteeRole')
    organizations = models.ManyToManyField(Organization, through='OrganizationMEP')
    position = models.IntegerField(default=None, null=True)
    total_score = models.FloatField(default=None, null=True)

    @reify
    def get_ep_webpage(self):
        if self.active and self.ep_webpage:
            return self.ep_webpage
        return None

    def get_absolute_url(self):
        return reverse('meps:mep', args=(self.id,))

    @reify
    def bxl_office(self):
        return self.bxl_floor + self.bxl_office_number

    @reify
    def stg_office(self):
        return self.stg_floor + self.stg_office_number

    @reify
    def group(self):
        return self.groupmep_set.latest('end').group

    @reify
    def groupmep(self):
        return self.groupmep_set.latest('end')

    @reify
    def country(self):
        return self.countrymep_set.latest('end').country

    @reify
    def party(self):
        return self.countrymep_set.latest('end').party

    @reify
    def previous_mandates(self):
        return self.countrymep_set.filter(end__lt=date(9999, 12, 31)).order_by('-end')

    @reify
    def current_delegations(self):
        return self.delegationrole_set.filter(end=date(9999, 12, 31))

    @reify
    def old_delegations(self):
        return self.delegationrole_set.filter(end__lt=date(9999, 12, 31)).order_by('-end')

    @reify
    def current_committees(self):
        return self.committeerole_set.filter(end=date(9999, 12, 31))

    @reify
    def old_committees(self):
        return self.committeerole_set.filter(end__lt=date(9999, 12, 31)).order_by('-end')

    @reify
    def current_organizations(self):
        return self.organizationmep_set.filter(end=date(9999, 12, 31))

    @reify
    def old_organizations(self):
        return self.organizationmep_set.exclude(end=date(9999, 12, 31)).order_by('-end')

    @property
    def score_color(self):
        red = 255 - self.total_score
        green = self.total_score * 2.55
        return "rgb(%d, %d, 0)" % (red, green)

    @snippet(template='meps/snippets/country.html')
    def country_tag(self):
        return dict(country=self.countrymep_set.latest('end').country)

    @snippet(template='meps/snippets/party.html')
    def party_tag(self):
        return dict(group=self.groupmep_set.latest('end').group)

    @reify
    def important_posts(self):
        all_roles = list(OrganizationMEP.objects.filter(mep=self, end__gt=date.today()))
        for i in (GroupMEP, CommitteeRole, DelegationRole):
            roles = i.objects.filter(mep=self, end__gt=date.today()).exclude(role="Member").exclude(role="Substitute")
            if roles:
                all_roles += list(roles)
        return all_roles

    class Meta:
        ordering = ['last_name']


class GroupMEP(models.Model):
    mep = models.ForeignKey(MEP)
    group = models.ForeignKey(Group)
    role = models.CharField(max_length=255)
    begin = models.DateField(null=True)
    end = models.DateField(null=True)

    @reify
    def instance(self):
        return self.group


class DelegationRole(models.Model):
    mep = models.ForeignKey(MEP)
    delegation = models.ForeignKey(Delegation)
    role = models.CharField(max_length=255)
    begin = models.DateField(null=True)
    end = models.DateField(null=True)

    @reify
    def instance(self):
        return self.delegation

    def __unicode__(self):
        return u"%s : %s" % (self.mep.full_name, self.delegation)


class CommitteeRole(models.Model):
    mep = models.ForeignKey(MEP)
    committee = models.ForeignKey(Committee)
    role = models.CharField(max_length=255)
    begin = models.DateField(null=True)
    end = models.DateField(null=True)

    @reify
    def instance(self):
        return self.committee

    def __unicode__(self):
        return u"%s : %s" % (self.committee.abbreviation, self.mep.full_name)


class PostalAddress(models.Model):
    addr = models.CharField(max_length=255)
    mep = models.ForeignKey(MEP)


class CountryMEP(models.Model):
    mep = models.ForeignKey(MEP)
    country = models.ForeignKey(Country)
    party = models.ForeignKey(Party)
    begin = models.DateField()
    end = models.DateField()


class OrganizationMEP(models.Model):
    mep = models.ForeignKey(MEP)
    organization = models.ForeignKey(Organization)
    role = models.CharField(max_length=255)
    begin = models.DateField()
    end = models.DateField()

    @reify
    def instance(self):
        return self.organization


class MepModerator(CommentModerator):
    email_notification = True
    moderate_after        = 0
    def moderate(self, comment, content_object, request):
        return True


moderator.register(MEP, MepModerator)
