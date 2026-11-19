# MediConnect

**Smart Healthcare platform for a connected hospital and home health monitoring.**

MediConnect is an interoperable platform that connects heterogeneous healthcare
services, each using a different communication protocol, and exposes them
through a single web client.

Academic project for the *Service Oriented Computing* course, 3rd year
Computer Engineering (ING GINF), 2026-2027.

## Overview

A patient at home wears a connected sensor (simulated by a script). When a vital
sign becomes critical, the platform detects the alert in real time, checks the
patient's record and insurance coverage, books an emergency slot, and displays
an intervention sheet to the doctor on the dashboard.

## Services

| Service | Protocol | Responsibility |
|---|---|---|
| Patient Record & Insurance | SOAP | Insurance rights check, certified care sheets, medical history |
| Patient Portal | REST | Appointments (CRUD), prescriptions, patient profile |
| Medical Dashboard | GraphQL | Custom patient queries, dynamic filtering, consolidated view |
| Telemetry & Emergency Alerts | gRPC | Real-time sensor streaming, critical threshold detection |
| Orchestrator | Internal | Business workflow chaining the four services |
| API Gateway | HTTP | Single entry point, routing, authentication |
| Web Client | React | Patient, doctor and administrator interfaces |

## Alert workflow

1. Critical vital sign received in real time (gRPC)
2. Patient record and insurance coverage verified (SOAP)
3. Emergency slot booked or ambulance dispatched (REST)
4. Enriched intervention sheet displayed on the doctor's dashboard (GraphQL)

## Tech stack

Java / Spring Boot, Python / FastAPI, GraphQL, gRPC, React, Docker, Docker Compose

## Documentation

WSDL (SOAP), OpenAPI (REST), SDL (GraphQL), .proto (gRPC) are available in the `docs/` folder.

## Getting started

```bash
docker compose up --build
```

## Author

Doaa Ben Marzouk, ENICarthage
