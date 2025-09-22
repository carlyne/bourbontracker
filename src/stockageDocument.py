import shutil
import zipfile
import requests
import logging
import os
import json

from pathlib import Path
from src.telechargementException import TelechargementException, LectureException

class StockageDocument:
    def __init__(self):
        self.cheminRacine = os.path.abspath("docs")
        self.cheminZipTemporaire = os.path.join(self.cheminRacine, "dossier_legislatifs.zip")
        self.cheminDossierDocument = os.path.join(self.cheminRacine, "document")
        self.url = "http://data.assemblee-nationale.fr/static/openData/repository/17/loi/dossiers_legislatifs/Dossiers_Legislatifs.json.zip"
    
    def recupererDocumentStocké(self):
          dossier = Path(self.cheminDossierDocument)

          if not dossier.exists():
            logging.warning("Le dossier de documents legislatifs n'existe pas : %s", dossier)
            return None
          
          try:
            fichiers = dossier.rglob("*.json")
            fichierLePlusRecent = max(fichiers, default=None, key=lambda p: p.stat().st_mtime)

            if fichierLePlusRecent is None:
                logging.info("Aucun fichier trouvé dans %s", dossier)
                return None
            
            with fichierLePlusRecent.open("r", encoding="utf-8") as fichier:
                return json.load(fichier)
          except Exception as e:
            logging.error("Erreur lors de la lecture du document legislatif : %s", e, exc_info=True)
            raise LectureException("Impossible de lire le document legislatif stocké") from e
    
    def mettreAJourStockDocuments(self):
        try:
            dossierZip = os.path.basename(self.cheminZipTemporaire)
            self.telechargerDonnees(self.url, self.cheminZipTemporaire)
            self.dezipperDonneesVersDestination(dossierZip)
        except Exception as e:
            logging.error(f"Erreur lors du téléchargement du dossier zip correspondant aux documents legislatifs : {e}", exc_info=True)
            raise TelechargementException(f"Impossible de traiter le dossier zip correspondant aux documents legislatifs")

    def telechargerDonnees(self, url, cheminZipTemporaire):
        logging.info(f"Téléchargement du dossier zip {cheminZipTemporaire}")
        reponse = requests.get(url, stream=True)
        with open(cheminZipTemporaire, 'wb') as dossier:
                for chunk in reponse.iter_content(chunk_size=8192):
                        dossier.write(chunk)

    def dezipperDonneesVersDestination(self, dossierZip):
        with zipfile.ZipFile(self.cheminZipTemporaire, 'r') as dossier:
            logging.info(f"Extraction des fichiers du zip {dossierZip} dans {self.cheminDossierDocument}")
            for fichier in dossier.namelist():
                if fichier.startswith('json/'):
                    cheminDeDestination = os.path.join(self.cheminDossierDocument, fichier[len('json/'):])
                    os.makedirs(os.path.dirname(cheminDeDestination), exist_ok=True)
                    with dossier.open(fichier) as source, open(cheminDeDestination, 'wb') as destination:
                        shutil.copyfileobj(source,destination)