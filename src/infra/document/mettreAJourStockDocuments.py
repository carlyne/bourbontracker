from __future__ import annotations

import logging

from src.infra.models import Document
from src.infra._baseStockage import _BaseStockage

logger = logging.getLogger(__name__)

class MettreAJourStockDocuments(_BaseStockage):
    
    def __init__(self):
        super().__init__(
            nom_dossier_zip="dossier_legislatifs.zip",
            nom_dossier="document",
            url= "http://data.assemblee-nationale.fr/static/openData/repository/17/loi/dossiers_legislatifs/Dossiers_Legislatifs.json.zip"
        )

        self._mettre_a_jour_stock()
    
    def _mettre_a_jour_stock(self) -> int:
        self._mettre_a_jour()
        with self.SessionLocal() as session:
            total_documents = self._enregistrer_depuis_dossier(session, Document, batch_size=1000)
            session.commit()
        return total_documents
    
    

