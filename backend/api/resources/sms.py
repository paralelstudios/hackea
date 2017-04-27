# -*- coding: utf-8 -*-
"""
    api.resources.sms
    ~~~~~~~~~~~~~~~~
    SMS API resources
"""
from flask import request, make_response
from flask_restful import Resource
from unidecode import unidecode
from datetime import datetime, timedelta
from twilio import twiml
from aidex.models import Org
from aidex.queries import filter_orgs
from ..helpers import (
    output_xml, twilio_send_not_found,
    clean_and_split, get_page_offset)


class SMSOrgEndpoint(Resource):
    uri = '/sms/orgs'
    representations = {'application/xml': output_xml}
    _default_limit = 3
    _not_found_msg =  \
        """Gracias por utilizar AIDEX
        No encontramos su criterio.\nConsejos:
        Escribe palabras claves (separadas por una coma)
        de la org que
        buscas, si deseas puedes buscar dentro
        de un municipio escribe "/"; seguido del
        municipio. Ej: educacion/San Juan. :)"""

    def _org_row_format(self, org):
        return "{name} tel: {phone}".format(name=org.name, phone=org.phone)

    def _process_query(self, body):
        raw_query = body.split('/')
        keywords = clean_and_split(raw_query[0])
        cities = clean_and_split(raw_query[1]) if len(raw_query) > 1 else None
        return keywords, cities

    def _process_body(self, body):
        page = int(request.cookies.get('page', 0))
        if body == "+":
            query = request.cookies.get('query')
            if not query:
                return None, page
            return query, page + 1
        return unidecode(body), page

    def post(self):
        raw_body = request.args.get('Body') or request.form.get('Body')

        body, page = self._process_body(raw_body)

        if not body or body == "guia":
            return twilio_send_not_found(self._not_found_msg)

        offset = get_page_offset(page, self._default_limit)
        keywords, cities = self._process_query_str(body)
        query = filter_orgs(Org.query, keywords=keywords, cities=cities)
        count = query.count()
        if not count:
            return twilio_send_not_found(self._not_found_msg)

        results = [self._org_row_format(org)
                   for org in
                   query.limit(self._default_limit).offset(offset)]

        message = '\n'.join(
            ['Encontramos {} organizaciones bajo "{}" (mostrando {}):'.format(
                count,
                body,
                self._default_limit)] +
            results)

        if count - offset > self._default_limit:
            message += '\nPara más resultados, responda con "+"'
        else:
            message += '\nNo hay más resultados'

        resp = twiml.Response()
        resp.message(message)
        return self._process_response(resp, body, page)

    def _process_response(self, resp, body, page):
        out_resp = make_response(str(resp))
        expires = datetime.utcnow() + timedelta(hours=4)
        if body not in {"guia", "+"}:
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
