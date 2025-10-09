# bourbontracker-api

## Démarrage local

1. Démarrer la base Postgres locale (via `docker compose up -d`).
2. Lancer l'API en s'assurant que la variable d'environnement `APP_ENVIRONMENT` vaut `local` (valeur par défaut).

```bash
APP_ENVIRONMENT=local uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## Déploiement sur Render

1. Configurez la variable d'environnement `APP_ENVIRONMENT=render` et fournissez `DATABASE_URL` dans le service Render.
2. Utilisez la commande de démarrage `uvicorn src.main:app --host 0.0.0.0 --port $PORT` afin que l'application écoute sur `0.0.0.0`
   et sur le port communiqué par Render ([documentation officielle](https://render.com/docs/web-services#port-binding)).
3. Optionnel : appliquez le fichier [`render.yaml`](render.yaml) comme blueprint Render pour versionner la configuration
   (construction `pip install -r requirements.txt` et démarrage `uvicorn` déjà paramétrés).
4. Pour un lancement manuel sans blueprint, vous pouvez également exécuter `python -m src` ; la commande utilise automatiquement
   le port exposé via la variable d'environnement `PORT`.
