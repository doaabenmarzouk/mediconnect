package com.mediconnect.soapdossier.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.io.ClassPathResource;
import org.springframework.ws.wsdl.wsdl11.DefaultWsdl11Definition;
import org.springframework.xml.xsd.SimpleXsdSchema;
import org.springframework.xml.xsd.XsdSchema;

@Configuration
public class WebServiceConfig {

    // Charge le contrat de données (XSD)
    @Bean
    public XsdSchema dossierSchema() {
        return new SimpleXsdSchema(new ClassPathResource("dossier.xsd"));
    }

    // Génère le WSDL à partir du XSD.
    // Le nom du bean ("dossier") donne l'URL : /ws/dossier.wsdl
    @Bean(name = "dossier")
    public DefaultWsdl11Definition dossierWsdl(XsdSchema dossierSchema) {
        DefaultWsdl11Definition wsdl = new DefaultWsdl11Definition();
        wsdl.setPortTypeName("DossierPort");
        wsdl.setLocationUri("/ws");
        wsdl.setTargetNamespace("http://mediconnect.tn/soap/dossier");
        wsdl.setSchema(dossierSchema);
        return wsdl;
    }
}