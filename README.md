# bourbontracker-api

## Démarrage local

1. Démarrer la base Postgres locale (via `docker compose up -d`).
2. Lancer l'API en s'assurant que la variable d'environnement `APP_ENVIRONMENT` vaut `local` (valeur par défaut).

```bash
APP_ENVIRONMENT=local uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```