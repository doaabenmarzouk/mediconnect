import queue
import threading
import time
import uuid
from concurrent import futures

import grpc

import telemetrie_pb2 as pb
import telemetrie_pb2_grpc as pb_grpc
from detection import evaluer

PORT = 50051


def maintenant_ms():
    return int(time.time() * 1000)


class TelemetrieService(pb_grpc.TelemetrieServicer):

    def __init__(self):
        self.dernieres_mesures = {}   # patient_id -> dernière Mesure
        self.abonnes = []             # liste de (patient_id, queue)
        self.verrou = threading.Lock()

    # ----- utilitaires -----

    def _creer_alerte(self, mesure, type_alerte, niveau, message):
        return pb.Alerte(
            alerte_id=str(uuid.uuid4()),
            patient_id=mesure.patient_id,
            type=type_alerte,
            niveau=niveau,
            message=message,
            mesure=mesure,
            horodatage=maintenant_ms(),
        )

    def _publier(self, alerte):
        """Envoie l'alerte à tous les abonnés concernés (SuivreAlertes)."""
        with self.verrou:
            for patient_id, file in self.abonnes:
                if patient_id == "" or patient_id == alerte.patient_id:
                    file.put(alerte)

    # ----- 1. Bidirectionnel : le capteur envoie des mesures, on renvoie des alertes -----

    def Surveiller(self, request_iterator, context):
        for mesure in request_iterator:
            with self.verrou:
                self.dernieres_mesures[mesure.patient_id] = mesure

            for type_alerte, niveau, message in evaluer(mesure):
                alerte = self._creer_alerte(mesure, type_alerte, niveau, message)
                nom_niveau = pb.Niveau.Name(niveau)
                print(f"[ALERTE {nom_niveau}] patient {mesure.patient_id} : {message}")
                self._publier(alerte)
                yield alerte   # renvoyée immédiatement au capteur

    # ----- 2. Server streaming : abonnement aux alertes -----

    def SuivreAlertes(self, request, context):
        file = queue.Queue()
        abonne = (request.patient_id, file)
        with self.verrou:
            self.abonnes.append(abonne)
        print(f"[ABONNEMENT] ouvert (patient='{request.patient_id or 'tous'}')")
        try:
            while context.is_active():
                try:
                    yield file.get(timeout=1)
                except queue.Empty:
                    continue
        finally:
            with self.verrou:
                self.abonnes.remove(abonne)
            print("[ABONNEMENT] fermé")

    # ----- 3. Unary : dernière mesure connue -----

    def DerniereMesure(self, request, context):
        with self.verrou:
            mesure = self.dernieres_mesures.get(request.patient_id)
        if mesure is None:
            context.abort(grpc.StatusCode.NOT_FOUND, "Aucune mesure pour ce patient")
        return mesure


def main():
    serveur = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb_grpc.add_TelemetrieServicer_to_server(TelemetrieService(), serveur)
    serveur.add_insecure_port(f"[::]:{PORT}")
    serveur.start()
    print(f"Serveur gRPC démarré sur le port {PORT}")
    serveur.wait_for_termination()


if __name__ == "__main__":
    main()