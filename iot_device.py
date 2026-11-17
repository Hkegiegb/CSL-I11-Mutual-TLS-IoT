"""
Legitimate IoT Device Client (mTLS Authenticated)
=================================================
Course: Cyber Security Lab (7CS4-22 / 7CIT4-22)
Project: CSL-I11 Mutual TLS Authentication for IoT Devices
Experiment Link: Exp 8 - Secure Storage, Transmission & Digital Signature

This device:
1. Presents its individual X.509 certificate & private key to the server.
2. Authenticates the gateway server's certificate against the trusted Root CA.
3. Digitally signs telemetry data (RSA-SHA256) prior to transmission.
4. Transmits encrypted sensor data over the established TLS tunnel.
"""

import os
import sys
import ssl
import json
import time
import socket
import random
from datetime import datetime

import crypto_utils

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CERTS_DIR = os.path.join(BASE_DIR, "certs")

def run_iot_device(device_name="device01", host="127.0.0.1", port=8443, tamper_data=False):
    cert_file = os.path.join(CERTS_DIR, f"{device_name}.crt")
    key_file = os.path.join(CERTS_DIR, f"{device_name}.key")
    ca_file = os.path.join(CERTS_DIR, "ca.crt")

    if not os.path.exists(cert_file) or not os.path.exists(key_file):
        print(f"[-] Error: Certificate or key file not found for '{device_name}' in {CERTS_DIR}")
        return False

    print("=" * 65)
    print(f"[*] Initializing IoT Device Node: {device_name}")
    print(f"[*] Certificate: {os.path.basename(cert_file)}")
    print(f"[*] Private Key: {os.path.basename(key_file)}")
    print("=" * 65)

    # 1. Setup SSL Context for client
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.minimum_version = ssl.TLSVersion.TLSv1_2

    # Verify Server's certificate against Root CA
    context.load_verify_locations(cafile=ca_file)
    context.verify_mode = ssl.CERT_REQUIRED
    context.check_hostname = False  # Set to True in production DNS, False for IP/localhost demo

    # Present Device Certificate & Key for Mutual Authentication
    context.load_cert_chain(certfile=cert_file, keyfile=key_file)

    try:
        raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"[*] Connecting to IoT Gateway Server at {host}:{port}...")
        raw_sock.connect((host, port))

        # Perform mTLS Handshake
        ssl_sock = context.wrap_socket(raw_sock, server_hostname=host)
        print(f"[+] mTLS Handshake SUCCESSFUL!")
        print(f"    |-- Protocol: {ssl_sock.version()}")
        print(f"    |-- Cipher: {ssl_sock.cipher()[0]}")

        # Server certificate verification details
        server_cert = ssl_sock.getpeercert()
        server_cn = dict(x[0] for x in server_cert.get('subject', [])).get('commonName')
        print(f"    |-- Verified Gateway Identity: {server_cn}")

        # 2. Generate Sensor Telemetry
        telemetry = {
            "device_id": device_name,
            "sensor_type": "Environmental_Monitor_v2",
            "temperature_celsius": round(24.0 + random.uniform(-2.5, 5.0), 2),
            "humidity_percent": round(55.0 + random.uniform(-5.0, 15.0), 1),
            "battery_voltage": round(3.7 + random.uniform(-0.2, 0.4), 2),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        print(f"\n[*] Generated Sensor Readings:\n    {json.dumps(telemetry, indent=4)}")

        # 3. Read Device Private Key for Digital Signature (Exp 8)
        with open(key_file, "rb") as kf:
            priv_key_pem = kf.read()

        signature = crypto_utils.sign_payload(telemetry, priv_key_pem)
        print(f"[+] [EXP 8 - DIGITAL SIGNATURE GENERATED] (RSA-SHA256): {signature[:32]}...")

        # If testing tampering attack:
        if tamper_data:
            print("[!] TAMPERING ATTACK: Modifying temperature reading after signing...")
            telemetry["temperature_celsius"] = 999.9  # Malicious alteration

        message = {
            "telemetry": telemetry,
            "signature": signature
        }

        # 4. Transmit encrypted data over mTLS
        print("[*] Transmitting encrypted payload across mTLS tunnel...")
        ssl_sock.sendall(json.dumps(message).encode('utf-8'))

        # 5. Receive Server Response
        resp_data = ssl_sock.recv(4096)
        if resp_data:
            response = json.loads(resp_data.decode('utf-8'))
            print(f"[+] Gateway Response Received:\n    {json.dumps(response, indent=4)}")

        ssl_sock.close()
        print(f"[+] Secure communication completed for {device_name}.\n")
        return True

    except ssl.SSLError as e:
        print(f"[!] TLS Error: {e}")
        return False
    except Exception as e:
        print(f"[-] Connection Error: {e}")
        return False

if __name__ == "__main__":
    dev_name = sys.argv[1] if len(sys.argv) > 1 else "device01"
    run_iot_device(dev_name)
