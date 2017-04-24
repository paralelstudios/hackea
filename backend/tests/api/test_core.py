# -*- coding: utf-8 -*-
"""
    tests.api.test_core
    ~~~~~~~~~~~~~~~~
    Tests API core
"""

import pytest


@pytest.mark.functional
def test_ping(client):
    resp = client.get("/_ping")
    assert resp.status_code == 200
