import sys

import grpc

import telemetrie_pb2 as pb
import telemetrie_pb2_grpc as pb_grpc

patient_id = sys.argv[1] if len(sys.argv) > 1 else "12345678"

with grpc.insecure_channel("localhost:50051") as canal:
    stub = pb_grpc.TelemetrieStub(canal)
    try:
        m = stub.DerniereMesure(pb.PatientRequest(patient_id=patient_id))
        print(f"Dernière mesure du patient {m.patient_id} : "
              f"FC={m.frequence_cardiaque} SpO2={m.spo2} T={m.temperature:.1f}")
    except grpc.RpcError as e:
        print(f"Erreur gRPC : {e.code().name} - {e.details()}")