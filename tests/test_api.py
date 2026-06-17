"""Tests de l'API JSON (routes /api, /api/distances, /api/distance).

app.py inchange ; on constate le comportement reel et on documente les ecarts
avec une API REST attendue.
"""
import math

import pytest


def test_api_racine_renvoie_objet_vide(client):
    resp = client.get("/api")
    assert resp.status_code == 200
    assert resp.get_json() == {}


def test_distances_vide_au_depart(client):
    resp = client.get("/api/distances")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_post_distance_calcule_correctement(client):
    resp = client.post("/api/distance", json={"start_point": "0,0", "end_point": "3,4"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["result_distance"] == pytest.approx(5.0)
    assert data["start_point"] == [0, 0]
    assert data["end_point"] == [3, 4]


def test_put_distance_est_accepte(client):
    """DEFAUT : PUT autorise sur un calcul sans effet de bord, identique a POST."""
    resp = client.put("/api/distance", json={"start_point": "2,5", "end_point": "1,6"})
    assert resp.status_code == 200
    assert resp.get_json()["result_distance"] == pytest.approx(math.sqrt(2))


def test_get_sur_distance_provoque_415(client):
    """DEFAUT : route GET autorisee mais lit request.json -> 415 systematique."""
    resp = client.get("/api/distance")
    assert resp.status_code == 415


def test_post_distance_cle_manquante_provoque_500(client):
    """DEFAUT : request.json['end_point'] absent -> KeyError -> 500 (attendu 400)."""
    resp = client.post("/api/distance", json={"start_point": "2,5"})
    assert resp.status_code == 500


def test_post_distance_non_numerique_provoque_500(client):
    resp = client.post("/api/distance", json={"start_point": "a,b", "end_point": "1,6"})
    assert resp.status_code == 500


def test_post_api_distance_ne_persiste_pas(client):
    """INCOHERENCE : POST /api/distance ne stocke rien alors que / alimente la liste."""
    client.post("/api/distance", json={"start_point": "0,0", "end_point": "3,4"})
    assert client.get("/api/distances").get_json() == []


def test_incoherence_inversion_start_end_entre_form_et_api(client):
    """INCOHERENCE : via le formulaire, apoint -> end_point et bpoint -> start_point
    (inversion) ; l'API respecte les cles fournies."""
    client.post("/", data={"apoint": "2,5", "bpoint": "1,6"})
    stocke = client.get("/api/distances").get_json()[0]
    assert stocke["end_point"] == [2, 5]
    assert stocke["start_point"] == [1, 6]


@pytest.mark.xfail(reason="GET declare mais inutilisable : devrait etre 405 ou 200", strict=True)
def test_get_distance_ne_devrait_pas_renvoyer_415(client):
    resp = client.get("/api/distance")
    assert resp.status_code != 415


@pytest.mark.xfail(reason="Erreur client mal geree : 500 au lieu de 400", strict=True)
def test_cle_manquante_devrait_renvoyer_400(client):
    resp = client.post("/api/distance", json={"start_point": "2,5"})
    assert resp.status_code == 400
