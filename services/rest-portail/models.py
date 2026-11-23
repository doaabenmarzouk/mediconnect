import datetime as dt
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

HEURE_REGEX = r"^([01][0-9]|2[0-3]):[0-5][0-9]$"


# ---------- Énumérations ----------

class StatutRendezVous(str, Enum):
    PLANIFIE = "PLANIFIE"
    ANNULE = "ANNULE"
    URGENCE = "URGENCE"


class NiveauUrgence(str, Enum):
    AVERTISSEMENT = "AVERTISSEMENT"
    CRITIQUE = "CRITIQUE"


# ---------- Médecins, patients, créneaux ----------

class Medecin(BaseModel):
    id: str
    nom: str
    specialite: str


class Patient(BaseModel):
    id: str
    nom: str
    prenom: str
    date_naissance: dt.date
    telephone: str
    email: str
    adresse: str
    contact_urgence: str


class PatientMiseAJour(BaseModel):
    """Coordonnées modifiables. PUT remplace l'ensemble : tous les champs sont obligatoires."""
    telephone: str = Field(pattern=r"^\+?[0-9 ]{8,15}$", examples=["+216 22 111 222"])
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", examples=["nom@example.tn"])
    adresse: str = Field(min_length=5, max_length=200)
    contact_urgence: str = Field(min_length=3, max_length=150)


class Creneau(BaseModel):
    medecin_id: str
    date: dt.date
    heure: str


# ---------- Rendez-vous ----------

class RendezVousCreation(BaseModel):
    """Données envoyées par le client pour prendre un rendez-vous."""
    patient_id: str = Field(pattern=r"^[0-9]{8}$", examples=["12345678"])
    medecin_id: str = Field(examples=["MED001"])
    date: dt.date = Field(examples=["2026-12-01"])
    heure: str = Field(pattern=HEURE_REGEX, examples=["09:30"])
    motif: str = Field(min_length=3, max_length=200, examples=["Consultation de suivi"])


class RendezVousModification(BaseModel):
    """Champs modifiables d'un rendez-vous (tous facultatifs)."""
    date: Optional[dt.date] = None
    heure: Optional[str] = Field(default=None, pattern=HEURE_REGEX)
    motif: Optional[str] = Field(default=None, min_length=3, max_length=200)


class RendezVous(RendezVousCreation):
    """Rendez-vous renvoyé par le service : on ajoute l'id et le statut."""
    id: int
    statut: StatutRendezVous


# ---------- Ordonnances ----------

class Medicament(BaseModel):
    nom: str
    dosage: str
    duree: str


class Ordonnance(BaseModel):
    id: int
    patient_id: str
    medecin_id: str
    date: dt.date
    medicaments: List[Medicament]


# ---------- Urgence ----------

class UrgenceRequest(BaseModel):
    """Demande de réservation d'urgence (envoyée par l'orchestrateur)."""
    patient_id: str = Field(pattern=r"^[0-9]{8}$", examples=["12345678"])
    motif: str = Field(min_length=3, max_length=200, examples=["Tachycardie sévère détectée"])
    niveau: NiveauUrgence = NiveauUrgence.CRITIQUE


class UrgenceReponse(BaseModel):
    rendez_vous_id: int
    patient_id: str
    medecin: Medecin
    statut: StatutRendezVous
    niveau: NiveauUrgence
    arrivee_estimee_minutes: int
    date: dt.date
    heure: str