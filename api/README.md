# Validation de l'API

Deux outils sont fournis pour valider l'API contre son contrat `openapi.yaml`.

## 1. schemathesis (tests de contrat automatiques)

[schemathesis](https://schemathesis.readthedocs.io/) génère des requêtes à
partir de l'OpenAPI et vérifie les réponses.

```bash
pip install schemathesis

# En ligne de commande, contre une app lancée :
(cd ../my_distance && flask --app app run) &
schemathesis run ../openapi.yaml --base-url http://127.0.0.1:5000

# Ou via pytest (lie directement l'app WSGI, sans serveur) :
pytest api/contract_test.py
```

> Attendu : schemathesis remonte les non-conformités décrites dans `questions.md`
> (415 sur `GET /api/distance`, 500 au lieu de 400 sur entrée invalide, etc.).
> C'est l'objectif : l'outil prouve les écarts au contrat REST.

## 2. Collection HTTP (validation manuelle)

`requests.http` regroupe une requête par cas (nominal + erreurs). À ouvrir avec
l'extension **REST Client** (VS Code) ou le client HTTP d'IntelliJ, puis
exécuter chaque requête. Les codes attendus sont indiqués en commentaire.
