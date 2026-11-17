# CSL-I11: Mutual TLS Authentication for IoT Devices
**RTU Kota — Cyber Security Lab (7CS4-22 / 7CIT4-22) — B.Tech VII Semester**  
**Swami Keshvanand Institute of Technology, Management & Gramothan (SKIT), Jaipur**  
**Linked Syllabus Experiment:** Exp 8 – Secure Storage, Transmission & Digital Signature

---

## 1. Project Overview

In standard TLS/HTTPS, authentication is asymmetric: only the server proves its identity to the client. This leaves IoT gateways vulnerable to spoofing, unauthorized device access, and rogue node injection.

**Mutual TLS (mTLS)** implements two-way cryptographic verification:
1. The **IoT Device** validates the Gateway Server's certificate against a trusted Root CA.
2. The **Gateway Server** demands (`ssl.CERT_REQUIRED`) and validates the individual X.509 certificate of each connecting IoT device.
3. Once mutual verification succeeds, a **TLS 1.3 encrypted tunnel** is established with AES-256-GCM.
4. Telemetry payloads are also **digitally signed (RSA-SHA256)** by the device to ensure non-repudiation and prevent data tampering (**Exp 8**).

---

## 2. Directory Structure

```
CSL-I11_mTLS_IoT/
├── certs/                                  # Generated X.509 certificates and RSA keys
│   ├── ca.crt & ca.key                    # Root Certificate Authority
│   ├── server.crt & server.key            # Gateway Server identity
│   ├── device01.crt & device01.key        # Legitimate Sensor Node 01
│   ├── device02.crt & device02.key        # Legitimate Actuator Node 02
│   ├── expired_device.crt & .key          # Expired certificate (Test TC-05)
│   ├── rogue_ca.crt & .key                # Unauthorized Rogue CA (Test TC-04)
│   └── rogue_device.crt & .key            # Rogue Device Certificate
├── logs/
│   └── server.log                         # Timestamped audit logs of all sessions & alerts
├── generate_certificates.py               # Generates all X.509 certs & keys using Python cryptography
├── crypto_utils.py                        # RSA-SHA256 Digital Signature signing & verification (Exp 8)
├── server.py                              # Multi-threaded mTLS Gateway Server (port 8443)
├── iot_device.py                          # Authenticated IoT Edge Node client
├── rogue_device.py                        # Attack simulations (no cert, fake CA, expired, tampered)
├── run_security_tests.py                  # Automated test runner (6/6 tests with audit table)
├── generate_project_report.py             # Generates formal Word (.docx) report following PDF guidelines
├── CSL-I11_Mutual_TLS_IoT_Project_Report.docx # Complete 15-25 page project report document
├── openssl_commands.bat                   # Batch script showing equivalent OpenSSL CLI commands
├── wireshark_capture_guide.md             # Guide for packet inspection and screenshot capture
├── create_submission_zip.py               # Packs deliverables into RollNo_Name_CSL-I11.zip
└── README.md                              # Complete documentation & Viva Guide
```

---

## 3. How to Run the Project

### Option A: Run the Complete Automated Test Suite (Fastest Demo)
Run all 6 test cases (positive + negative attack simulations) automatically:
```bash
python run_security_tests.py
```
This script will start the server, execute tests TC-01 through TC-06, verify all security controls, and display the audit table.

---

### Option B: Step-by-Step Manual Demonstration (Recommended for Viva)

#### Step 1: Regenerate Fresh Certificates (Optional)
```bash
python generate_certificates.py
```

#### Step 2: Start the Gateway Server
Open **Terminal 1**:
```bash
python server.py
```

#### Step 3: Run Legitimate IoT Sensor Node
Open **Terminal 2**:
```bash
python iot_device.py device01
```
* **Expected Output:** Handshake successful (TLS 1.3, AES-256-GCM), sensor readings sent, digital signature verified, `status: SUCCESS (200 OK)`.

#### Step 4: Run Attack & Negative Simulations
In **Terminal 2**, run:
```bash
python rogue_device.py
```
Choose from the interactive menu:
1. **No Client Certificate:** Server rejects with `PEER_DID_NOT_RETURN_A_CERTIFICATE`.
2. **Rogue Untrusted CA Certificate:** Server rejects with `CERTIFICATE_VERIFY_FAILED`.
3. **Expired Certificate:** Server rejects with `CERTIFICATE_VERIFY_FAILED`.
4. **Data Tampering Attack:** Connection succeeds, but modified sensor data triggers `401 REJECTED (Signature verification failed)`.

---

## 4. Generating the Project Report & Submission ZIP

### Generate the Word Report (.docx)
```bash
python generate_project_report.py
```
Outputs `CSL-I11_Mutual_TLS_IoT_Project_Report.docx` strictly formatted to SKIT guidelines (Times New Roman, 1.5 line spacing, 16pt/14pt headings, declarations, abstract, Chapters 1-6).

### Create the Final Submission ZIP
```bash
python create_submission_zip.py 23ESKCSxxx "Your Name"
```
Creates `23ESKCSxxx_YourName_CSL-I11.zip` in the parent directory, ready for submission to `vikash@skit.ac.in`.

---

## 5. Viva Voce Questions & Answers (25% Weightage)

**Q1: What is the fundamental difference between standard TLS and Mutual TLS (mTLS)?**  
*Answer:* In standard TLS, only the client authenticates the server's certificate. The client remains unauthenticated at the transport layer. In mTLS, both parties exchange and validate each other's X.509 certificates before establishing the session, enforcing mutual zero-trust identity verification.

**Q2: How does this project link to RTU Syllabus Experiment 8?**  
*Answer:* Exp 8 covers *Secure Storage, Transmission & Digital Signature*. In this project:
- *Secure Storage:* Private keys are isolated with restricted filesystem permissions (`0600`).
- *Secure Transmission:* Sensor payloads travel over an encrypted TLS 1.3 channel using AES-256-GCM.
- *Digital Signature:* Telemetry is digitally signed using the device's RSA private key (RSA-SHA256) and validated by the gateway with the device's public key from the X.509 certificate.

**Q3: What role does the `CertificateRequest` message play in the TLS handshake?**  
*Answer:* In TLS, when `ssl.CERT_REQUIRED` is set on the server, the server sends a `CertificateRequest` message specifying acceptable Certificate Authorities. The client must reply with its client certificate and a `CertificateVerify` signature message.

**Q4: What happens if an attacker tampers with the sensor readings in transit?**  
*Answer:* First, the TLS 1.3 AES-GCM cipher suite contains an authentication tag that detects in-flight packet alteration at the transport layer. Second, at the application layer, the server verifies the RSA-SHA256 digital signature over the telemetry payload. If any field (e.g., temperature) is altered, mathematical verification fails and the payload is rejected with error 401.

**Q5: How would you store private keys securely in production physical hardware?**  
*Answer:* On physical microcontrollers (e.g., ESP32, Raspberry Pi), private keys should not reside in standard flash memory. They should be stored in a dedicated Hardware Security Module (HSM) or secure element such as the Microchip ATECC608A or a Trusted Platform Module (TPM).
