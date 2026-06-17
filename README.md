# my_distance

Petit service web de **calcul de distance entre deux points** d'un plan 2D.
La distance est obtenue par le théorème de Pythagore :

```
distance(A, B)² = (Bx − Ax)² + (By − Ay)²
```

L'application expose une page HTML (saisie via formulaire) et une petite API JSON.
À terme, la formule sera étendue (Haversine) pour des distances à l'échelle planétaire.

## Prérequis

- Python ≥ 3.13 (le projet est verrouillé avec [uv](https://docs.astral.sh/uv/), voir `my_distance/uv.lock`)
- Flask ≥ 3.1

## Installation

Avec **uv** (recommandé, le lock est fourni) :

```bash
cd my_distance
uv sync          # installe les dépendances figées par uv.lock
```

Ou avec un venv classique :

```bash
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install flask
```

## Lancer l'application

```bash
cd my_distance
flask --app app run            # http://127.0.0.1:5000
# ou : python -c "from app import app; app.run(debug=True)"
```

## Utilisation

### Interface web (`/`)

Ouvrir `http://127.0.0.1:5000/`, saisir deux points au format `x,y` puis
soumettre. Le résultat (distance + points) s'affiche sous le formulaire.

### API JSON

| Méthode        | Route             | Rôle                                             |
|----------------|-------------------|--------------------------------------------------|
| `GET`          | `/api`            | Point d'entrée (renvoie `{}`)                    |
| `GET`          | `/api/distances`  | Historique des distances calculées via le formulaire |
| `POST` / `PUT` | `/api/distance`   | Calcule une distance à partir d'un corps JSON    |

Exemple de calcul via l'API :

```bash
curl -X POST http://127.0.0.1:5000/api/distance \
     -H "Content-Type: application/json" \
     -d '{"start_point": "0,0", "end_point": "3,4"}'
# -> {"start_point":[0,0],"end_point":[3,4],"result_distance":5.0,"requested_at":"..."}
```

> Le contrat complet de l'API est décrit dans [`openapi.yaml`](./openapi.yaml)
> (format OpenAPI 3.0).

## Structure du dépôt

```
.
├── my_distance/          # application livrée (non modifiée)
│   ├── app.py
│   ├── templates/index.html
│   └── uv.lock
├── tests/                # suite de tests (pytest)
├── openapi.yaml          # description OpenAPI de l'API
├── api/                  # outils de validation de l'API
├── pyproject.toml        # config pytest / couverture
├── questions.md          # réponses au questionnaire
└── rapport.md            # note d'analyse et de revue de code
```

## Tests

```bash
pip install pytest pytest-cov
python -m pytest                 # lance la suite
python -m pytest --cov           # avec la couverture
```

## Qualité, sécurité et couverture (SAST / DAST)

Outils utilisés pour mesurer la dette technique, la sécurité et la couverture.
Tous sont installables via `pip` (cf. `pyproject.toml`, groupe `dev`).

### Couverture de tests (coverage.py / pytest-cov)

```bash
pip install pytest pytest-cov
python -m pytest --cov --cov-branch --cov-report=term-missing
python -m pytest --cov --cov-report=xml      # produit coverage.xml (pour SonarQube)
```

### Dette technique & qualité

```bash
pip install radon pylint
radon mi my_distance/app.py        # indice de maintenabilité
radon cc -s my_distance/app.py     # complexité cyclomatique
pylint my_distance/app.py          # note /10 + code smells
```

### Analyse de sécurité statique — SAST (Bandit)

```bash
pip install bandit
bandit -c bandit.yaml -r my_distance            # lecture humaine
bandit -c bandit.yaml -r my_distance -f json -o bandit-report.json   # pour SonarQube
```

### Analyse agrégée (SonarQube)

La configuration est dans `sonar-project.properties`. Après avoir généré
`coverage.xml` et `bandit-report.json` :

```bash
sonar-scanner            # nécessite un serveur SonarQube accessible
```

### Analyse dynamique — DAST (OWASP ZAP)

Sur l'application lancée (`flask --app app run`) :

```bash
docker run -t ghcr.io/zaproxy/zaproxy zap-baseline.py \
    -t http://host.docker.internal:5000 -r zap-report.html
```
