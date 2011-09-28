#!/usr/bin/python
# -*- coding:Utf-8 -*-

import os
import sys
import json
import re
from datetime import datetime, date

from django.db.models import Count

sys.path += [os.path.abspath(os.path.split(__file__)[0])[:-len("parltrack")] + "apps/"]

from meps.utils import update_total_score_of_all_meps, update_meps_positions
from memopol2.utils import update_search_index

from reps.models import Party, PartyRepresentative, Email, WebSite, CV
from meps.models import MEP, Delegation, DelegationRole, PostalAddress, Country, CountryMEP, Organization, OrganizationMEP, Committee, CommitteeRole, Group, GroupMEP, Building

current_meps = "meps.json"

_parse_date = lambda date: datetime.strptime(date, "%Y-%m-%dT00:00:00")

def get_or_create(klass, _id=None, **kwargs):
    if _id is None:
        object = klass.objects.filter(**kwargs)
    else:
        object = klass.objects.filter(**{_id : kwargs[_id]})
    if object:
        return object[0]
    else:
        print "     add new", klass.__name__, kwargs
        return klass.objects.create(**kwargs)

def create_uniq_id(mep_json):
    id = mep_json["Name"]["sur"].capitalize().replace(" ", "") + mep_json["Name"]["family"].capitalize().replace(" ", "")
    id = id.replace(u"Á", u"A")
    id = id.replace(u"À", u"A")
    id = id.replace(u"Â", u"A")
    id = id.replace(u"Ä", u"A")
    id = id.replace(u"Å", u"A")
    id = id.replace(u"Ă", u"A")
    id = id.replace(u"Ã", u"A")
    id = id.replace(u"Ā", u"A")
    id = id.replace(u"É", u"E")
    id = id.replace(u"È", u"E")
    id = id.replace(u"Ê", u"E")
    id = id.replace(u"Ë", u"E")
    id = id.replace(u"Ě", u"E")
    id = id.replace(u"Ė", u"E")
    id = id.replace(u"Ę", u"E")
    id = id.replace(u"Í", u"I")
    id = id.replace(u"Î", u"I")
    id = id.replace(u"Ï", u"I")
    id = id.replace(u"Ī", u"I")
    id = id.replace(u"Ó", u"O")
    id = id.replace(u"Ô", u"O")
    id = id.replace(u"Ö", u"O")
    id = id.replace(u"Ø", u"O")
    id = id.replace(u"Ő", u"O")
    id = id.replace(u"Ù", u"U")
    id = id.replace(u"Û", u"U")
    id = id.replace(u"Ü", u"U")
    id = id.replace(u"Ū", u"U")
    id = id.replace(u"Ý", u"Y")
    id = id.replace(u"Ç", u"C")
    id = id.replace(u"Ľ", u"L")
    id = id.replace(u"Ł", u"L")
    id = id.replace(u"Č", u"C")
    id = id.replace(u"Ģ", u"G")
    id = id.replace(u"Ķ", u"K")
    id = id.replace(u"Ñ", u"n")
    id = id.replace(u"Ň", u"N")
    id = id.replace(u"Ń", u"N")
    id = id.replace(u"Ņ", u"N")
    id = id.replace(u"Ř", u"r")
    id = id.replace(u"Š", u"S")
    id = id.replace(u"Ş", u"S")
    id = id.replace(u"Ś", u"S")
    id = id.replace(u"Ţ", u"T")
    id = id.replace(u"Ť", u"T")
    id = id.replace(u"Ț", u"T")
    id = id.replace(u"Ż", u"Z")
    id = id.replace(u"Ź", u"Z")
    id = id.replace(u"Ž", u"Z")
    id = id.replace(u"á", u"a")
    id = id.replace(u"à", u"a")
    id = id.replace(u"â", u"a")
    id = id.replace(u"ä", u"a")
    id = id.replace(u"å", u"a")
    id = id.replace(u"ă", u"a")
    id = id.replace(u"ã", u"a")
    id = id.replace(u"ā", u"a")
    id = id.replace(u"é", u"e")
    id = id.replace(u"è", u"e")
    id = id.replace(u"ê", u"e")
    id = id.replace(u"ë", u"e")
    id = id.replace(u"ě", u"e")
    id = id.replace(u"ė", u"e")
    id = id.replace(u"ę", u"e")
    id = id.replace(u"í", u"i")
    id = id.replace(u"î", u"i")
    id = id.replace(u"ï", u"i")
    id = id.replace(u"ī", u"i")
    id = id.replace(u"ó", u"o")
    id = id.replace(u"ô", u"o")
    id = id.replace(u"ö", u"o")
    id = id.replace(u"ø", u"o")
    id = id.replace(u"ő", u"o")
    id = id.replace(u"ú", u"u")
    id = id.replace(u"ù", u"u")
    id = id.replace(u"û", u"u")
    id = id.replace(u"ü", u"u")
    id = id.replace(u"ū", u"u")
    id = id.replace(u"ý", u"y")
    id = id.replace(u"ç", u"c")
    id = id.replace(u"č", u"c")
    id = id.replace(u"ģ", u"g")
    id = id.replace(u"ķ", u"k")
    id = id.replace(u"ľ", u"l")
    id = id.replace(u"ł", u"l")
    id = id.replace(u"ñ", u"n")
    id = id.replace(u"ň", u"n")
    id = id.replace(u"ń", u"n")
    id = id.replace(u"ņ", u"n")
    id = id.replace(u"ř", u"r")
    id = id.replace(u"š", u"s")
    id = id.replace(u"ş", u"s")
    id = id.replace(u"ś", u"s")
    id = id.replace(u"ţ", u"t")
    id = id.replace(u"ť", u"t")
    id = id.replace(u"ț", u"t")
    id = id.replace(u"ż", u"z")
    id = id.replace(u"ź", u"z")
    id = id.replace(u"ž", u"z")
    id = re.sub("\W", lambda _: "", id)
    return id

def add_committees(mep, committees):
    CommitteeRole.objects.filter(mep=mep).delete()
    for committee in committees:
        if committee.get("committee_id"):
            try:
                    in_db_committe = Committee.objects.get(abbreviation=committee["committee_id"])
            except Committee.DoesNotExist:
                print "     create new commitee:", committee["committee_id"], committee["Organization"]
                in_db_committe = Committee.objects.create(name=committee["Organization"],
                                                          abbreviation=committee["committee_id"])
            print "     link mep to commmitte:", committee["Organization"]
            CommitteeRole.objects.create(mep=mep, committee=in_db_committe,
                                         role=committee["role"],
                                         begin=_parse_date(committee["start"]),
                                         end=_parse_date(committee["end"]))
        else:
            # FIXME create or how abbreviations ? Or are they really important ? or create a new class ?
            print "WARNING: committe without abbreviation:", committee["Organization"]

def add_delegations(mep, delegations):
    DelegationRole.objects.filter(mep=mep).delete()
    for delegation in delegations:
        db_delegation = get_or_create(Delegation, name=delegation["Organization"])
        print "     create DelegationRole to link mep to delegation"
        DelegationRole.objects.create(mep=mep, delegation=db_delegation,
                                      role=delegation["role"],
                                      begin=_parse_date(delegation["start"]),
                                      end=_parse_date(delegation["end"]))

def add_addrs(mep, addrs):
    print "     add Brussels infos"
    bxl = addrs["Brussels"]
    if bxl["Address"].get("building_code"):
        mep.bxl_building = get_or_create(Building, _id="id",
                                     id=bxl["Address"]["building_code"],
                                     name=bxl["Address"]["Building"],
                                     street=bxl["Address"]["Street"],
                                     postcode=bxl["Address"]["Zip"])
    mep.bxl_floor = bxl["Address"]["Office"][:2]
    mep.bxl_office_number = bxl["Address"]["Office"][2:]
    mep.bxl_fax = bxl["Fax"]
    mep.bxl_phone1 = bxl["Phone"]
    mep.bxl_phone2 = bxl["Phone"][:-4] + "7" + bxl["Phone"][-3:]
    print "     add Strasbourg infos"
    stg = addrs["Strasbourg"]
    if stg["Address"].get("building_code"):
        mep.stg_building = get_or_create(Building, _id="id",
                                     id=stg["Address"]["building_code"],
                                     name=stg["Address"]["Building"],
                                     street=stg["Address"]["Street"],
                                     postcode=stg["Address"].get("Zip", stg["Address"]["Zip1"]))
    mep.stg_floor = stg["Address"]["Office"][:3]
    mep.stg_office_number = stg["Address"]["Office"][3:]
    mep.stg_fax = stg["Fax"]
    mep.stg_phone1 = stg["Phone"]
    mep.stg_phone2 = stg["Phone"][:-4] + "7" + stg["Phone"][-3:]
    print "     adding mep's postal addresses:"
    mep.save()
    PostalAddress.objects.filter(mep=mep).delete()
    for addr in addrs["Postal"]:
        print "       *", addr
        PostalAddress.objects.create(addr=addr, mep=mep)

def add_countries(mep, countries):
    PartyRepresentative.objects.filter(representative=mep.representative_ptr).delete()
    CountryMEP.objects.filter(mep=mep).delete()
    print "     add countries"
    for country in countries:
        party = get_or_create(Party, name=country["party"])
        print "     link representative to party"
        if not PartyRepresentative.objects.filter(representative=mep.representative_ptr, party=party):
            current = True if _parse_date(country["end"]).year > date.today().year else False
            PartyRepresentative.objects.create(representative=mep.representative_ptr,
                                               party=party, current=current)
        _country = Country.objects.get(name=country["country"])
        print "     link mep to country", '"%s"' % country["country"], "for a madate"
        CountryMEP.objects.create(mep=mep, country=_country, party=party,
                                  begin=_parse_date(country["start"]),
                                  end=_parse_date(country["end"]))

def add_organizations(mep, organizations):
    OrganizationMEP.objects.filter(mep=mep).delete()
    for organization in organizations:
        in_db_organization = get_or_create(Organization, name=organization["Organization"])
        print "     link mep to organization:", in_db_organization.name
        OrganizationMEP.objects.create(mep=mep,
                                       organization=in_db_organization,
                                       role=organization["role"],
                                       begin=_parse_date(organization["start"]),
                                       end=_parse_date(organization["end"]))

def change_mep_details(mep, mep_json):
    if mep_json.get("Birth"):
        print "     update mep birth date"
        mep.birth_date = _parse_date(mep_json["Birth"]["date"])
        print "     update mep birth place"
        mep.birth_place = mep_json["Birth"]["place"]
    print "     update mep first name"
    mep.first_name = mep_json["Name"]["sur"]
    print "     update mep last name"
    mep.last_name = mep_json["Name"]["family"]
    print "     update mep full name"
    mep.full_name = "%s %s" %(mep_json["Name"]["sur"], mep_json["Name"]["family"])

def add_mep_email(mep, email):
    get_or_create(Email, representative=mep.representative_ptr, email=email)

def add_mep_website(mep, url):
    if url:
        get_or_create(WebSite, representative=mep.representative_ptr, url=url)

def add_mep_cv(mep, cv):
    for c in cv:
        if c:
            get_or_create(CV, title=c, representative=mep.representative_ptr)

def add_groups(mep, groups):
    # I don't create group if they don't exist for the moment
    convert = {"S&D": "SD", "NA": "NI", "ID": "IND/DEM", "PPE": "EPP", "Verts/ALE": "Greens/EFA"}
    GroupMEP.objects.filter(mep=mep).delete()
    for group in groups:
        if not group.get("groupid"):
            continue
        print "     link mep to group", group["groupid"], group["Organization"]
        if type(group["groupid"]) is list:
            # I really don't like that hack
            group["groupid"] = group["groupid"][0]
        group["groupid"] = convert.get(group["groupid"], group["groupid"])
        in_db_group = Group.objects.filter(abbreviation=group["groupid"])
        if in_db_group:
            in_db_group = in_db_group[0]
        else:
            in_db_group = Group.objects.create(abbreviation=group["groupid"], name=group["Organization"])
        GroupMEP.objects.create(mep=mep, group=in_db_group, role=group["role"],
                                begin=_parse_date(group["start"]),
                                end=_parse_date(group["end"]))

def manage_mep(mep, mep_json):
    change_mep_details(mep, mep_json)
    mep.committeerole_set.all().delete()
    add_committees(mep, mep_json.get("Committees", []))
    add_delegations(mep, mep_json.get("Delegations", []))
    add_countries(mep, mep_json["Constituencies"])
    add_groups(mep, mep_json["Groups"])
    if mep_json.get("Addresses"):
        add_addrs(mep, mep_json["Addresses"])
    add_organizations(mep, mep_json.get("Staff", []))
    if mep_json.get("Mail"):
        add_mep_email(mep, mep_json["Mail"])
    mep.website_set.filter(url="").delete()
    if mep_json.get("Homepage"):
        add_mep_website(mep, mep_json["Homepage"])
    add_mep_cv(mep, mep_json.get("CV", []))
    print "     save mep modifications"
    mep.save()

def add_missing_details(mep, mep_json):
    mep.ep_id = mep_json["UserID"]

def create_mep(mep_json):
    mep = MEP()
    mep.id = create_uniq_id(mep_json)
    mep.picture = mep.id + ".jpg"
    mep.active = True
    change_mep_details(mep, mep_json)
    add_missing_details(mep, mep_json)
    add_addrs(mep, mep_json["Addresses"])
    mep.save()
    add_committees(mep, mep_json.get("Committees", []))
    add_delegations(mep, mep_json.get("Delegations", []))
    add_countries(mep, mep_json["Constituencies"])
    add_groups(mep, mep_json["Groups"])
    add_organizations(mep, mep_json.get("Staff", []))
    add_mep_email(mep, mep_json["Mail"])
    add_mep_website(mep, mep_json["Homepage"])
    add_mep_cv(mep, mep_json.get("CV", []))
    print "     save mep modifications"
    mep.save()

def clean():
    Delegation.objects.annotate(mep_count=Count('mep')).filter(mep_count=0).delete()
    Committee.objects.annotate(mep_count=Count('mep')).filter(mep_count=0).delete()
    Organization.objects.annotate(mep_count=Count('mep')).filter(mep_count=0).delete()

if __name__ == "__main__":
    print "load json"
    meps = json.load(open(current_meps, "r"))
    a = 0
    count = meps["count"]
    print "Set all current active mep to unactive before importing"
    for mep in MEP.objects.filter(active=True):
        a += 1
        mep.active = False
        mep.save()
        sys.stdout.write("%3i/%i\r" % (a, count))
    sys.stdout.write("%i/%i" % (a, count))
    sys.stdout.write("\n")
    a = 0
    for mep_json in meps["meps"]:
        a += 1
        print a, "-", mep_json["Name"]["full"]
        in_db_mep = MEP.objects.filter(ep_id=mep_json["UserID"])
        if in_db_mep:
            mep = in_db_mep[0]
            mep.active = True
            manage_mep(mep, mep_json)
        else:
            mep = create_mep(mep_json)
    clean()
    print
    update_meps_positions(verbose=True)
    update_search_index()

# vim:set shiftwidth=4 tabstop=4 expandtab:
