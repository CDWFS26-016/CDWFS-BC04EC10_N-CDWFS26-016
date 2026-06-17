"""Tests de l'interaction utilisateur via le formulaire HTML (route /).

Couverture du chemin nominal ET des chemins d'erreur utilisateur.
app.py n'est PAS modifie : on constate le comportement reel. Les defauts
sont soit verrouilles par une assertion sur le code d'erreur actuel (avec
un commentaire), soit decrits par un test xfail exprimant l'attendu.
"""
import math

import pytest


def test_get_affiche_le_formulaire_vide(client):
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "<form" in body
    assert "Distance" in body
    assert "Votre resultat est None" in body


def test_post_calcule_la_distance_pythagore(client):
    # Sujet : A(2,5), B(1,6) -> distance = sqrt((1-2)^2 + (6-5)^2) = sqrt(2).
    resp = client.post("/", data={"apoint": "2,5", "bpoint": "1,6"})
    assert resp.status_code == 200
    assert str(math.sqrt(2)) in resp.get_data(as_text=True)


def test_post_distance_entiers_simples(client):
    # (0,0) -> (3,4) : triangle 3-4-5, distance = 5.
    resp = client.post("/", data={"apoint": "0,0", "bpoint": "3,4"})
    assert resp.status_code == 200
    assert "5.0" in resp.get_data(as_text=True)


def test_post_alimente_le_stockage_en_memoire(client):
    client.post("/", data={"apoint": "2,5", "bpoint": "1,6"})
    distances = client.get("/api/distances").get_json()
    assert len(distances) == 1
    assert distances[0]["result_distance"] == pytest.approx(math.sqrt(2))


def test_post_coordonnees_non_numeriques_provoque_500(client):
    """DEFAUT : aucune validation -> int('abc') -> ValueError -> 500
    (devrait etre 400)."""
    resp = client.post("/", data={"apoint": "abc", "bpoint": "1,6"})
    assert resp.status_code == 500


def test_post_coordonnees_decimales_provoque_500(client):
    """DEFAUT : int('2.5') echoue -> 500 ; les decimales sont pourtant
    indispensables (extension Haversine annoncee)."""
    resp = client.post("/", data={"apoint": "2.5,5", "bpoint": "1,6"})
    assert resp.status_code == 500


def test_post_champ_manquant_provoque_400(client):
    """request.form['bpoint'] sur champ absent -> BadRequestKeyError -> 400."""
    resp = client.post("/", data={"apoint": "2,5"})
    assert resp.status_code == 400


def test_post_coordonnees_surnumeraires_silencieusement_ignorees(client):
    """DEFAUT : split(',')[0:2] tronque sans avertir. '2,5,9' accepte (2,5)."""
    resp = client.post("/", data={"apoint": "2,5,9", "bpoint": "1,6"})
    assert resp.status_code == 200


@pytest.mark.xfail(reason="Aucune validation : 500 au lieu de 400", strict=True)
def test_entree_invalide_devrait_renvoyer_400(client):
    resp = client.post("/", data={"apoint": "abc", "bpoint": "1,6"})
    assert resp.status_code == 400


@pytest.mark.xfail(reason="int() tronque : decimales rejetees", strict=True)
def test_devrait_accepter_les_decimales(client):
    resp = client.post("/", data={"apoint": "2.5,5.5", "bpoint": "1.0,6.0"})
    assert resp.status_code == 200
