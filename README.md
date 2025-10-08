# bourbontracker-api

## Démarrage local

1. Copiez `.env.example` vers `.env` puis adaptez les valeurs si besoin.
2. Démarrez la base Postgres locale (via Docker Compose si nécessaire).
3. Lancez l'API en vous assurant que la variable d'environnement `APP_ENVIRONMENT` vaut `local` (c'est la valeur par défaut).

```bash
# Exemple : lancement avec uvicorn en mode développement
APP_ENVIRONMENT=local uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## Déploiement sur Render

Lors du déploiement sur Render, définissez `APP_ENVIRONMENT` à `render` dans l'onglet **Environment** de votre service Web ainsi que les variables sensibles (`DATABASE_URL`, `RENDER_EXTERNAL_URL`, etc.). Render injecte ensuite ces variables avant de lancer la commande `Dockerfile`.

```bash
# Commande équivalente exécutée par Render (valeurs d'environnement fournies par la plateforme)
APP_ENVIRONMENT=render uvicorn src.main:app --host 0.0.0.0 --port 8000
```

Grâce à cette variable, le module `src.settings` sélectionne automatiquement la configuration (CORS, base de données…) adaptée à l'environnement courant.
