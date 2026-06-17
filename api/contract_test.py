"""Validation de contrat de l'API pilotee par OpenAPI (schemathesis).

schemathesis genere automatiquement des cas a partir de openapi.yaml et verifie
que l'application les honore (codes de statut, schemas de reponse, etc.).

Ce fichier vit volontairement HORS de `tests/` : il n'est pas execute par la
suite unitaire (`pytest`) car il met en evidence les non-conformites REST de
l'API (et echouerait donc tant que l'app n'est pas corrigee). Il est lance
explicitement (voir api/README.md).
"""
import os
import sys

import pytest

schemathesis = pytest.importorskip("schemathesis")

PROJECT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "my_distance")
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "openapi.yaml")
sys.path.insert(0, PROJECT_DIR)

from app import app as wsgi_app  # noqa: E402

# Charge le contrat depuis le fichier et le lie a l'application WSGI Flask.
schema = schemathesis.from_path(SCHEMA_PATH, app=wsgi_app)


@schema.parametrize()
def test_api_conforme_au_contrat(case):
    case.call_and_validate()
