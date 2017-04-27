# -*- coding: utf-8 -*-
"""
    aidex.queries
    ~~~~~~~~~~~~~~~~
    home for "more" complicated queries of aidex data
"""
from sqlalchemy import func, or_
from unidecode import unidecode
from .helpers import to_regex_or
from .models import Location, Org


def join_locations(query, cities=None, country=None, **kwargs):
    loc_filters = []
    if cities:
        cities_regex = to_regex_or(*cities)
        loc_filters.append(Location.city.op('~*')(cities_regex))
    if country:
        loc_filters.append(Location.country.ilike(unidecode(country)))
    if loc_filters:
        return query.join(Location).filter(*loc_filters)
    return query


def filter_orgs(query, keywords=None, categories=None, **kwargs):
    if keywords:
        keyword_regex = to_regex_or(*keywords)
        query = query.filter(
            or_(Org.name.op('~*')(keyword_regex),
                func.array_to_string(Org.services, " ").op('~*')(keyword_regex),
                Org.mission.op('~*')(keyword_regex)))
    if categories:
        categories_regex = to_regex_or(*categories)
        query = query.filter(
            func.array_to_string(Org.categories, " ").op("~*")(categories_regex))

    return join_locations(query, **kwargs)
