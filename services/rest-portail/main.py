import datetime as dt
from typing import List, Optional

from fastapi import APIRouter, FastAPI, HTTPException, Query, Response

import donnees
from models import (Creneau, Medecin, NiveauUrgence, Ordonnance, Patient,
                    PatientMiseAJour, RendezVous, RendezVousCreation,
                    RendezVousModification, StatutRendezVous, UrgenceReponse,
                    UrgenceRequest)

app = FastAPI(
    title="MediConnect - Portail Patient",
    description="Service REST : rendez-vous, urgences, ordonnances et profil patient.",
    version="1.0.0",
)

router = APIRouter(prefix="/api/v1")


# ---------- Fonctions utilitaires ----------

def creneau_pris(medecin_id: str, jour: dt.date, heure: str,
                 ignorer_id: Optional[int] = None) -> bool:
    """Vrai si un rendez-vous PLANIFIE occupe déjà ce créneau."""
    return any(
        r.medecin_id == medecin_id and r.date == jour and r.heure == heure
        and r.statut == StatutRendezVous.PLANIFIE and r.id != ignorer_id
        for r in donnees.RENDEZ_VOUS.values()
    )


# ---------- Technique ----------

@router.get("/sante", tags=["Technique"])
def sante():
    """Vérifie que le service répond."""
    return {"service": "rest-portail", "statut": "ok"}


# ---------- Médecins et créneaux ----------

@router.get("/medecins", response_model=List[Medecin], tags=["Médecins"])
def lister_medecins():
    """Liste des médecins."""
    return list(donnees.MEDECINS.values())


@router.get("/creneaux", response_model=List[Creneau], tags=["Créneaux"],
            responses={404: {"description": "Médecin introuvable"}})
def lister_creneaux(medecin_id: str, jour: dt.date = Query(alias="date")):
    """Créneaux encore libres pour un médecin à une date donnée."""
    if medecin_id not in donnees.MEDECINS:
        raise HTTPException(status_code=404, detail="Médecin introuvable")
    return [Creneau(medecin_id=medecin_id, date=jour, heure=h)
            for h in donnees.HEURES if not creneau_pris(medecin_id, jour, h)]


# ---------- Rendez-vous (CRUD) ----------

@router.post("/rendez-vous", response_model=RendezVous, status_code=201,
             tags=["Rendez-vous"],
             responses={404: {"description": "Patient ou médecin introuvable"},
                        409: {"description": "Créneau déjà réservé"}})
def creer_rendez_vous(demande: RendezVousCreation):
    """Prend un rendez-vous sur un créneau libre."""
    if demande.patient_id not in donnees.PATIENTS:
        raise HTTPException(status_code=404, detail="Patient introuvable")
    if demande.medecin_id not in donnees.MEDECINS:
        raise HTTPException(status_code=404, detail="Médecin introuvable")
    if demande.heure not in donnees.HEURES:
        raise HTTPException(status_code=422, detail="Heure hors des horaires de consultation")
    if creneau_pris(demande.medecin_id, demande.date, demande.heure):
        raise HTTPException(status_code=409, detail="Créneau déjà réservé")

    rdv = RendezVous(id=donnees.prochain_id(), statut=StatutRendezVous.PLANIFIE,
                     **demande.model_dump())
    donnees.RENDEZ_VOUS[rdv.id] = rdv
    return rdv


@router.get("/rendez-vous", response_model=List[RendezVous], tags=["Rendez-vous"])
def lister_rendez_vous(patient_id: Optional[str] = None,
                       statut: Optional[StatutRendezVous] = None):
    """Liste les rendez-vous, avec filtres facultatifs par patient et par statut."""
    resultat = list(donnees.RENDEZ_VOUS.values())
    if patient_id:
        resultat = [r for r in resultat if r.patient_id == patient_id]
    if statut:
        resultat = [r for r in resultat if r.statut == statut]
    return resultat


@router.get("/rendez-vous/{rdv_id}", response_model=RendezVous, tags=["Rendez-vous"],
            responses={404: {"description": "Rendez-vous introuvable"}})
def lire_rendez_vous(rdv_id: int):
    """Détail d'un rendez-vous."""
    rdv = donnees.RENDEZ_VOUS.get(rdv_id)
    if rdv is None:
        raise HTTPException(status_code=404, detail="Rendez-vous introuvable")
    return rdv


@router.put("/rendez-vous/{rdv_id}", response_model=RendezVous, tags=["Rendez-vous"],
            responses={404: {"description": "Rendez-vous introuvable"},
                       409: {"description": "Créneau pris ou rendez-vous non modifiable"}})
def modifier_rendez_vous(rdv_id: int, modification: RendezVousModification):
    """Modifie la date, l'heure ou le motif d'un rendez-vous planifié."""
    rdv = donnees.RENDEZ_VOUS.get(rdv_id)
    if rdv is None:
        raise HTTPException(status_code=404, detail="Rendez-vous introuvable")
    if rdv.statut != StatutRendezVous.PLANIFIE:
        raise HTTPException(status_code=409, detail="Seul un rendez-vous planifié peut être modifié")

    changements = modification.model_dump(exclude_none=True)
    nouveau = rdv.model_copy(update=changements)
    if nouveau.heure not in donnees.HEURES:
        raise HTTPException(status_code=422, detail="Heure hors des horaires de consultation")
    if creneau_pris(nouveau.medecin_id, nouveau.date, nouveau.heure, ignorer_id=rdv_id):
        raise HTTPException(status_code=409, detail="Créneau déjà réservé")

    donnees.RENDEZ_VOUS[rdv_id] = nouveau
    return nouveau


@router.delete("/rendez-vous/{rdv_id}", status_code=204, tags=["Rendez-vous"],
               responses={404: {"description": "Rendez-vous introuvable"}})
def annuler_rendez_vous(rdv_id: int):
    """Annule un rendez-vous (il est conservé avec le statut ANNULE)."""
    rdv = donnees.RENDEZ_VOUS.get(rdv_id)
    if rdv is None:
        raise HTTPException(status_code=404, detail="Rendez-vous introuvable")
    donnees.RENDEZ_VOUS[rdv_id] = rdv.model_copy(update={"statut": StatutRendezVous.ANNULE})
    return Response(status_code=204)


# ---------- Urgence (appelée par l'orchestrateur) ----------

@router.post("/rendez-vous/urgence", response_model=UrgenceReponse, status_code=201,
             tags=["Urgences"],
             responses={404: {"description": "Patient introuvable"}})
def reserver_urgence(demande: UrgenceRequest):
    """Réserve une prise en charge d'urgence : le médecin de garde est attribué
    automatiquement, sans passer par les créneaux classiques."""
    if demande.patient_id not in donnees.PATIENTS:
        raise HTTPException(status_code=404, detail="Patient introuvable")

    medecin = donnees.MEDECINS[donnees.MEDECIN_GARDE]
    maintenant = dt.datetime.now()
    rdv = RendezVous(
        id=donnees.prochain_id(),
        patient_id=demande.patient_id,
        medecin_id=medecin.id,
        date=maintenant.date(),
        heure=maintenant.strftime("%H:%M"),
        motif=demande.motif,
        statut=StatutRendezVous.URGENCE,
    )
    donnees.RENDEZ_VOUS[rdv.id] = rdv

    return UrgenceReponse(
        rendez_vous_id=rdv.id,
        patient_id=rdv.patient_id,
        medecin=medecin,
        statut=rdv.statut,
        niveau=demande.niveau,
        arrivee_estimee_minutes=10 if demande.niveau == NiveauUrgence.CRITIQUE else 30,
        date=rdv.date,
        heure=rdv.heure,
    )


# ---------- Profil patient ----------

@router.get("/patients/{patient_id}", response_model=Patient, tags=["Patients"],
            responses={404: {"description": "Patient introuvable"}})
def lire_patient(patient_id: str):
    """Profil d'un patient."""
    patient = donnees.PATIENTS.get(patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient introuvable")
    return patient


@router.put("/patients/{patient_id}", response_model=Patient, tags=["Patients"],
            responses={404: {"description": "Patient introuvable"}})
def mettre_a_jour_patient(patient_id: str, coordonnees: PatientMiseAJour):
    """Met à jour les coordonnées. L'identité (nom, prénom, date de naissance) n'est pas modifiable."""
    patient = donnees.PATIENTS.get(patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient introuvable")
    patient = patient.model_copy(update=coordonnees.model_dump())
    donnees.PATIENTS[patient_id] = patient
    return patient


# ---------- Ordonnances ----------

@router.get("/patients/{patient_id}/ordonnances", response_model=List[Ordonnance],
            tags=["Ordonnances"],
            responses={404: {"description": "Patient introuvable"}})
def lister_ordonnances(patient_id: str):
    """Historique des ordonnances d'un patient."""
    if patient_id not in donnees.PATIENTS:
        raise HTTPException(status_code=404, detail="Patient introuvable")
    return donnees.ORDONNANCES.get(patient_id, [])


app.include_router(router)