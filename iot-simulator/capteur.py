import random
import sys
import time

import grpc

import telemetrie_pb2 as pb
import telemetrie_pb2_grpc as pb_grpc

ADRESSE = "localhost:50051"


def maintenant_ms():
    return int(time.time() * 1000)


def mesure_normale(patient_id):
    return pb.Mesure(
        patient_id=patient_id,
        frequence_cardiaque=random.randint(65, 90),
        spo2=random.randint(96, 99),
        temperature=round(random.uniform(36.4, 37.2), 1),
        horodatage=maintenant_ms(),
    )


def mesure_critique(patient_id):
    return pb.Mesure(
        patient_id=patient_id,
        frequence_cardiaque=random.randint(145, 165),   # tachycardie sévère
        spo2=random.randint(82, 88),                    # détresse respiratoire
        temperature=round(random.uniform(36.4, 37.2), 1),
        horodatage=maintenant_ms(),
    )


def generer_mesures(patient_id, nb_mesures, crise_a):
    """Flux de mesures : une par seconde, avec une crise à partir de la mesure n° crise_a."""
    for i in range(1, nb_mesures + 1):
        if i >= crise_a:
            mesure = mesure_critique(patient_id)
            etat = "CRITIQUE"
        else:
            mesure = mesure_normale(patient_id)
            etat = "normale"
        print(f"[capteur] mesure {i:02d} ({etat}) : FC={mesure.frequence_cardiaque} "
              f"SpO2={mesure.spo2} T={mesure.temperature}")
        yield mesure
        time.sleep(1)


def main():
    patient_id = sys.argv[1] if len(sys.argv) > 1 else "12345678"
    nb_mesures = 12
    crise_a = 8

    with grpc.insecure_channel(ADRESSE) as canal:
        stub = pb_grpc.TelemetrieStub(canal)
        print(f"Capteur démarré pour le patient {patient_id}")

        # Appel bidirectionnel : on envoie le flux, on reçoit les alertes au fil de l'eau
        for alerte in stub.Surveiller(generer_mesures(patient_id, nb_mesures, crise_a)):
            niveau = pb.Niveau.Name(alerte.niveau)
            print(f"   >>> ALERTE {niveau} reçue : {alerte.message}")

    print("Fin de la session du capteur")


if __name__ == "__main__":
    main()