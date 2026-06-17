# Rapport technique — revue, tests et documentation de `my_distance`

## L'idée

On m'a transmis le projet de notre développeur principal : un petit service
Flask qui calcule la distance entre deux points d'un plan, par Pythagore. Mon
job ici n'est pas de réécrire son application, mais de la **passer au crible** :
revue de code, campagne de tests centrée sur l'utilisateur, documentation, et
mise en place de l'outillage qui mesure la dette et la couverture. J'ai donc
décidé de **ne pas toucher à `app.py`** : je constate, je teste, je documente,
et je propose des corrections — mais je laisse le code en l'état pour que la
revue reste honnête.

## Mes choix de base

- **pytest** pour toute la campagne de tests, avec **pytest-cov** pour la
  couverture. C'est le standard de l'écosystème, et le client de test Flask
  s'y intègre nativement.
- Comme je ne corrige pas le code, je sépare mes tests en deux familles : ceux
  qui **constatent le comportement réel** (y compris les bugs, verrouillés par
  une assertion sur le code d'erreur actuel) et ceux qui **expriment l'attendu**,
  marqués `xfail`. Résultat : la suite est verte, mais elle documente noir sur
  blanc tout ce qui cloche. Quand le code sera corrigé, les `xfail` passeront au
  vert — c'est mon backlog, exécutable.
- Une **branche de fonctionnalité par étape**, fusionnée en `--no-ff` dans
  `main` : tous les commits d'étape restent ainsi *présents sur `main`* comme
  l'exige le sujet, tout en gardant une trace du travail par branches. Un
  message de commit imposé par étape, et un **auteur anonymisé** (numéro de
  candidat).

## Étape par étape

**Revue de code.** J'ai outillé la mesure avant de juger : pylint me sort
**2,50/10**, radon un indice de maintenabilité de **59** et une complexité
faible, bandit ne trouve aucune faille de sécurité. Mais à la lecture, les
défauts s'accumulent : aucune validation des entrées (l'app renvoie un 500 dès
qu'on saisit autre chose que deux entiers), du code mort (`print` après
`return`), un dictionnaire de résultat construit deux fois, des noms qui se
contredisent (le premier point du formulaire est stocké comme `end_point`…), des
`lambda` inutiles et zéro docstring.

**Tests (commit `Tests fixed`).** J'ai écrit une suite centrée sur l'interaction
utilisateur : le chemin nominal (l'exemple A(2,5)/B(1,6) du sujet donne bien
√2), mais surtout tous les chemins d'erreur qu'un utilisateur peut déclencher
(texte, décimales, champ manquant, coordonnées en trop). Côté API, je couvre
`/api`, `/api/distances` et `/api/distance`, y compris le `GET` qui renvoie 415
et l'incohérence de stockage. On finit à **~100 % de lignes, 97 % de branches**.

**Documentation (commit `Documentation`).** Un `README.md` qui explique à quoi
sert l'app, comment l'installer (uv ou venv), la lancer et l'utiliser
(formulaire + API, avec un exemple `curl`). J'ai aussi rédigé ce rapport.

**OpenAPI (commit `OpenAPI`).** J'ai décrit l'API **telle qu'elle est** dans
`openapi.yaml` (OpenAPI 3.0, validé) — quirks compris, pour que la doc colle à
la réalité et serve de base aux tests de contrat.

**Validation d'API (commit `API`).** Une collection `requests.http` pour rejouer
chaque cas à la main, et un test de contrat **schemathesis** piloté par
l'OpenAPI. Je l'ai volontairement placé hors de `tests/` : son rôle est de
**révéler** les écarts au contrat, donc il échouerait tant que l'app n'est pas
corrigée — ce n'est pas un test de non-régression.

**Dette & sécurité (commit `SAST/DAST fixed`).** J'ai rassemblé la config
outillée — `bandit.yaml` (SAST), `sonar-project.properties` (analyse agrégée +
couverture), et la marche à suivre DAST avec OWASP ZAP — et j'ai détaillé toutes
les commandes utiles dans le `README.md`.

## Ce que j'améliorerais (si je passais en correctif)

- **Valider les entrées** (WTForms côté formulaire, Pydantic côté API) et
  renvoyer des **400** explicites au lieu des 500 actuels.
- Passer les coordonnées en **`float`** : sans ça, l'extension Haversine
  annoncée dans le contexte est impossible.
- **Nettoyer** : supprimer le code mort, dédupliquer le dictionnaire de
  résultat, renommer les variables, remettre les imports dans l'ordre, ajouter
  des docstrings et du typage.
- **Rendre l'API REST** : `POST /api/distances` → 201, retirer GET/PUT du
  calcul, statuts cohérents, versionnement `/v1`.
- **Sortir le stockage de la mémoire** (une base, même SQLite) pour que
  l'historique survive au redémarrage et tienne la montée en charge.
