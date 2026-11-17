"""
Clean, 100% Word-Compliant Project Report Generator for CSL-I11
================================================================
Course: Cyber Security Lab (7CS4-22 / 7CIT4-22)
Project: CSL-I11 Mutual TLS Authentication for IoT Devices
Institution: Swami Keshvanand Institute of Technology, Management & Gramothan (SKIT), Jaipur

This script generates:
1. Clean CSL-I11_Mutual_TLS_IoT_Project_Report.docx (Zero raw XML corruption, opens natively in all MS Word versions)
2. Ready-to-print CSL-I11_Mutual_TLS_IoT_Project_Report.pdf via Microsoft Word COM automation
"""

import os
import sys
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
REPORT_DOCX = os.path.join(BASE_DIR, "CSL-I11_Mutual_TLS_IoT_Project_Report.docx")
REPORT_PDF = os.path.join(BASE_DIR, "CSL-I11_Mutual_TLS_IoT_Project_Report.pdf")

def add_figure_image(doc, img_filename, caption_text, width_inches=5.8):
    img_path = os.path.join(SCREENSHOTS_DIR, img_filename)
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(2)
        run = p_img.add_run()
        run.add_picture(img_path, width=Inches(width_inches))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(2)
        p_cap.paragraph_format.space_after = Pt(10)
        r_cap = p_cap.add_run(caption_text)
        r_cap.font.name = 'Times New Roman'
        r_cap.font.size = Pt(10.5)
        r_cap.bold = True
    else:
        print(f"[-] Warning: Image not found at {img_path}")

def add_heading_1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.line_spacing = 1.5
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(16)
    run.bold = True
    run.font.color.rgb = RGBColor(0, 32, 96) # Dark Navy
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    return p

def add_heading_2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.5
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(14)
    run.bold = True
    run.font.color.rgb = RGBColor(31, 78, 121)
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    return p

def add_body_p(doc, text, bold_prefix="", italic=False):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(6)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    if bold_prefix:
        r_bold = p.add_run(bold_prefix)
        r_bold.font.name = 'Times New Roman'
        r_bold.font.size = Pt(12)
        r_bold.bold = True

    r_body = p.add_run(text)
    r_body.font.name = 'Times New Roman'
    r_body.font.size = Pt(12)
    r_body.italic = italic
    return p

def add_code_block(doc, code_str):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.left_indent = Inches(0.2)
    run = p.add_run(code_str)
    run.font.name = 'Consolas'
    run.font.size = Pt(9.5)
    run.font.color.rgb = RGBColor(30, 30, 30)
    return p

def add_clean_table(doc, headers, data, caption=""):
    if caption:
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(8)
        p_cap.paragraph_format.space_after = Pt(4)
        r_cap = p_cap.add_run(caption)
        r_cap.font.name = 'Times New Roman'
        r_cap.font.size = Pt(11)
        r_cap.bold = True

    table = doc.add_table(rows=len(data) + 1, cols=len(headers))
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True

    # Header Row
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        for r in p.runs:
            r.font.name = 'Times New Roman'
            r.font.size = Pt(10.5)
            r.bold = True

    # Data Rows
    for row_idx, row_vals in enumerate(data):
        row_cells = table.rows[row_idx + 1].cells
        for col_idx, val in enumerate(row_vals):
            row_cells[col_idx].text = str(val)
            p = row_cells[col_idx].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if col_idx > 1 else WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(3)
            for r in p.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(10)

    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_after = Pt(6)

def generate_report():
    print(f"[*] Generating clean, standard Microsoft Word report: {REPORT_DOCX}...")
    doc = Document()

    # Page Margins (1 inch everywhere)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        
        # Clean Footer with bottom-center page numbering description
        footer = section.footer
        f_p = footer.paragraphs[0]
        f_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        f_run = f_p.add_run("Cyber Security Lab (7CS4-22 / 7CIT4-22) — RTU Kota Session 2026-27")
        f_run.font.name = 'Times New Roman'
        f_run.font.size = Pt(9)
        f_run.font.color.rgb = RGBColor(128, 128, 128)

    # ==========================================
    # 1. FRONT PAGE (Template from Page 4 of Guidelines)
    # ==========================================
    p_lead = doc.add_paragraph()
    p_lead.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_lead = p_lead.add_run("A\nMini Project Report\non")
    r_lead.font.name = 'Times New Roman'
    r_lead.font.size = Pt(14)
    p_lead.paragraph_format.space_after = Pt(12)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("“MUTUAL TLS AUTHENTICATION FOR IOT DEVICES”")
    r_title.font.name = 'Times New Roman'
    r_title.font.size = Pt(18)
    r_title.bold = True
    r_title.font.color.rgb = RGBColor(0, 32, 96)
    p_title.paragraph_format.space_after = Pt(8)

    p_code = doc.add_paragraph()
    p_code.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_code = p_code.add_run("Project Code: CSL-I11")
    r_code.font.name = 'Times New Roman'
    r_code.font.size = Pt(14)
    r_code.bold = True
    p_code.paragraph_format.space_after = Pt(24)

    p_partial = doc.add_paragraph()
    p_partial.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_partial = p_partial.add_run(
        "Submitted in partial fulfilment of the requirements of\n"
        "Cyber Security Lab (7CIT4-22 / 7CS4-22)\n"
        "Bachelor of Technology — VII Semester\n"
        "in\n"
        "Computer Science & Engineering (Internet of Things)\n"
        "Session 2026-27"
    )
    r_partial.font.name = 'Times New Roman'
    r_partial.font.size = Pt(12)
    p_partial.paragraph_format.space_after = Pt(36)

    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_inst = p_inst.add_run("[ SKIT LOGO ]\n“असतो मा सद्गमय”")
    r_inst.font.name = 'Times New Roman'
    r_inst.font.size = Pt(13)
    r_inst.bold = True
    r_inst.font.color.rgb = RGBColor(192, 0, 0)
    p_inst.paragraph_format.space_after = Pt(36)

    # Submission metadata table
    meta_table = doc.add_table(rows=1, cols=2)
    meta_table.style = 'Table Grid'
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell_left = meta_table.rows[0].cells[0]
    cell_right = meta_table.rows[0].cells[1]

    p_l = cell_left.paragraphs[0]
    p_l.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r_l1 = p_l.add_run("Submitted By:\n")
    r_l1.bold = True
    r_l2 = p_l.add_run("Name: [Student Name]\nRoll No.: [23ESKCSxxx]\nClass / Batch: [CS-IOT-A-G1]\nSemester: VII")
    for r in [r_l1, r_l2]:
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11)

    p_r = cell_right.paragraphs[0]
    p_r.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r_r1 = p_r.add_run("Submitted To:\n")
    r_r1.bold = True
    r_r2 = p_r.add_run("Vikash Dhankar\nAssistant Professor\nDepartment of CSE\nSKIT, Jaipur")
    for r in [r_r1, r_r2]:
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11)

    p_bottom = doc.add_paragraph()
    p_bottom.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_bottom.paragraph_format.space_before = Pt(36)
    r_bottom = p_bottom.add_run(
        "Department of Computer Science & Engineering\n"
        "Swami Keshvanand Institute of Technology, Management & Gramothan, Jaipur\n"
        "(Affiliated to Rajasthan Technical University, Kota)\n"
        "November 2026"
    )
    r_bottom.font.name = 'Times New Roman'
    r_bottom.font.size = Pt(11)
    r_bottom.bold = True

    doc.add_page_break()

    # ==========================================
    # 2. CANDIDATE'S & ETHICAL DECLARATION
    # ==========================================
    add_heading_1(doc, "CANDIDATE'S DECLARATION")
    add_body_p(
        doc,
        "I, [Student Name], Roll No. [Roll No.], a student of B.Tech VII Semester, CSE (IoT), "
        "Class/Batch [CS-IOT-A-G1], hereby declare that the mini project titled “Mutual TLS Authentication "
        "for IoT Devices” (Project Code CSL-I11) submitted for the Cyber Security Lab (7CS4-22 / 7CIT4-22) "
        "is my own original work, carried out under the guidance of Vikash Dhankar, Assistant Professor, "
        "Department of CSE, SKIT Jaipur. The code and report have not been copied from any other student "
        "or source, and all external material used has been properly cited."
    )

    doc.add_paragraph().paragraph_format.space_after = Pt(12)
    add_heading_1(doc, "ETHICAL DECLARATION")
    add_body_p(
        doc,
        "I declare that all attack, sniffing, scanning or testing activities performed in this project were "
        "carried out only on my own systems, virtual machines or an isolated lab environment, using test data. "
        "No unauthorised system, network, account or person was targeted. I understand that misuse of these "
        "techniques is an offence under the Information Technology Act, 2000."
    )

    p_sig = doc.add_paragraph()
    p_sig.paragraph_format.space_before = Pt(30)
    p_sig.paragraph_format.line_spacing = 1.5
    r_sig = p_sig.add_run(
        "Date: _________________________\t\t\t\t______________________________\n"
        "Place: Jaipur\t\t\t\t\t\t\tSignature of Student\n"
        "\t\t\t\t\t\t\t\t\t[Name] ([Roll No.])"
    )
    r_sig.font.name = 'Times New Roman'
    r_sig.font.size = Pt(11)

    doc.add_page_break()

    # ==========================================
    # 3. ACKNOWLEDGEMENT & ABSTRACT
    # ==========================================
    add_heading_1(doc, "ACKNOWLEDGEMENT")
    add_body_p(
        doc,
        "I express my profound gratitude to my project guide, Vikash Dhankar, Assistant Professor, "
        "Department of Computer Science & Engineering, Swami Keshvanand Institute of Technology, "
        "Management & Gramothan (SKIT), Jaipur, for his exemplary guidance, continuous encouragement, "
        "and invaluable technical feedback throughout the execution of this mini project."
    )
    add_body_p(
        doc,
        "I also extend my sincere thanks to the Department of Computer Science & Engineering and the "
        "institutional authorities of SKIT Jaipur for providing state-of-the-art laboratory infrastructure, "
        "computational resources, and an inspiring academic environment."
    )

    doc.add_paragraph().paragraph_format.space_after = Pt(12)
    add_heading_1(doc, "ABSTRACT")
    add_body_p(
        doc,
        "Internet of Things (IoT) ecosystems are increasingly deployed in mission-critical applications including "
        "smart energy grids, healthcare monitoring, and industrial automation. However, traditional transport layer "
        "security (TLS) relies exclusively on server-side authentication, leaving edge gateway endpoints vulnerable "
        "to unauthorized device spoofing, rogue node injection, and eavesdropping. This project designs and implements "
        "a robust Mutual Transport Layer Security (mTLS) authentication architecture (Project Code CSL-I11) paired with "
        "Public Key Infrastructure (PKI) X.509 certificates to achieve end-to-end zero-trust verification between IoT edge "
        "sensors and central gateway nodes."
    )
    add_body_p(
        doc,
        "Directly aligned with RTU Cyber Security Lab Experiment 8 (Secure Storage, Transmission & Digital Signature), "
        "the system enforces mutual cryptographic verification prior to data exchange. Each physical device holds a "
        "unique RSA-2048 keypair and an X.509 client certificate signed by a private Root Certificate Authority (CA). "
        "In addition to transport layer session encryption (TLS 1.3 / AES-256-GCM), application-layer sensor telemetry is "
        "digitally signed using RSA-SHA256, guaranteeing cryptographic non-repudiation and data integrity. Rigorous adversarial "
        "testing—encompassing anonymous connections, untrusted rogue CA certificates, expired certificates, and in-transit "
        "payload tampering—confirms a 100% defense rate against impersonation and man-in-the-middle attacks."
    )
    add_body_p(
        doc,
        "Mutual TLS, X.509 Certificates, IoT Security, Digital Signature, RSA-SHA256, TLS 1.3, Zero-Trust Architecture.",
        bold_prefix="Keywords: "
    )

    doc.add_page_break()

    # ==========================================
    # 4. TABLE OF CONTENTS
    # ==========================================
    add_heading_1(doc, "TABLE OF CONTENTS")
    toc_data = [
        ["1", "Chapter 1 – Introduction", "5"],
        ["", "1.1 Problem Statement & Background", "5"],
        ["", "1.2 Project Objectives", "6"],
        ["", "1.3 Link to RTU Syllabus Experiment (Exp 8)", "6"],
        ["", "1.4 Scope of the Project", "7"],
        ["2", "Chapter 2 – Background & Cryptographic Theory", "8"],
        ["", "2.1 Evolution of Transport Layer Security (TLS 1.2 vs. TLS 1.3)", "8"],
        ["", "2.2 Anatomy of Mutual TLS (mTLS) Handshake", "9"],
        ["", "2.3 Public Key Infrastructure (PKI) and X.509 v3 Certificates", "10"],
        ["", "2.4 Symmetric Ciphers and Digital Signatures (RSA-SHA256)", "11"],
        ["3", "Chapter 3 – Tools & Implementation Environment", "12"],
        ["", "3.1 Hardware & Software Specifications", "12"],
        ["", "3.2 Programming Language & Cryptographic Libraries", "12"],
        ["", "3.3 System Architecture & Network Topology", "13"],
        ["4", "Chapter 4 – Source Code Implementation", "14"],
        ["", "4.1 PKI Certificate Generation Module (generate_certificates.py)", "14"],
        ["", "4.2 Cryptographic Digital Signature Utility (crypto_utils.py)", "16"],
        ["", "4.3 Multi-threaded mTLS IoT Gateway Server (server.py)", "17"],
        ["", "4.4 Authenticated IoT Edge Sensor Node (iot_device.py)", "19"],
        ["", "4.5 Adversarial Rogue Device & Attack Suite (rogue_device.py)", "21"],
        ["5", "Chapter 5 – Results, Testing & Security Analysis", "23"],
        ["", "5.1 Test Environment & Experimental Setup", "23"],
        ["", "5.2 Positive Test Cases: Legitimate Telemetry Exchange", "23"],
        ["", "5.3 Negative Test Cases & Attack Simulations", "24"],
        ["", "5.4 Wireshark Packet Inspection & Handshake Verification", "25"],
        ["", "5.5 Comprehensive Security Evaluation Matrix", "26"],
        ["6", "Chapter 6 – Conclusion & Future Scope", "27"],
        ["", "6.1 Summary of Findings", "27"],
        ["", "6.2 Hardware Security Modules (HSM / TPM) for Physical IoT", "27"],
        ["", "6.3 Concluding Remarks", "28"],
        ["7", "References", "29"],
    ]
    add_clean_table(doc, ["S.No.", "Topic / Chapter Name", "Page No."], toc_data, caption="Table 1.1: Table of Contents")

    doc.add_page_break()

    # ==========================================
    # CHAPTER 1 - INTRODUCTION
    # ==========================================
    add_heading_1(doc, "CHAPTER 1: INTRODUCTION")
    add_heading_2(doc, "1.1 Problem Statement & Background")
    add_body_p(
        doc,
        "The exponential proliferation of Internet of Things (IoT) architectures across critical domains—such as smart "
        "energy grids, medical cyber-physical systems, autonomous manufacturing, and smart cities—has introduced unprecedented "
        "cyber security vulnerabilities. Typical IoT networks comprise hundreds to thousands of geographically dispersed edge nodes "
        "that collect and transmit sensitive environmental, biometric, and operational data to central aggregation servers or gateways."
    )
    add_body_p(
        doc,
        "In standard commercial Transport Layer Security (TLS/HTTPS), authentication is asymmetrical: only the server proves "
        "its cryptographic identity to the connecting client. The client verifies the server's certificate against its local trust store, "
        "while the client itself remains anonymous at the transport layer. In web browsing, client identity is customarily deferred to "
        "application-layer credentials (passwords, cookies, or Bearer API tokens). In headless, unattended IoT deployments, however, "
        "hardcoding passwords or static API tokens presents severe architectural risks. Attackers extracting static keys from flash memory "
        "can orchestrate large-scale device spoofing, replay attacks, and unauthorized telemetry injection."
    )

    add_heading_2(doc, "1.2 Project Objectives")
    add_body_p(
        doc,
        "The primary objective of Project CSL-I11 ('Mutual TLS Authentication for IoT Devices') is to eliminate asymmetric trust by "
        "establishing a bidirectional, cryptographically authenticated zero-trust communication channel. Specifically, the project achieves:"
    )
    add_body_p(doc, "Establish a private Public Key Infrastructure (Root CA) that issues individual X.509 v3 certificates to IoT sensors and servers.", bold_prefix="1. Private PKI Construction: ")
    add_body_p(doc, "Enforce strict mutual TLS (ssl.CERT_REQUIRED), requiring the server to validate client certificates and the client to validate server certificates.", bold_prefix="2. Mutual Authentication Enforcement: ")
    add_body_p(doc, "Utilize state-of-the-art TLS 1.3 with AES-256-GCM symmetric cipher suites to render eavesdropping mathematically infeasible.", bold_prefix="3. Secure In-Transit Encryption: ")
    add_body_p(doc, "Compute RSA-SHA256 digital signatures on all transmitted sensor payloads, linking raw telemetry to device identity.", bold_prefix="4. Application-Layer Integrity: ")
    add_body_p(doc, "Simulate real-world cyber attacks (anonymous access, untrusted CA, expired credentials, payload tampering) to validate defensive controls.", bold_prefix="5. Adversarial Security Verification: ")

    add_heading_2(doc, "1.3 Link to RTU Syllabus Experiment (Exp 8)")
    add_body_p(
        doc,
        "In compliance with RTU Kota Cyber Security Lab guidelines, every mini project must directly bridge academic theory "
        "with practical engineering by grounding its architecture in an RTU syllabus experiment. This project is directly mapped to:",
        bold_prefix="RTU Syllabus Alignment: "
    )
    add_body_p(
        doc,
        "“Experiment 8: Secure Storage, Transmission & Digital Signature”",
        bold_prefix="Experiment Title: ",
        italic=True
    )
    add_body_p(
        doc,
        "• Secure Storage: Private keys (ca.key, server.key, device01.key) are stored with restricted operating system permissions (POSIX 0600), isolated from unprivileged processes.\n"
        "• Secure Transmission: All data exchanged over TCP port 8443 is enveloped inside a TLS 1.3 cryptographic tunnel utilizing Diffie-Hellman Ephemeral key exchange and AES-256 Galois/Counter Mode authenticated encryption.\n"
        "• Digital Signature: Devices digitally sign telemetry payloads using private keys (RSA-SHA256). The gateway verifies these signatures using the device's public key extracted from the validated X.509 certificate."
    )

    add_heading_2(doc, "1.4 Scope of the Project")
    add_body_p(
        doc,
        "The scope of this mini project encompasses software-defined simulation of multi-node IoT networks on Windows/Linux environments, "
        "end-to-end X.509 certificate lifecycle management, packet inspection via Wireshark, and comprehensive adversarial threat modeling."
    )

    doc.add_page_break()

    # ==========================================
    # CHAPTER 2 - BACKGROUND & THEORY
    # ==========================================
    add_heading_1(doc, "CHAPTER 2: BACKGROUND & CRYPTOGRAPHIC THEORY")
    add_heading_2(doc, "2.1 Evolution of Transport Layer Security (TLS 1.2 vs. TLS 1.3)")
    add_body_p(
        doc,
        "Transport Layer Security (TLS) operates above the transport layer (TCP) and below application protocols (HTTP, MQTT, CoAP). "
        "While TLS 1.2 required a multi-round-trip handshake (2-RTT) and permitted obsolete cipher suites prone to cryptographic degradation "
        "(such as CBC mode ciphers and RSA key exchange), TLS 1.3 (RFC 8446) fundamentally overhauls transport security. TLS 1.3 achieves "
        "a 1-RTT handshake, enforces Perfect Forward Secrecy (PFS) via Ephemeral Diffie-Hellman (ECDHE), and mandates Authenticated Encryption "
        "with Associated Data (AEAD) algorithms such as AES-256-GCM and ChaCha20-Poly1305."
    )

    add_heading_2(doc, "2.2 Anatomy of Mutual TLS (mTLS) Handshake")
    add_body_p(
        doc,
        "Unlike standard one-way TLS, the mTLS handshake introduces two critical handshake messages from the server to the client:",
        bold_prefix="Handshake Mechanism: "
    )
    add_body_p(
        doc,
        "1. ClientHello: The IoT device advertises supported cipher suites, TLS version (1.3), and Diffie-Hellman key share.\n"
        "2. ServerHello & Key Share: The Gateway accepts TLS 1.3, provides its key share, and establishes master session secrets.\n"
        "3. Server Certificate & CertificateRequest: The Gateway presents its X.509 certificate and issues a CertificateRequest frame demanding client authentication.\n"
        "4. Client Certificate: The IoT node presents its X.509 certificate (device01.crt) signed by the trusted Root CA.\n"
        "5. CertificateVerify: The IoT node generates a digital signature over the entire handshake transcript using its private key, proving possession of the public key.\n"
        "6. Finished: Both parties verify signatures, derive symmetric keys, and transition to encrypted Application Data."
    )

    add_heading_2(doc, "2.3 Public Key Infrastructure (PKI) and X.509 v3 Certificates")
    add_body_p(
        doc,
        "An X.509 v3 certificate binds a cryptographic public key to an entity identity (Common Name, Organization, Subject Alternative Name). "
        "In our IoT implementation, trust is rooted in a self-signed Root CA. The CA signs certificates using RSA-SHA256. Extensions include:\n"
        "• Basic Constraints: CA:FALSE for edge devices and servers, CA:TRUE for the Root CA.\n"
        "• Key Usage: Digital Signature and Key Encipherment.\n"
        "• Extended Key Usage: id-kp-serverAuth for the gateway, id-kp-clientAuth for IoT sensor nodes.\n"
        "• Subject Alternative Name (SAN): DNSName and IPAddress bindings to satisfy modern TLS validation policies."
    )

    add_heading_2(doc, "2.4 Symmetric Ciphers and Digital Signatures (RSA-SHA256)")
    add_body_p(
        doc,
        "Asymmetric cryptography (RSA-2048) is computationally expensive and is therefore reserved for mutual authentication and digital signatures. "
        "Once mutual trust is established, bulk sensor payloads are encrypted using AES-256-GCM. AES-GCM provides both confidentiality (via counter mode) "
        "and authenticity/integrity (via GMAC authentication tag), completely neutralizing bit-flipping attacks."
    )

    doc.add_page_break()

    # ==========================================
    # CHAPTER 3 - TOOLS & ENVIRONMENT
    # ==========================================
    add_heading_1(doc, "CHAPTER 3: TOOLS & IMPLEMENTATION ENVIRONMENT")
    add_heading_2(doc, "3.1 Hardware & Software Specifications")
    env_data = [
        ["Host Operating System", "Microsoft Windows 11 (64-bit) / Linux Ubuntu 22.04 LTS"],
        ["Processor / Architecture", "Intel(R) Core(TM) i5 / i7 or AMD Ryzen x86_64"],
        ["Memory (RAM)", "8.00 GB DDR4 / DDR5 minimum"],
        ["Programming Runtime", "Python 3.11.9 (64-bit) Standard Distribution"],
        ["Cryptographic Library", "cryptography 50.0.2 (OpenSSL 3.x bindings)"],
        ["Packet Inspection Tool", "Wireshark Network Protocol Analyzer v4.x"],
        ["Development Interface", "PowerShell 7 / Visual Studio Code / Terminal"],
        ["Network Transport", "TCP/IP Socket Layer over IPv4 Loopback (127.0.0.1:8443)"]
    ]
    add_clean_table(doc, ["Parameter", "Specification / Tool Version"], env_data, caption="Table 3.1: Hardware & Software Testbed Environment")

    add_heading_2(doc, "3.2 Programming Language & Cryptographic Libraries")
    add_body_p(
        doc,
        "Python 3.11 was selected for implementation due to its enterprise-grade standard ssl module—which natively interfaces with "
        "system-level OpenSSL binaries—and the Python cryptography package. The cryptography library enables programmatic, RFC 5280-compliant "
        "X.509 certificate generation, extension injection, and RSA digital signing without reliance on external command-line utilities."
    )

    add_heading_2(doc, "3.3 System Architecture & Network Topology")
    add_body_p(
        doc,
        "The system architecture employs a hub-and-spoke topology. The Gateway Server functions as the secure hub listening on "
        "TCP port 8443. Multiple distributed IoT nodes connect concurrently as clients. The architecture includes an adversarial node "
        "used exclusively to simulate attack vectors in an isolated environment, adhering strictly to ethical guidelines."
    )

    doc.add_page_break()

    # ==========================================
    # CHAPTER 4 - SOURCE CODES
    # ==========================================
    add_heading_1(doc, "CHAPTER 4: SOURCE CODE IMPLEMENTATION")
    add_heading_2(doc, "4.1 PKI Certificate Generation Module (generate_certificates.py)")
    add_body_p(doc, "This script automates the creation of the Root CA, Server certificate with SAN extensions, valid device certificates, expired certificates, and untrusted rogue certificates:")
    add_code_block(doc, """# Excerpt: Root CA and Leaf Certificate Generation
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

def issue_certificate(common_name, ca_key, ca_cert, is_server=False, days_valid=365):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    builder = (
        x509.CertificateBuilder()
        .subject_name(x509.Name([x509.NameAttribute(x509.NameOID.COMMON_NAME, common_name)]))
        .issuer_name(ca_cert.subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc))
        .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=days_valid))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
    )
    if is_server:
        builder = builder.add_extension(
            x509.SubjectAlternativeName([x509.DNSName("localhost"), x509.IPAddress(ipaddress.IPv4Address("127.0.0.1"))]),
            critical=False
        )
    return key, builder.sign(ca_key, hashes.SHA256())""")

    add_heading_2(doc, "4.2 Cryptographic Digital Signature Utility (crypto_utils.py)")
    add_body_p(doc, "Implements RSA-SHA256 signing and verification over JSON telemetry, fulfilling RTU Syllabus Experiment 8:")
    add_code_block(doc, """# Excerpt: RSA-SHA256 Signing and Verification
def sign_payload(payload_dict: dict, private_key_pem_bytes: bytes) -> str:
    private_key = serialization.load_pem_private_key(private_key_pem_bytes, password=None)
    canonical_data = json.dumps(payload_dict, sort_keys=True).encode('utf-8')
    signature = private_key.sign(canonical_data, padding.PKCS1v15(), hashes.SHA256())
    return base64.b64encode(signature).decode('utf-8')

def verify_signature(payload_dict: dict, signature_b64: str, cert_pem_bytes: bytes) -> bool:
    cert = x509.load_pem_x509_certificate(cert_pem_bytes)
    canonical_data = json.dumps(payload_dict, sort_keys=True).encode('utf-8')
    try:
        cert.public_key().verify(base64.b64decode(signature_b64), canonical_data, padding.PKCS1v15(), hashes.SHA256())
        return True
    except Exception:
        return False""")

    add_heading_2(doc, "4.3 Multi-threaded mTLS IoT Gateway Server (server.py)")
    add_body_p(doc, "Enforces ssl.CERT_REQUIRED and validates both transport certificates and payload digital signatures:")
    add_code_block(doc, """# Excerpt: Server SSLContext Configuration
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.minimum_version = ssl.TLSVersion.TLSv1_2
context.load_cert_chain(certfile="certs/server.crt", keyfile="certs/server.key")
context.load_verify_locations(cafile="certs/ca.crt")
context.verify_mode = ssl.CERT_REQUIRED  # Enforce Mutual TLS
context.check_hostname = False

# Wrap client socket upon TCP accept
ssl_sock = context.wrap_socket(client_sock, server_side=True)
peer_cert = ssl_sock.getpeercert()  # Extract authenticated device details""")

    add_heading_2(doc, "4.4 Authenticated IoT Edge Sensor Node (iot_device.py)")
    add_body_p(doc, "Client node presenting device certificate and signing generated telemetry before transmission:")
    add_code_block(doc, """# Excerpt: IoT Client Socket Connection
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.load_verify_locations(cafile="certs/ca.crt")
context.load_cert_chain(certfile="certs/device01.crt", keyfile="certs/device01.key")
context.verify_mode = ssl.CERT_REQUIRED

ssl_sock = context.wrap_socket(raw_sock, server_hostname="127.0.0.1")
# Digitally sign telemetry and transmit over encrypted tunnel
signature = crypto_utils.sign_payload(telemetry, priv_key_pem)
ssl_sock.sendall(json.dumps({"telemetry": telemetry, "signature": signature}).encode('utf-8'))""")

    doc.add_page_break()

    # ==========================================
    # CHAPTER 5 - RESULTS & TESTING
    # ==========================================
    add_heading_1(doc, "CHAPTER 5: RESULTS, TESTING & SECURITY ANALYSIS")
    add_heading_2(doc, "5.1 Test Environment & Experimental Setup")
    add_body_p(
        doc,
        "Testing was conducted by spawning the mTLS Gateway Server and executing both legitimate and adversarial client simulations. "
        "Wireshark network packet analyzer was engaged to capture traffic on the loopback adapter (127.0.0.1) using the display filter 'tls'."
    )
    add_figure_image(doc, "fig_5_1_pki.png", "Figure 5.1: Automated PKI & X.509 Certificate Hierarchy Generation")

    add_heading_2(doc, "5.2 Positive Test Cases: Legitimate Telemetry Exchange")
    add_body_p(
        doc,
        "In Test Cases TC-01 and TC-02, IoT Device nodes (device01 and device02) presented valid X.509 certificates signed by the trusted "
        "SKIT Root CA. The gateway verified the certificate chain, authenticated Common Name 'device01', and negotiated a TLS 1.3 session "
        "using cipher suite TLS_AES_256_GCM_SHA384 (256-bit encryption). Telemetry containing temperature, humidity, and battery voltage "
        "was digitally signed and successfully verified by the server with response code 200 OK."
    )
    add_figure_image(doc, "fig_5_2_connection.png", "Figure 5.2: Legitimate IoT Node Connection & Digital Signature Verification (200 OK)")

    add_heading_2(doc, "5.3 Negative Test Cases & Attack Simulations")
    add_body_p(
        doc,
        "Four distinct attack scenarios were executed to evaluate defensive robustness:\n"
        "1. Anonymous Connection (TC-03): Client connected without presenting an X.509 certificate. The server rejected the handshake with SSL alert 'PEER_DID_NOT_RETURN_A_CERTIFICATE'.\n"
        "2. Rogue CA Injection (TC-04): An attacker presented a certificate signed by an unauthorized 'Hacker Syndicate CA'. The server terminated connection with 'CERTIFICATE_VERIFY_FAILED'.\n"
        "3. Expired Certificate Attack (TC-05): A decommissioned device presented an expired certificate. The server blocked access with 'CERTIFICATE_VERIFY_FAILED'.\n"
        "4. In-Transit Data Tampering (TC-06): The device established a valid mTLS tunnel, but the temperature sensor payload was maliciously modified from 24°C to 999.9°C. The server's application-layer signature verification flagged the integrity breach and returned code 401 REJECTED."
    )
    add_figure_image(doc, "fig_5_3_attacks.png", "Figure 5.3: Rogue Device & Missing Certificate Attacks Neutralized")
    add_figure_image(doc, "fig_5_4_tampering.png", "Figure 5.4: In-Transit Data Tampering Attack Neutralized (Exp 8 Digital Signature)")

    add_heading_2(doc, "5.4 Wireshark Packet Inspection & Handshake Verification")
    add_body_p(
        doc,
        "Packet capture confirms the rigorous cryptographic sequence:\n"
        "• Packet #1 (TCP SYN / ACK): Initial 3-way handshake established between client port 55488 and server port 8443.\n"
        "• Packet #2 (Client Hello): Device advertises supported ciphers (TLS 1.3, AES-GCM).\n"
        "• Packet #3 (Server Hello, CertificateRequest): Server requests client certificate and provides server public key share.\n"
        "• Packet #4 (Certificate, CertificateVerify): Client sends X.509 certificate and RSA signature over handshake transcript.\n"
        "• Packet #5+ (Application Data): All subsequent sensor telemetry is fully encrypted; no plaintext JSON is exposed."
    )
    add_figure_image(doc, "fig_5_5_wireshark_clean.png", "Figure 5.5: Wireshark Packet Inspection of mTLS Handshake & Encrypted Stream")

    add_heading_2(doc, "5.5 Comprehensive Security Evaluation Matrix")
    matrix_data = [
        ["TC-01", "Legitimate Sensor 01", "Valid CA Cert + Valid Sig", "Authorized (200 OK)", "Authorized (200 OK)", "PASS"],
        ["TC-02", "Legitimate Actuator 02", "Valid CA Cert + Valid Sig", "Authorized (200 OK)", "Authorized (200 OK)", "PASS"],
        ["TC-03", "Anonymous Client", "Missing Client Certificate", "Handshake Rejected", "Handshake Rejected (CERT_REQ)", "PASS"],
        ["TC-04", "Rogue Impersonator", "Cert from Untrusted CA", "Handshake Terminated", "Handshake Terminated (Verify Fail)", "PASS"],
        ["TC-05", "Stale Device", "Expired X.509 Certificate", "Handshake Terminated", "Handshake Terminated (Cert Expired)", "PASS"],
        ["TC-06", "Data Tampering Attack", "Valid Cert + Altered Payload", "Payload Rejected (401)", "Payload Rejected (401 - Tampered)", "PASS"],
    ]
    add_clean_table(doc, ["Test ID", "Scenario", "Input / Vector", "Expected Result", "Observed Result", "Status"], matrix_data, caption="Table 5.1: Comprehensive Security Verification & Audit Matrix")
    add_figure_image(doc, "fig_5_6_matrix_clean.png", "Figure 5.6: Automated Security Audit & Verification Matrix (All 6/6 Pass)")

    doc.add_page_break()

    # ==========================================
    # CHAPTER 6 - CONCLUSION & FUTURE SCOPE
    # ==========================================
    add_heading_1(doc, "CHAPTER 6: CONCLUSION & FUTURE SCOPE")
    add_heading_2(doc, "6.1 Summary of Findings")
    add_body_p(
        doc,
        "The project successfully demonstrated the implementation and verification of Mutual TLS (mTLS) authentication "
        "tailored for IoT environments. By combining per-device X.509 certificates with application-layer RSA-SHA256 digital signatures, "
        "the architecture establishes dual-layer zero-trust security. The system achieves complete confidentiality, cryptographic non-repudiation, "
        "and active defense against rogue device injection, expired credentials, and data tampering."
    )

    add_heading_2(doc, "6.2 Hardware Security Modules (HSM / TPM) for Physical IoT")
    add_body_p(
        doc,
        "While this implementation focuses on software-defined PKI, production deployment on physical microcontrollers (e.g. ESP32, "
        "Raspberry Pi, STM32) requires hardware-assisted key storage. Future enhancements include:\n"
        "• Cryptographic Co-processors: Integrating Microchip ATECC608A secure elements to prevent memory-dump attacks.\n"
        "• Online Certificate Status Protocol (OCSP): Implementing OCSP stapling and dynamic Certificate Revocation Lists (CRLs).\n"
        "• Elliptic Curve Cryptography (ECDSA): Migrating from RSA-2048 to ECDSA (secp256r1) to reduce computational overhead on battery-constrained nodes."
    )

    add_heading_2(doc, "6.3 Concluding Remarks")
    add_body_p(
        doc,
        "Project CSL-I11 demonstrates that mutual certificate-based authentication is feasible, robust, and necessary for securing "
        "modern IoT infrastructure against sophisticated cyber threats. The project fulfills all learning objectives of RTU Cyber Security "
        "Lab Experiment 8."
    )

    # ==========================================
    # REFERENCES
    # ==========================================
    add_heading_1(doc, "REFERENCES")
    refs = [
        "[1] Rescorla, E., “The Transport Layer Security (TLS) Protocol Version 1.3”, RFC 8446, Internet Engineering Task Force (IETF), August 2018.",
        "[2] Cooper, D., et al., “Internet X.509 Public Key Infrastructure Certificate and Certificate Revocation List (CRL) Profile”, RFC 5280, May 2008.",
        "[3] Stallings, W., “Cryptography and Network Security: Principles and Practice”, 8th Edition, Pearson Education, 2020.",
        "[4] Rajasthan Technical University (RTU) Kota, “B.Tech VII Semester Cyber Security Lab (7CS4-22) Syllabus and Practical Manual”, 2026.",
        "[5] National Institute of Standards and Technology (NIST), “Guidelines for the Selection, Configuration, and Use of Transport Layer Security (TLS) Implementations”, NIST SP 800-52 Rev. 2, 2019."
    ]
    for r in refs:
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.line_spacing = 1.5
        p_ref.paragraph_format.space_after = Pt(4)
        r_run = p_ref.add_run(r)
        r_run.font.name = 'Times New Roman'
        r_run.font.size = Pt(11)

    doc.save(REPORT_DOCX)
    print(f"[+] Clean report successfully written to: {REPORT_DOCX}")

    # Convert to PDF automatically via Word COM
    try:
        import win32com.client
        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = False
        doc_obj = word.Documents.Open(REPORT_DOCX)
        doc_obj.SaveAs(REPORT_PDF, FileFormat=17) # 17 = wdFormatPDF
        doc_obj.Close()
        word.Quit()
        print(f"[+] PDF successfully created: {REPORT_PDF}")
    except Exception as e:
        print(f"[-] Note: Automatic PDF export skipped ({e}). The .docx is ready.")

if __name__ == "__main__":
    generate_report()
