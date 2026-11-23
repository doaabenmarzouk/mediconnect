import datetime as dt

from models import (Medecin, Medicament, Ordonnance, Patient, RendezVous,
                    StatutRendezVous)

# Mêmes identifiants patients que dans le SOAP et le gRPC
PATIENTS = {
    "12345678": Patient(
        id="12345678", nom="Ben Ali", prenom="Mohamed",
        date_naissance=dt.date(1985, 4, 12), telephone="+216 22 111 222",
        email="mohamed.benali@example.tn", adresse="12 rue de la Liberté, Bizerte",
        contact_urgence="Amel Ben Ali, +216 98 333 444",
    ),
    "11223344": Patient(
        id="11223344", nom="Trabelsi", prenom="Salma",
        date_naissance=dt.date(1992, 9, 3), telephone="+216 55 666 777",
        email="salma.trabelsi@example.tn", adresse="5 avenue Habib Bourguiba, Tunis",
        contact_urgence="Karim Trabelsi, +216 97 888 999",
    ),
}

MEDECINS = {
    "MED001": Medecin(id="MED001", nom="Dr Leila Mansour", specialite="Médecine générale"),
    "MED002": Medecin(id="MED002", nom="Dr Sami Gharbi", specialite="Cardiologie"),
    "MED003": Medecin(id="MED003", nom="Dr Karim Jebali", specialite="Urgences"),
}

# Médecin de garde, attribué automatiquement aux urgences
MEDECIN_GARDE = "MED003"

# Heures de consultation proposées chaque jour
HEURES = ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
          "14:00", "14:30", "15:00", "15:30", "16:00"]

RENDEZ_VOUS: dict[int, RendezVous] = {}
_compteur = 0


def prochain_id() -> int:
    global _compteur
    _compteur += 1
    return _compteur


# Un rendez-vous de départ pour la démonstration
_id = prochain_id()
RENDEZ_VOUS[_id] = RendezVous(
    id=_id, patient_id="12345678", medecin_id="MED001",
    date=dt.date(2026, 12, 1), heure="09:00",
    motif="Consultation de suivi", statut=StatutRendezVous.PLANIFIE,
)

ORDONNANCES: dict[str, list[Ordonnance]] = {
    "12345678": [
        Ordonnance(
            id=1, patient_id="12345678", medecin_id="MED001", date=dt.date(2026, 9, 10),
            medicaments=[
                Medicament(nom="Paracétamol", dosage="1 g", duree="5 jours"),
                Medicament(nom="Amoxicilline", dosage="500 mg, 3 fois par jour", duree="7 jours"),
            ],
        ),
        Ordonnance(
            id=2, patient_id="12345678", medecin_id="MED002", date=dt.date(2026, 10, 2),
            medicaments=[Medicament(nom="Bisoprolol", dosage="5 mg, 1 fois par jour", duree="30 jours")],
        ),
    ],
    "11223344": [
        Ordonnance(
            id=3, patient_id="11223344", medecin_id="MED001", date=dt.date(2026, 11, 5),
            medicaments=[Medicament(nom="Ibuprofène", dosage="400 mg", duree="3 jours")],
        ),
    ],
}