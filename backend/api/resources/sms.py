# -*- coding: utf-8 -*-
"""
    api.resources.sms
    ~~~~~~~~~~~~~~~~
    SMS API resources
"""
from flask import request, make_response
from flask_restful import Resource
from datetime import datetime, timedelta
from twilio import twiml
from sqlalchemy import or_, and_
from aidex.models import Org
from api.helpers import (
    output_xml, twilio_send_not_found,
    to_regex_or, sms_org_format,
    clean_and_split, get_page_offset)


class SMSOrgEndpoint(Resource):
    uri = '/sms/orgs'
    representations = {'application/xml': output_xml}

    def _process_query(self, query):
        key_words = query[0]
        locs = query[1] if len(query) > 1 else None
        kw_conditions, loc_conditions = [], []
        kw_regex = to_regex_or(*clean_and_split(query[0]))

        if key_words:
            kw_conditions += [
                Org.name.op('~*')(kw_regex),
                Org.services.op('~*')(kw_regex),
                Org.mission.op('~*')(kw_regex)
            ]

        if locs:
            loc_regex = to_regex_or(*clean_and_split(locs))
            loc = Org.location
            loc_conditions += [
                loc.city.op('~*')(loc_regex),
                loc.country.op('~*')(loc_regex)
            ]

        return and_(or_(*kw_conditions), or_(*loc_conditions))

    def _process_body(self, body):
        page = int(request.cookies.get('page', 0))
        if body == "+":
            query = request.cookies.get('query')
            if not query:
                return None, page
            return query, page + 1
        return body, page

    def post(self):
        raw_body = request.args.get('Body') or request.form.get('Body')
        print(raw_body)
        body, page = self._process_body(raw_body)

        if not body:
            return twilio_send_not_found(
                'favor de formar el mensaje como "causa(s,)/municipio(s,)"')

        query = body.split('/')
        page_offset = get_page_offset(page, self.limit) if page > 0 else page
        conditions = self._process_query(query)
        orgs = list(Org.query.filter(conditions).offset(page_offset))
        if not orgs:
            return twilio_send_not_found("No encontramos nada :(")

        org_names = [sms_org_format(org) for org in orgs]

        message = '\n'.join(
            ['Organizaciones encontrado bajo "{}":'.format(body)] +
            org_names)

        resp = twiml.Response()
        resp.message(message)
        return self._process_response(resp, body, page)

    def _process_response(self, resp, body, page):
        out_resp = make_response(str(resp))
        expires = datetime.utcnow() + timedelta(hours=4)
        out_resp.set_cookie(
            'query',
            body,
            expires=expires.strftime(
                '%a, %d %b %Y %H:%M:%S GMT'))
        out_resp.set_cookie(
            'page',
            str(page),
            expires=expires.strftime(
                '%a, %d %b %Y %H:%M:%S GMT'))

        return out_resp


endpoints = [SMSOrgEndpoint]
