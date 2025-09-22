from fastapi import FastAPI

from src.reponseDocument import ReponseDocument
from src.metier.traitementDocument import TraitementDocument

traitementDocument = TraitementDocument()

app = FastAPI()

@app.get("/v1/documents", response_model=ReponseDocument)
def retournerDocument():
    return traitementDocument.recupererDocument()
