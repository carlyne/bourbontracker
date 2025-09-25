from enum import Enum

class TypeFiltrage(str, Enum):
    jour = "jour"
    semaine = "semaine"
    mois = "mois"