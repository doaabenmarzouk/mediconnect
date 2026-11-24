PATIENTS = {
    "12345678": {"nom": "Ben Ali", "prenom": "Mohamed", "age": 41,
                 "service": "CARDIOLOGIE", "pathologie": "Hypertension", "risque": "ELEVE"},
    "11223344": {"nom": "Trabelsi", "prenom": "Salma", "age": 34,
                 "service": "MEDECINE_GENERALE", "pathologie": "Migraine", "risque": "FAIBLE"},
    "55667788": {"nom": "Hamdi", "prenom": "Youssef", "age": 67,
                 "service": "URGENCES", "pathologie": "Insuffisance respiratoire", "risque": "ELEVE"},
}

# Dernières constantes vitales par patient
CONSTANTES = {
    "12345678": {"frequence_cardiaque": 158, "spo2": 88, "temperature": 36.9,
                 "horodatage": "2026-11-24T10:15:00"},
    "11223344": {"frequence_cardiaque": 72, "spo2": 98, "temperature": 36.6,
                 "horodatage": "2026-11-24T10:10:00"},
    "55667788": {"frequence_cardiaque": 95, "spo2": 86, "temperature": 37.8,
                 "horodatage": "2026-11-24T10:12:00"},
}

ALERTES = {
    "12345678": [
        {"id": "A1", "type": "TACHYCARDIE", "niveau": "CRITIQUE",
         "message": "Tachycardie sévère : 158 bpm", "horodatage": "2026-11-24T10:15:00"},
        {"id": "A2", "type": "HYPOXIE", "niveau": "CRITIQUE",
         "message": "Détresse respiratoire : SpO2 88 %", "horodatage": "2026-11-24T10:15:00"},
    ],
    "11223344": [],
    "55667788": [
        {"id": "A3", "type": "HYPOXIE", "niveau": "CRITIQUE",
         "message": "Détresse respiratoire : SpO2 86 %", "horodatage": "2026-11-24T10:12:00"},
    ],
}

TRAITEMENTS = {
    "12345678": [{"nom": "Bisoprolol", "dosage": "5 mg, 1 fois par jour", "duree": "30 jours"}],
    "11223344": [{"nom": "Ibuprofène", "dosage": "400 mg", "duree": "3 jours"}],
    "55667788": [{"nom": "Salbutamol", "dosage": "2 bouffées, 3 fois par jour", "duree": "15 jours"}],
}

# Fiches d'intervention créées par l'orchestrateur
FICHES = []