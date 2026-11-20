package com.mediconnect.soapdossier.endpoint;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

import javax.xml.datatype.DatatypeFactory;
import javax.xml.datatype.XMLGregorianCalendar;

import org.springframework.ws.server.endpoint.annotation.Endpoint;
import org.springframework.ws.server.endpoint.annotation.PayloadRoot;
import org.springframework.ws.server.endpoint.annotation.RequestPayload;
import org.springframework.ws.server.endpoint.annotation.ResponsePayload;

import tn.mediconnect.soap.dossier.*;

@Endpoint
public class DossierEndpoint {

    private static final String NAMESPACE = "http://mediconnect.tn/soap/dossier";

    // ---- Données simulées (en mémoire) ----
    // Patients dont les droits CNAM sont ouverts
    private static final List<String> PATIENTS_ASSURES = List.of("12345678", "11223344");

    // Historique des actes par patient
    private final Map<String, List<ActeMedical>> historique = new ConcurrentHashMap<>();
    private final AtomicInteger compteurFeuilles = new AtomicInteger(1000);

    public DossierEndpoint() {
        // Quelques actes de départ pour le patient 12345678
        ajouterActe("12345678", "FS-0001", "2026-09-10", "C", "Consultation généraliste", "30.00", 80);
        ajouterActe("12345678", "FS-0002", "2026-10-02", "K50", "Acte de chirurgie courante", "200.00", 50);
    }

    // ---- Opération 1 : verifierDroitsCNAM ----
    @PayloadRoot(namespace = NAMESPACE, localPart = "VerifierDroitsCNAMRequest")
    @ResponsePayload
    public VerifierDroitsCNAMResponse verifierDroits(@RequestPayload VerifierDroitsCNAMRequest request) {
        VerifierDroitsCNAMResponse response = new VerifierDroitsCNAMResponse();

        if (PATIENTS_ASSURES.contains(request.getPatientId())) {
            response.setDroitsOuverts(true);
            response.setTauxRemboursement(calculerTaux(request.getCodeActe()));
            response.setMessage("Droits ouverts");
        } else {
            response.setDroitsOuverts(false);
            response.setTauxRemboursement(0);
            response.setMessage("Patient non assuré ou droits expirés");
        }
        return response;
    }

    // ---- Opération 2 : emettreFeuilleDeSoins ----
    @PayloadRoot(namespace = NAMESPACE, localPart = "EmettreFeuilleDeSoinsRequest")
    @ResponsePayload
    public EmettreFeuilleDeSoinsResponse emettreFeuille(@RequestPayload EmettreFeuilleDeSoinsRequest request) {
        EmettreFeuilleDeSoinsResponse response = new EmettreFeuilleDeSoinsResponse();
        String numero = "FS-" + compteurFeuilles.incrementAndGet();
        response.setNumeroFeuille(numero);
        response.setDateEmission(aujourdhui());

        if (!PATIENTS_ASSURES.contains(request.getPatientId())) {
            response.setStatut(StatutFeuille.REJETEE);
            response.setMontantRembourse(BigDecimal.ZERO);
            response.setResteACharge(request.getMontant());
            return response;
        }

        int taux = calculerTaux(request.getCodeActe());
        BigDecimal rembourse = request.getMontant()
                .multiply(BigDecimal.valueOf(taux))
                .divide(BigDecimal.valueOf(100), 2, RoundingMode.HALF_UP);

        response.setStatut(StatutFeuille.EMISE);
        response.setMontantRembourse(rembourse);
        response.setResteACharge(request.getMontant().subtract(rembourse));

        // On enregistre l'acte dans l'historique du patient
        ActeMedical acte = new ActeMedical();
        acte.setNumeroFeuille(numero);
        acte.setDateActe(request.getDateActe());
        acte.setCodeActe(request.getCodeActe());
        acte.setLibelle("Acte " + request.getCodeActe());
        acte.setMontant(request.getMontant());
        acte.setTauxRemboursement(taux);
        historique.computeIfAbsent(request.getPatientId(), k -> new ArrayList<>()).add(acte);

        return response;
    }

    // ---- Opération 3 : consulterHistorique ----
    @PayloadRoot(namespace = NAMESPACE, localPart = "ConsulterHistoriqueRequest")
    @ResponsePayload
    public ConsulterHistoriqueResponse consulterHistorique(@RequestPayload ConsulterHistoriqueRequest request) {
        ConsulterHistoriqueResponse response = new ConsulterHistoriqueResponse();
        response.setPatientId(request.getPatientId());
        response.getActes().addAll(historique.getOrDefault(request.getPatientId(), List.of()));
        return response;
    }

    // ---- Méthodes utilitaires ----

    // Règle simulée : actes chirurgicaux (lettre-clé K) à 80 %, le reste à 50 %
    private int calculerTaux(String codeActe) {
        return codeActe.startsWith("K") ? 80 : 50;
    }

    private void ajouterActe(String patientId, String numero, String date, String code,
                             String libelle, String montant, int taux) {
        ActeMedical acte = new ActeMedical();
        acte.setNumeroFeuille(numero);
        acte.setDateActe(convertirDate(date));
        acte.setCodeActe(code);
        acte.setLibelle(libelle);
        acte.setMontant(new BigDecimal(montant));
        acte.setTauxRemboursement(taux);
        historique.computeIfAbsent(patientId, k -> new ArrayList<>()).add(acte);
    }

    private XMLGregorianCalendar aujourdhui() {
        return convertirDate(LocalDate.now().toString());
    }

    private XMLGregorianCalendar convertirDate(String isoDate) {
        try {
            return DatatypeFactory.newInstance().newXMLGregorianCalendar(isoDate);
        } catch (Exception e) {
            throw new IllegalStateException("Date invalide : " + isoDate, e);
        }
    }
}