import sys

import grpc

import telemetrie_pb2 as pb
import telemetrie_pb2_grpc as pb_grpc

patient_id = sys.argv[1] if len(sys.argv) > 1 else ""   # vide = toutes les alertes

with grpc.insecure_channel("localhost:50051") as canal:
    stub = pb_grpc.TelemetrieStub(canal)
    print(f"Abonné aux alertes (patient='{patient_id or 'tous'}'). Ctrl+C pour arrêter.")
    try:
        for alerte in stub.SuivreAlertes(pb.AbonnementRequest(patient_id=patient_id)):
            print(f"[ABONNÉ] {pb.Niveau.Name(alerte.niveau)} | patient {alerte.patient_id} | {alerte.message}")
    except KeyboardInterrupt:
        print("Abonnement arrêté")