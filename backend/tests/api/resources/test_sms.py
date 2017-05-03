# -*- coding: utf-8 -*-
"""
    tests.api.resources.test_sms
    ~~~~~~~~~~~~~~~~
    Tests SMS API resources
"""
import pytest


@pytest.mark.functional
def test_sms_org_post(client, orgs_sample):
    resp = client.post("/sms/orgs", data={"Body": "guia"})
    assert resp.status_code == 200
    assert resp.data == b'"<?xml version=\\"1.0\\" encoding=\\"UTF-8\\"?><Response><Message><Body>Gracias por utilizar AIDEX\\n        No encontramos su criterio.\\nConsejos:\\n        Escribe palabras claves (separadas por una coma)\\n        de la org que\\n        buscas, si deseas puedes buscar dentro\\n        de un municipio escribe \\"/\\"; seguido del\\n        municipio. Ej: educacion/San Juan. :)</Body></Message></Response>"\n'  # noqa

    # test one keyword
    resp = client.post("/sms/orgs", data={"Body": "talleres"})
    assert resp.data == b'<?xml version="1.0" encoding="UTF-8"?><Response><Message><Body>Encontramos 4 organizaciones bajo "talleres" (mostrando 3):\nSoluna Art Foundation Inc. tel: 7872414881\nJovenes de PR en Riesgo tel: 7877535541\nEclectico Internacional Inc tel: 7875872014\nPara m&#225;s resultados, responda con "+"</Body></Message></Response>'  # noqa

    # tests one keyword and municipio
    resp = client.post("/sms/orgs", data={"Body": "talleres/san juan"})
    assert resp.data == b'<?xml version="1.0" encoding="UTF-8"?><Response><Message><Body>Encontramos 2 organizaciones bajo "talleres/san juan" (mostrando 2):\nJovenes de PR en Riesgo tel: 7877535541\nSociedad Americana contra el cancer de Puerto Rico tel: 7877642295\nNo hay m&#225;s resultados</Body></Message></Response>'  # noqa

    # test multi keyword and municipio
    resp = client.post("/sms/orgs", data={"Body": "talleres, tutoría/san juan, guaynabo"})
    assert resp.data == b'<?xml version="1.0" encoding="UTF-8"?><Response><Message><Body>Encontramos 3 organizaciones bajo "talleres, tutoria/san juan, guaynabo" (mostrando 3):\nCaras con causa tel: 7872352151\nJovenes de PR en Riesgo tel: 7877535541\nSociedad Americana contra el cancer de Puerto Rico tel: 7877642295\nNo hay m&#225;s resultados</Body></Message></Response>'  # noqa

    # test multi keyword
    resp = client.post("/sms/orgs", data={"Body": "talleres, tutorías"})
    assert resp.data == b'<?xml version="1.0" encoding="UTF-8"?><Response><Message><Body>Encontramos 6 organizaciones bajo "talleres, tutorias" (mostrando 3):\nCaras con causa tel: 7872352151\nSoluna Art Foundation Inc. tel: 7872414881\nASPIRA Inc. de Puerto Rico tel: 7876411985\nPara m&#225;s resultados, responda con "+"</Body></Message></Response>'  # noqa
    resp = client.post("/sms/orgs", data={"Body": "+"})
    assert resp.data == b'<?xml version="1.0" encoding="UTF-8"?><Response><Message><Body>m&#225;s organizaciones bajo "talleres, tutorias" (mostrando 3 de 6):\nJovenes de PR en Riesgo tel: 7877535541\nEclectico Internacional Inc tel: 7875872014\nSociedad Americana contra el cancer de Puerto Rico tel: 7877642295\nNo hay m&#225;s resultados</Body></Message></Response>'  # noqa
