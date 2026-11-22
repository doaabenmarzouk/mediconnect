"""Détection des constantes vitales anormales (seuils simulés, non médicaux)."""
import telemetrie_pb2 as pb


def evaluer(mesure):
    """Retourne la liste des anomalies détectées : [(type, niveau, message), ...]"""
    anomalies = []

    # --- Fréquence cardiaque (bpm) ---
    fc = mesure.frequence_cardiaque
    if fc > 130:
        anomalies.append((pb.TACHYCARDIE, pb.CRITIQUE, f"Tachycardie sévère : {fc} bpm"))
    elif fc > 100:
        anomalies.append((pb.TACHYCARDIE, pb.AVERTISSEMENT, f"Tachycardie : {fc} bpm"))
    elif fc < 40:
        anomalies.append((pb.BRADYCARDIE, pb.CRITIQUE, f"Bradycardie sévère : {fc} bpm"))
    elif fc < 60:
        anomalies.append((pb.BRADYCARDIE, pb.AVERTISSEMENT, f"Bradycardie : {fc} bpm"))

    # --- Saturation en oxygène (%) ---
    spo2 = mesure.spo2
    if spo2 < 90:
        anomalies.append((pb.HYPOXIE, pb.CRITIQUE, f"Détresse respiratoire : SpO2 {spo2} %"))
    elif spo2 < 95:
        anomalies.append((pb.HYPOXIE, pb.AVERTISSEMENT, f"SpO2 basse : {spo2} %"))

    # --- Température (°C) ---
    t = mesure.temperature
    if t > 39:
        anomalies.append((pb.FIEVRE, pb.CRITIQUE, f"Fièvre élevée : {t:.1f} °C"))
    elif t > 37.5:
        anomalies.append((pb.FIEVRE, pb.AVERTISSEMENT, f"Fièvre : {t:.1f} °C"))
    elif t < 35:
        anomalies.append((pb.HYPOTHERMIE, pb.CRITIQUE, f"Hypothermie : {t:.1f} °C"))
    elif t < 36.1:
        anomalies.append((pb.HYPOTHERMIE, pb.AVERTISSEMENT, f"Température basse : {t:.1f} °C"))

    return anomalies