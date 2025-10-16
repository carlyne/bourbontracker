import json
import logging

from pydantic import ValidationError
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import func
from typing import Iterable

from src.infra.models import OrganeModel
from src.infra._baseStockage import _BaseStockage
from src.metier.organe.organe import Organe, parser_organe_depuis_payload

logger = logging.getLogger(__name__)

class MettreAJourStockOrganes(_BaseStockage):
    def __init__(self):
        super().__init__(
            nom_dossier_zip="acteurs.zip",
            nom_dossier="organe",
            url= (
                "http://data.assemblee-nationale.fr/static/openData/repository/17/amo/"
                "deputes_senateurs_ministres_legislature/AMO20_dep_sen_min_tous_mandats_et_organes.json.zip"
            )
        )

        self._mettre_a_jour_stock()
    
    def _mettre_a_jour_stock(self) -> int:
        self._mettre_a_jour()
        with self.SessionLocal() as session:
            try:
                total_organes = self._enregistrer_organes_depuis_dossier(session, batch_size=1000)
                session.commit()
            except Exception:
                session.rollback()
                logger.exception("Rollback de la transaction en raison d'une erreur lors de la mise à jour des organes")
                raise
        return total_organes
    
    def _enregistrer_organes_depuis_dossier(self, session, batch_size: int = 1000) -> int:
        compteur_total = 0
        batch: list[dict[str, object]] = []

        fichiers = self._itérer_dans_le_dossier_dezippé()
        if fichiers is None:
            logger.warning("Aucun fichier JSON trouvé pour les organes")
            return 0

        for fichier in fichiers:
            try:
                with fichier.open("r", encoding="utf-8") as contenu:
                    payload: dict = json.load(contenu)
            except (json.JSONDecodeError, OSError, ValueError):
                logger.exception("JSON illisible/invalide: %s", fichier)
                continue

            try:
                organe = parser_organe_depuis_payload(payload)
            except ValidationError as erreur:
                logger.warning("Organe invalide ignoré (%s): %s", fichier.name, erreur)
                continue

            batch.append(self._convertir_organe_en_ligne(organe))
            compteur_total += 1

            if len(batch) >= batch_size:
                self._creer_ou_mettre_a_jour(session, batch)
                batch.clear()

        if batch:
            self._creer_ou_mettre_a_jour(session, batch)

        return compteur_total

    def _convertir_organe_en_ligne(self, organe: Organe) -> dict[str, object]:
        vi_mode = organe.viMoDe
        return {
            "uid": organe.uid,
            "code_type": self._nettoyer_chaine(organe.codeType),
            "libelle": self._nettoyer_chaine(organe.libelle),
            "libelle_edition": self._nettoyer_chaine(organe.libelleEdition),
            "libelle_abrege": self._nettoyer_chaine(organe.libelleAbrege),
            "libelle_abrev": self._nettoyer_chaine(organe.libelleAbrev),
            "organe_parent": self._nettoyer_chaine(organe.organeParent),
            "preseance": self._nettoyer_chaine(organe.preseance),
            "organe_precedent_ref": self._nettoyer_chaine(organe.organePrecedentRef),
            "vimode_date_debut": vi_mode.dateDebut if vi_mode else None,
            "vimode_date_agrement": vi_mode.dateAgrement if vi_mode else None,
            "vimode_date_fin": vi_mode.dateFin if vi_mode else None,
        }

    def _creer_ou_mettre_a_jour(self, session, lignes: Iterable[dict[str, object]]) -> None:
        lignes = list(lignes)
        if not lignes:
            return

        query = pg_insert(OrganeModel).values(lignes)
        colonnes = {clé for clé in lignes[0] if clé != "uid"}
        set_clause = {colonne: query.excluded[colonne] for colonne in colonnes}
        set_clause["updated_at"] = func.now()

        session.execute(
            query.on_conflict_do_update(
                index_elements=[OrganeModel.uid],
                set_=set_clause,
            )
        )

    @staticmethod
    def _nettoyer_chaine(valeur: str | None) -> str | None:
        if valeur is None:
            return None
        valeur_nettoyee = valeur.strip()
        return valeur_nettoyee or None
