"""
PKI & X.509 Certificate Generator for mTLS IoT Architecture
============================================================
Course: Cyber Security Lab (7CS4-22 / 7CIT4-22)
Project: CSL-I11 Mutual TLS Authentication for IoT Devices
Experiment Link: Exp 8 - Secure Storage, Transmission & Digital Signature

This script creates:
1. Root Certificate Authority (CA) - Private Key & Self-Signed Root Certificate
2. Server Certificate & Private Key (signed by Root CA, with SAN: localhost, 127.0.0.1)
3. Valid IoT Device 01 Certificate & Private Key (signed by Root CA)
4. Valid IoT Device 02 Certificate & Private Key (signed by Root CA)
5. Untrusted Rogue Device Certificate & Private Key (signed by an unapproved Rogue CA)
6. Expired IoT Device Certificate & Private Key (for testing expiration defenses)
"""

import os
import datetime
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import ipaddress

CERTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "certs")
os.makedirs(CERTS_DIR, exist_ok=True)

def generate_rsa_key(key_size=2048):
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size
    )

def save_key(key, filename):
    filepath = os.path.join(CERTS_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )
        )
    return filepath

def save_cert(cert, filename):
    filepath = os.path.join(CERTS_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    return filepath

def build_ca(common_name="IoT-Root-CA", org="SKIT CyberSec Lab"):
    print(f"[*] Generating Root CA ({common_name})...")
    ca_key = generate_rsa_key(2048)
    save_key(ca_key, f"{common_name}.key")

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "IN"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Rajasthan"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Jaipur"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, org),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "IoT Security Trust Center"),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])

    ca_cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1))
        .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=3650)) # 10 years
        .add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        )
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=True,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(ca_key.public_key()),
            critical=False,
        )
        .sign(ca_key, hashes.SHA256())
    )
    save_cert(ca_cert, f"{common_name}.crt")
    return ca_key, ca_cert

def issue_certificate(common_name, ca_key, ca_cert, is_server=False, days_valid=365, expired=False):
    role = "Server" if is_server else "Device"
    print(f"[*] Issuing {role} Certificate: {common_name}...")
    key = generate_rsa_key(2048)
    save_key(key, f"{common_name}.key")

    subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "IN"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Rajasthan"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Jaipur"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "SKIT CyberSec Lab"),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Edge Devices" if not is_server else "Central Gateway"),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])

    now = datetime.datetime.now(datetime.timezone.utc)
    if expired:
        not_before = now - datetime.timedelta(days=60)
        not_after = now - datetime.timedelta(days=10) # Expired 10 days ago
    else:
        not_before = now - datetime.timedelta(days=1)
        not_after = now + datetime.timedelta(days=days_valid)

    builder = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(ca_cert.subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(not_before)
        .not_valid_after(not_after)
        .add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True,
        )
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=True,
                key_encipherment=True,
                data_encipherment=True,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
    )

    if is_server:
        builder = builder.add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]),
            critical=False,
        )
        # SAN extension is mandatory for modern TLS servers
        builder = builder.add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
            ]),
            critical=False,
        )
    else:
        builder = builder.add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.CLIENT_AUTH]),
            critical=False,
        )
        builder = builder.add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(common_name),
            ]),
            critical=False,
        )

    cert = builder.sign(ca_key, hashes.SHA256())
    save_cert(cert, f"{common_name}.crt")
    return key, cert

def generate_all():
    print("=" * 65)
    print("  PKI Generator for Mutual TLS (mTLS) IoT Authentication")
    print("=" * 65)

    # 1. Main Trusted CA
    ca_key, ca_cert = build_ca("ca", "SKIT IoT Authority")

    # 2. Server Certificate
    issue_certificate("server", ca_key, ca_cert, is_server=True)

    # 3. Legitimate IoT Device 1
    issue_certificate("device01", ca_key, ca_cert, is_server=False)

    # 4. Legitimate IoT Device 2
    issue_certificate("device02", ca_key, ca_cert, is_server=False)

    # 5. Expired IoT Device (for testing expiry defense)
    issue_certificate("expired_device", ca_key, ca_cert, is_server=False, expired=True)

    # 6. Rogue / Untrusted CA & Device
    print("\n[*] Generating Rogue / Untrusted CA & Certificate for Attack Simulation...")
    rogue_ca_key, rogue_ca_cert = build_ca("rogue_ca", "Hacker Syndicate CA")
    issue_certificate("rogue_device", rogue_ca_key, rogue_ca_cert, is_server=False)

    print("\n" + "=" * 65)
    print(f"[+] All certificates generated successfully in: {CERTS_DIR}")
    print("=" * 65)
    for fname in sorted(os.listdir(CERTS_DIR)):
        fpath = os.path.join(CERTS_DIR, fname)
        size = os.path.getsize(fpath)
        print(f"  - {fname:<22} ({size} bytes)")

if __name__ == "__main__":
    generate_all()
