"""
Cryptographic Utilities for Digital Signatures and Payload Integrity
=====================================================================
Course: Cyber Security Lab (7CS4-22 / 7CIT4-22)
Experiment Link: Exp 8 - Secure Storage, Transmission & Digital Signature

This module implements:
- RSA-SHA256 Digital Signatures on IoT sensor payloads
- Digital Signature Verification using the sender's public key (from X.509 cert)
- Cryptographic hash (SHA-256) digest verification
"""

import json
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography import x509

def sign_payload(payload_dict: dict, private_key_pem_bytes: bytes) -> str:
    """
    Computes RSA-SHA256 digital signature over canonical JSON payload.
    Returns base64-encoded signature.
    """
    private_key = serialization.load_pem_private_key(
        private_key_pem_bytes,
        password=None
    )
    # Serialize canonical JSON (sorted keys, no extra whitespace)
    canonical_data = json.dumps(payload_dict, sort_keys=True).encode('utf-8')
    
    signature = private_key.sign(
        canonical_data,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode('utf-8')

def verify_signature(payload_dict: dict, signature_b64: str, certificate_pem_bytes: bytes) -> bool:
    """
    Verifies RSA-SHA256 digital signature using the public key from the device's X.509 certificate.
    """
    try:
        cert = x509.load_pem_x509_certificate(certificate_pem_bytes)
        public_key = cert.public_key()
        
        canonical_data = json.dumps(payload_dict, sort_keys=True).encode('utf-8')
        signature_bytes = base64.b64decode(signature_b64)
        
        public_key.verify(
            signature_bytes,
            canonical_data,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True
    except Exception as e:
        return False
