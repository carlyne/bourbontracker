from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class Document:
    id: str
    typeTexte : Optional[str] = None
    dateCreation : Optional[str] = None
    legislature : Optional[str] = None
    dateDepot : Optional[str] = None
    datePublication : Optional[str] = None
    denominationStructurelle : Optional[str] = None
    provenance : Optional[str] = None
    titrePrincipal : Optional[str] = None
    libelleDepot : Optional[str] = None
    libelleClasse : Optional[str] = None
    libelleEspeces: Optional[str] = None
    typeClassification : Optional[str] = None
    statutAdoption : Optional[str] = None
    noticeFormule : Optional[str] = None
    dossierId : Optional[str] = None
    dossierUrl: Optional[str] = None

    def affichageDictionnaire(self):
        return asdict(self)