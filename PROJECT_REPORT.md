# MINI PROJECT REPORT
## MUTUAL TLS AUTHENTICATION FOR IOT DEVICES
**Course:** Cyber Security Lab (7CS4-22 / 7CIT4-22) — B.Tech VII Semester  
**Department:** Computer Science & Engineering (Internet of Things)  
**Institution:** Swami Keshvanand Institute of Technology, Management & Gramothan (SKIT), Jaipur  
**Affiliated to:** Rajasthan Technical University (RTU), Kota  
**Session:** 2026-27  
**Project Code:** CSL-I11  
**Guide:** Vikash Dhankar, Assistant Professor, Dept. of CSE  

---

## CANDIDATE'S DECLARATION
I, [Student Name], Roll No. [Roll No.], a student of B.Tech VII Semester, CSE (IoT), Class/Batch [CS-IOT-A-G1], hereby declare that the mini project titled **“Mutual TLS Authentication for IoT Devices”** (Project Code **CSL-I11**) submitted for the Cyber Security Lab (7CS4-22 / 7CIT4-22) is my own original work, carried out under the guidance of Vikash Dhankar, Assistant Professor, Department of CSE, SKIT Jaipur. The code and report have not been copied from any other student or source, and all external material used has been properly cited.

## ETHICAL DECLARATION
I declare that all attack, sniffing, scanning or testing activities performed in this project were carried out only on my own systems, virtual machines or an isolated lab environment, using test data. No unauthorised system, network, account or person was targeted. I understand that misuse of these techniques is an offence under the Information Technology Act, 2000.

---

## ABSTRACT
Internet of Things (IoT) ecosystems are increasingly deployed in mission-critical applications including smart energy grids, healthcare monitoring, and industrial automation. However, traditional transport layer security (TLS) relies exclusively on server-side authentication, leaving edge gateway endpoints vulnerable to unauthorized device spoofing, rogue node injection, and eavesdropping. This project designs and implements a robust Mutual Transport Layer Security (mTLS) authentication architecture (Project Code CSL-I11) paired with Public Key Infrastructure (PKI) X.509 certificates to achieve end-to-end zero-trust verification between IoT edge sensors and central gateway nodes.

Directly aligned with RTU Cyber Security Lab Experiment 8 (Secure Storage, Transmission & Digital Signature), the system enforces mutual cryptographic verification prior to data exchange. Each physical device holds a unique RSA-2048 keypair and an X.509 client certificate signed by a private Root Certificate Authority (CA). In addition to transport layer session encryption (TLS 1.3 / AES-256-GCM), application-layer sensor telemetry is digitally signed using RSA-SHA256, guaranteeing cryptographic non-repudiation and data integrity. Rigorous adversarial testing—encompassing anonymous connections, untrusted rogue CA certificates, expired certificates, and in-transit payload tampering—confirms a 100% defense rate against impersonation and man-in-the-middle attacks.

**Keywords:** Mutual TLS, X.509 Certificates, IoT Security, Digital Signature, RSA-SHA256, TLS 1.3, Zero-Trust Architecture.

---

## CHAPTER 1: INTRODUCTION

### 1.1 Problem Statement & Background
The exponential proliferation of Internet of Things (IoT) architectures across critical domains has introduced unprecedented cyber security vulnerabilities. Typical IoT networks comprise hundreds to thousands of geographically dispersed edge nodes that collect and transmit sensitive environmental, biometric, and operational data to central aggregation servers or gateways.

In standard commercial Transport Layer Security (TLS/HTTPS), authentication is asymmetrical: only the server proves its cryptographic identity to the connecting client. The client verifies the server's certificate against its local trust store, while the client itself remains anonymous at the transport layer. In web browsing, client identity is customarily deferred to application-layer credentials (passwords, cookies, or Bearer API tokens). In headless, unattended IoT deployments, hardcoding passwords or static API tokens presents severe architectural risks. Attackers extracting static keys from flash memory can orchestrate large-scale device spoofing, replay attacks, and unauthorized telemetry injection.

### 1.2 Project Objectives
The primary objective of Project CSL-I11 ("Mutual TLS Authentication for IoT Devices") is to eliminate asymmetric trust by establishing a bidirectional, cryptographically authenticated zero-trust communication channel:
1. **Private PKI Construction:** Establish a private Public Key Infrastructure (Root CA) that issues individual X.509 v3 certificates to IoT sensors and servers.
2. **Mutual Authentication Enforcement:** Enforce strict mutual TLS (`ssl.CERT_REQUIRED`), requiring the server to validate client certificates and the client to validate server certificates.
3. **Secure In-Transit Encryption:** Utilize state-of-the-art TLS 1.3 with AES-256-GCM symmetric cipher suites to render eavesdropping mathematically infeasible.
4. **Application-Layer Integrity:** Compute RSA-SHA256 digital signatures on all transmitted sensor payloads, linking raw telemetry to device identity.
5. **Adversarial Security Verification:** Simulate real-world cyber attacks (anonymous access, untrusted CA, expired credentials, payload tampering) to validate defensive controls.

### 1.3 Link to RTU Syllabus Experiment (Exp 8)
In compliance with RTU Kota Cyber Security Lab guidelines, this project is directly mapped to **Experiment 8: Secure Storage, Transmission & Digital Signature**:
- **Secure Storage:** Private keys (`ca.key`, `server.key`, `device01.key`) are stored with restricted operating system permissions (`0600`), isolated from unprivileged processes.
- **Secure Transmission:** All data exchanged over TCP port 8443 is enveloped inside a TLS 1.3 cryptographic tunnel utilizing Diffie-Hellman Ephemeral key exchange and AES-256 Galois/Counter Mode authenticated encryption.
- **Digital Signature:** Devices digitally sign telemetry payloads using private keys (RSA-SHA256). The gateway verifies these signatures using the device's public key extracted from the validated X.509 certificate.

---

## CHAPTER 2: BACKGROUND & CRYPTOGRAPHIC THEORY

### 2.1 Evolution of Transport Layer Security (TLS 1.2 vs. TLS 1.3)
TLS operates above the transport layer (TCP) and below application protocols (HTTP, MQTT, CoAP). TLS 1.3 (RFC 8446) fundamentally overhauls transport security by achieving a 1-RTT handshake, enforcing Perfect Forward Secrecy (PFS) via Ephemeral Diffie-Hellman (ECDHE), and mandating Authenticated Encryption with Associated Data (AEAD) algorithms such as AES-256-GCM.

### 2.2 Anatomy of Mutual TLS (mTLS) Handshake
1. **ClientHello:** The IoT device advertises supported cipher suites, TLS version (1.3), and Diffie-Hellman key share.
2. **ServerHello & Key Share:** The Gateway accepts TLS 1.3, provides its key share, and establishes master session secrets.
3. **Server Certificate & CertificateRequest:** The Gateway presents its X.509 certificate and issues a `CertificateRequest` frame demanding client authentication.
4. **Client Certificate:** The IoT node presents its X.509 certificate (`device01.crt`) signed by the trusted Root CA.
5. **CertificateVerify:** The IoT node generates a digital signature over the entire handshake transcript using its private key, proving possession of the private key matching the public certificate.
6. **Finished:** Both parties verify signatures, derive symmetric keys, and transition to encrypted Application Data.

---

## CHAPTER 3: TOOLS & IMPLEMENTATION ENVIRONMENT

| Parameter | Specification / Tool Version |
| :--- | :--- |
| **Host Operating System** | Microsoft Windows 11 (64-bit) / Linux Ubuntu 22.04 LTS |
| **Processor / Architecture** | Intel(R) Core(TM) i5 / i7 or AMD Ryzen x86_64 |
| **Memory (RAM)** | 8.00 GB DDR4 / DDR5 minimum |
| **Programming Runtime** | Python 3.11.9 (64-bit) Standard Distribution |
| **Cryptographic Library** | cryptography 50.0.2 (OpenSSL 3.x bindings) |
| **Packet Inspection Tool** | Wireshark Network Protocol Analyzer v4.x |
| **Development Interface** | PowerShell 7 / Visual Studio Code / Terminal |
| **Network Transport** | TCP/IP Socket Layer over IPv4 Loopback (127.0.0.1:8443) |

---

## CHAPTER 4: SOURCE CODE ARCHITECTURE

### Architecture Summary
1. `generate_certificates.py`: Generates the Root CA, Server Certificate (with SAN), and Client Device Certificates.
2. `crypto_utils.py`: Signs JSON payloads using RSA-SHA256 and verifies signatures using public keys extracted from X.509 certificates.
3. `server.py`: Multi-threaded mTLS Gateway Server configured with `ssl.CERT_REQUIRED`.
4. `iot_device.py`: Valid IoT edge sensor client establishing mTLS connection and transmitting digitally signed sensor data.
5. `rogue_device.py`: Attack simulator executing 4 negative test cases.
6. `run_security_tests.py`: Automated test runner executing positive and negative test cases.

---

## CHAPTER 5: RESULTS, TESTING & SECURITY ANALYSIS

### 5.1 Comprehensive Security Evaluation Matrix

| Test ID | Scenario Description | Input / Attack Vector | Expected Outcome | Observed Outcome | Status |
| :---: | :--- | :--- | :--- | :--- | :---: |
| **TC-01** | Legitimate Sensor 01 | Valid CA Cert + Valid Signature | Authorized (200 OK) | Authorized (200 OK) | **PASS** |
| **TC-02** | Legitimate Actuator 02 | Valid CA Cert + Valid Signature | Authorized (200 OK) | Authorized (200 OK) | **PASS** |
| **TC-03** | Anonymous Client | Missing Client Certificate | Handshake Rejected | Rejected (`CERT_REQUIRED`) | **PASS** |
| **TC-04** | Rogue Impersonator | Cert from Fake Untrusted CA | Handshake Terminated | Rejected (`CERT_VERIFY_FAILED`) | **PASS** |
| **TC-05** | Stale / Deprecated Device | Expired X.509 Certificate | Handshake Terminated | Rejected (`CERT_VERIFY_FAILED`) | **PASS** |
| **TC-06** | Data Tampering Attack | Valid Cert + Modified Payload | Payload Rejected (401) | Rejected (`401 Integrity Error`) | **PASS** |

### 5.2 Wireshark Packet Inspection Analysis
- **Packet #1 (TCP SYN/ACK):** Handshake initiated between client port 55488 and server port 8443.
- **Packet #2 (Client Hello):** IoT device advertises cipher suites and TLS 1.3 support.
- **Packet #3 (Server Hello, CertificateRequest):** Gateway server requests client certificate.
- **Packet #4 (Client Certificate, CertificateVerify):** Client sends `device01.crt` and RSA digital signature proving private key possession.
- **Packet #5+ (Application Data):** Telemetry payload is completely encrypted; zero plaintext JSON is visible to network sniffers.

---

## CHAPTER 6: CONCLUSION & FUTURE SCOPE
The project successfully designed, implemented, and validated a Mutual TLS (mTLS) authentication architecture for IoT ecosystems. By combining per-device X.509 certificates with application-layer RSA-SHA256 digital signatures, the system establishes a zero-trust communication channel. Future work includes integrating physical Hardware Security Modules (Microchip ATECC608A / TPM 2.0) and implementing Online Certificate Status Protocol (OCSP) stapling.

---

## REFERENCES
1. Rescorla, E., "The Transport Layer Security (TLS) Protocol Version 1.3", RFC 8446, IETF, 2018.
2. Cooper, D., et al., "Internet X.509 Public Key Infrastructure Certificate Profile", RFC 5280, 2008.
3. Stallings, W., "Cryptography and Network Security: Principles and Practice", 8th Ed., Pearson, 2020.
4. Rajasthan Technical University (RTU) Kota, "B.Tech VII Semester Cyber Security Lab (7CS4-22) Syllabus", 2026.
