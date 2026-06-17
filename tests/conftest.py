"""Fixtures partagees pour la suite de tests de my_distance.

Le projet livre place app.py dans my_distance/ sans paquet installable :
on l'ajoute donc au sys.path pour pouvoir l'importer tel quel.
"""
import os
import sys

import pytest

PROJECT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "my_distance")
sys.path.insert(0, PROJECT_DIR)

import app as app_module  # noqa: E402

# app.py fait `Flask('my_distance')` : hors de son repertoire, Flask ne
# retrouve pas le dossier templates/. On fixe le chemin en absolu cote
# harnais de test, sans modifier app.py.
app_module.app.template_folder = os.path.join(PROJECT_DIR, "templates")


@pytest.fixture
def client():
    """Client de test Flask isole (le stockage en memoire est un global)."""
    app_module.app.testing = False
    app_module.distances.clear()
    return app_module.app.test_client()
