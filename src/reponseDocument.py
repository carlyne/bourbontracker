from typing import Optional
from pydantic import BaseModel

class ReponseDocument(BaseModel):
    id: Optional[str] = None
    legislature: Optional[str] = None
    typeTexte: Optional[str] = None
    titrePrincipal: Optional[str] = None
    statutAdoption: Optional[str] = None
    noticeFormule: Optional[str] = None
    denominationStructurelle: Optional[str] = None
    provenance: Optional[str] = None
    libelleClasse: Optional[str] = None
    libelleEspeces: Optional[str] = None
    typeClassification: Optional[str] = None
    sous_typeClassification: Optional[str] = None
    dateCreation: Optional[str] = None
    dateDepot: Optional[str] = None
    libelleDepot: Optional[str] = None
    datePublication: Optional[str] = None
    dossierId: Optional[str] = None
    dossierUrl: Optional[str] = None