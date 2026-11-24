import datetime as dt
from enum import Enum
from typing import List, Optional

import strawberry

import donnees


# ---------- Énumérations ----------

@strawberry.enum
class Niveau(Enum):
    AVERTISSEMENT = "AVERTISSEMENT"
    CRITIQUE = "CRITIQUE"


@strawberry.enum
class Risque(Enum):
    FAIBLE = "FAIBLE"
    MOYEN = "MOYEN"
    ELEVE = "ELEVE"


@strawberry.enum
class Service(Enum):
    CARDIOLOGIE = "CARDIOLOGIE"
    URGENCES = "URGENCES"
    MEDECINE_GENERALE = "MEDECINE_GENERALE"


# ---------- Types ----------

@strawberry.type
class Constantes:
    frequence_cardiaque: int
    spo2: int
    temperature: float
    horodatage: str


@strawberry.type
class Alerte:
    id: strawberry.ID
    type: str
    niveau: Niveau
    message: str
    horodatage: str


@strawberry.type
class Traitement:
    nom: str
    dosage: str
    duree: str


@strawberry.type
class Patient:
    id: strawberry.ID
    nom: str
    prenom: str
    age: int
    service: Service
    pathologie: str
    risque: Risque

    # Résolveurs : ces champs ne sont calculés QUE si le client les demande
    @strawberry.field
    def constantes(self) -> Optional[Constantes]:
        d = donnees.CONSTANTES.get(self.id)
        return Constantes(**d) if d else None

    @strawberry.field
    def alertes(self) -> List[Alerte]:
        return [Alerte(id=a["id"], type=a["type"], niveau=Niveau[a["niveau"]],
                       message=a["message"], horodatage=a["horodatage"])
                for a in donnees.ALERTES.get(self.id, [])]

    @strawberry.field
    def traitements(self) -> List[Traitement]:
        return [Traitement(**t) for t in donnees.TRAITEMENTS.get(self.id, [])]


def construire_patient(patient_id: str) -> Optional[Patient]:
    d = donnees.PATIENTS.get(patient_id)
    if d is None:
        return None
    return Patient(id=patient_id, nom=d["nom"], prenom=d["prenom"], age=d["age"],
                   service=Service[d["service"]], pathologie=d["pathologie"],
                   risque=Risque[d["risque"]])


# ---------- Fiche d'intervention ----------

@strawberry.type
class FicheIntervention:
    id: strawberry.ID
    patient_id: strawberry.ID
    alerte_declenchante: str
    medecin: str
    rendez_vous_id: int
    arrivee_estimee_minutes: int
    droits_ouverts: bool
    taux_remboursement: int
    statut: str
    creee_le: str

    @strawberry.field
    def patient(self) -> Optional[Patient]:
        """Le dossier complet du patient, relié à la fiche."""
        return construire_patient(str(self.patient_id))


@strawberry.input
class FicheInput:
    patient_id: strawberry.ID
    alerte_declenchante: str
    medecin: str
    rendez_vous_id: int
    arrivee_estimee_minutes: int
    droits_ouverts: bool
    taux_remboursement: int


def construire_fiche(d: dict) -> FicheIntervention:
    return FicheIntervention(**d)


# ---------- Requêtes ----------

@strawberry.type
class Query:
    @strawberry.field
    def sante(self) -> str:
        return "graphql-dashboard ok"

    @strawberry.field
    def patient(self, id: strawberry.ID) -> Optional[Patient]:
        """Dossier consolidé d'un patient (null si inconnu)."""
        return construire_patient(str(id))

    @strawberry.field
    def patients(
        self,
        service: Optional[Service] = None,
        pathologie: Optional[str] = None,
        risque: Optional[Risque] = None,
    ) -> List[Patient]:
        """Liste des patients, avec filtres facultatifs et cumulables."""
        resultat = []
        for patient_id, d in donnees.PATIENTS.items():
            if service and d["service"] != service.value:
                continue
            if risque and d["risque"] != risque.value:
                continue
            if pathologie and pathologie.lower() not in d["pathologie"].lower():
                continue
            resultat.append(construire_patient(patient_id))
        return resultat

    @strawberry.field
    def fiches_intervention(self, patient_id: Optional[strawberry.ID] = None) -> List[FicheIntervention]:
        """Historique des fiches d'intervention, filtrable par patient."""
        fiches = donnees.FICHES
        if patient_id:
            fiches = [f for f in fiches if f["patient_id"] == patient_id]
        return [construire_fiche(f) for f in fiches]


# ---------- Mutations ----------

@strawberry.type
class Mutation:
    @strawberry.mutation
    def creer_fiche_intervention(self, input: FicheInput) -> FicheIntervention:
        """Crée la fiche d'intervention d'urgence (appelée par l'orchestrateur)."""
        if str(input.patient_id) not in donnees.PATIENTS:
            raise ValueError("Patient introuvable")
        fiche = {
            "id": f"FI-{len(donnees.FICHES) + 1:04d}",
            "patient_id": input.patient_id,
            "alerte_declenchante": input.alerte_declenchante,
            "medecin": input.medecin,
            "rendez_vous_id": input.rendez_vous_id,
            "arrivee_estimee_minutes": input.arrivee_estimee_minutes,
            "droits_ouverts": input.droits_ouverts,
            "taux_remboursement": input.taux_remboursement,
            "statut": "EN_COURS",
            "creee_le": dt.datetime.now().isoformat(timespec="seconds"),
        }
        donnees.FICHES.append(fiche)
        return construire_fiche(fiche)


schema = strawberry.Schema(query=Query, mutation=Mutation)