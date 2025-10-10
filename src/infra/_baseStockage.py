import shutil
import zipfile
import requests
import logging
import json
import tempfile
import os

from pathlib import Path
from typing import BinaryIO, Iterable, Iterator, Mapping, Type
from sqlalchemy.orm import DeclarativeMeta, Session as SASession
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from src.infra._baseConnexionBdd import _BaseConnexionBdd
from src.infra.infrastructureException import MiseAJourStockException

logger = logging.getLogger(__name__)

class _BaseStockage(_BaseConnexionBdd):
    def __init__(
            self, 
            nom_dossier_zip: str, 
            nom_dossier: str, 
            url: str
    ) -> None:
        
        super().__init__()

        self.nom_dossier: str = nom_dossier
        self.chemin_racine: Path = self._initialiser_chemin_racine()

        self.chemin_zip: Path = self.chemin_racine / nom_dossier_zip
        self.dossier_dezippé: Path = self.chemin_racine / nom_dossier

        self.url: str = url
    
    def vider_dossier_racine(self) -> None:
        base = Path(self.chemin_racine).resolve()
        logger.info("Réinitialisation de '%s' (suppression + recréation)", base)
        try:
            if base.exists() and base.is_dir() and base.name == "docs":
                try:
                    shutil.rmtree(base)
                except Exception:
                    logger.exception("Suppression de %s échouée", base)
                    raise
                base.mkdir(parents=True, exist_ok=True)
        except Exception:
            logger.exception("Réinitialisation de %s échouée", base)

    # --- Private functions

    def _initialiser_chemin_racine(self) -> Path:
        chemin_configuré = os.environ.get("STOCKAGE_RACINE", "docs")
        chemin = Path(chemin_configuré)

        if not chemin.is_absolute():
            chemin = Path.cwd() / chemin

        try:
            chemin.mkdir(parents=True, exist_ok=True)
            return chemin
        except PermissionError:
            chemin_temporaire = Path(tempfile.gettempdir()) / chemin.name
            chemin_temporaire.mkdir(parents=True, exist_ok=True)
            logger.warning(
                "Impossible de créer le dossier %s (PermissionError). Utilisation du dossier temporaire %s.",
                chemin,
                chemin_temporaire,
            )
            return chemin_temporaire


    def _mettre_a_jour(self) -> list[Path]:
        try:
            logger.debug("Mise à jour du dossier %s", self.dossier_dezippé)
            self._telecharger_dossier_zip()
            return self._dezipper_fichiers()
        except Exception as e:
            logger.error("Erreur lors de la mise à jour des données : %s", e, exc_info=True)
            raise MiseAJourStockException("Impossible de récupérer les données à jour du dossier %s", self.dossier_dezippé) from e

    def _enregistrer_depuis_dossier(
        self, 
        session: SASession, 
        model: Type[DeclarativeMeta],
        batch_size: int = 1000,
    ) -> int:
        """
        Lit tous les fichiers .json d'un dossier, extrait (uid:str, payload:dict) et met à jour ou créé en base.
        'model' est l'ORM cible (Document, Acteur, Organe, ...).
        Le traitement est fait en mode batch
        """
        compteur_total = 0
        batch = []

        for fichier in self._itérer_dans_le_dossier_dezippé():
            try:
                with fichier.open("r", encoding="utf-8") as contenu:
                    payload: dict = json.load(contenu)
            except (json.JSONDecodeError, OSError, ValueError):
                logger.exception("JSON illisible/invalide: %s", fichier)
                continue

            uid = self._extraire_uid(payload)

            if not uid:
                # FIXME Logger le nom du fichier, etc...
                continue

            batch.append({"uid": uid, "payload": payload.get(self.nom_dossier)})

            if len(batch) >= batch_size:
                try:
                    self._creer_ou_mettre_à_jour_en_base(session, batch, model)
                except SQLAlchemyError:
                    logger.exception("Erreur SQL lors de l'enregistrement du batch contenant le fichier %s", fichier)
                    raise
                batch.clear()

            compteur_total += 1

        if batch:
            try:
                self._creer_ou_mettre_à_jour_en_base(session, batch, model)
            except SQLAlchemyError:
                logger.exception("Erreur SQL lors de l'enregistrement du dernier batch")
                raise

        return compteur_total

    def _telecharger_dossier_zip(self):
        self.chemin_zip.parent.mkdir(parents=True, exist_ok=True)

        logger.debug("Téléchargement du dossier '.zip' vers : %s", self.chemin_zip)

        chemin_temporaire = self._telecharger_dans_un_chemin_temporaire(self.chemin_zip)
        chemin_temporaire.replace(self.chemin_zip)
    
    def _dezipper_fichiers(self) -> list[Path]:
        prefixe = "json/" + self.nom_dossier + "/"
        self.dossier_dezippé.mkdir(parents=True, exist_ok=True)

        fichiers_extraits: list[Path] = []
        logger.debug("Extraction des fichiers '.zip' '%s*' vers %s", prefixe, self.dossier_dezippé)

        with zipfile.ZipFile(self.chemin_zip, "r") as fichier_zip:
            for info in fichier_zip.infolist():
                nom_fichier = info.filename
                if not nom_fichier.startswith(prefixe):
                    continue

                if info.is_dir():
                    (self.dossier_dezippé / nom_fichier[len(prefixe):]).mkdir(parents=True, exist_ok=True)
                    continue

                fichier_extrait = (self.dossier_dezippé / nom_fichier[len(prefixe):]).resolve()
                fichier_extrait.parent.mkdir(parents=True, exist_ok=True)

                with fichier_zip.open(info, "r") as source, fichier_extrait.open("wb") as destination:
                    shutil.copyfileobj(source, destination)

                fichiers_extraits.append(fichier_extrait)
        
        return fichiers_extraits
    
    def _telecharger_dans_un_chemin_temporaire(self, destination: Path) -> Path:
        with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as tmp:
            chemin_temporaire = Path(tmp.name)
            logger.debug("Ecriture du dossier '.zip' %s dans un chemin temporaire : %s", self.nom_dossier, chemin_temporaire)
            self._executer_requete_telechargement_dossier_zip(tmp)
        return chemin_temporaire

    def _executer_requete_telechargement_dossier_zip(self, tmp: BinaryIO):
        with requests.get(self.url, stream=True, timeout=(5, 30)) as reponse:
            logger.debug("Requête de téléchargement du dossier '.zip' %s : %s %s", self.nom_dossier, reponse.request.method, reponse.url)
            reponse.raise_for_status()
            for chunk in reponse.iter_content(chunk_size=256 * 1024):
                if chunk:
                    tmp.write(chunk)
    
    def _itérer_dans_le_dossier_dezippé(self) -> Iterator[Path] :
        if not self.dossier_dezippé.exists():
            # FIXME faire des contrôles en amont ou lever une exception ici si le dossier n'existe pas
            logger.warning("Le dossier %s n'existe pas", self.dossier_dezippé)
            return
        
        # yield : permet de traiter les fichiers en flux continue (méthode utilisée en mode batch)
        yield from (fichier for fichier in self.dossier_dezippé.rglob("*.json") if fichier.is_file())

    def _creer_ou_mettre_à_jour_en_base(
        self, 
        session: SASession, 
        lignes: Iterable[Mapping[str, object]], 
        model: Type[DeclarativeMeta]
    ) -> None:
        lignes = list(lignes)
        if not lignes:
            return

        query = pg_insert(model).values(lignes)

        query = query.on_conflict_do_update(
            index_elements=[model.uid],
            set_={
                "payload": query.excluded.payload,
                "updated_at": func.now(),
            }
        )

        session.execute(query)

    def _extraire_uid(self, payload: dict) -> str | None:
        donnée = payload.get(self.nom_dossier) or {}
        uid_brut = donnée.get("uid")

        if isinstance(uid_brut, str):
            return uid_brut.strip() or None

        if isinstance(uid_brut, dict):
            for clé in ("#text", "text", "value"):
                valeur = uid_brut.get(clé)
                if isinstance(valeur, str) and valeur.strip():
                    return valeur.strip()
            
            logger.warning("Le fichier n'a pas d'uid")
            return None

        logger.warning("Le fichier n'a pas d'uid")
        return None