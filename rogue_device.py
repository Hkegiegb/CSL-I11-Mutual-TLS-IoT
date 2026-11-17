"""
Attack & Negative Test Suite: Rogue Device Simulations
=======================================================
Course: Cyber Security Lab (7CS4-22 / 7CIT4-22)
Project: CSL-I11 Mutual TLS Authentication for IoT Devices
Experiment Link: Exp 8 - Secure Storage, Transmission & Digital Signature

Simulates 4 Common IoT Cyber Attacks:
------------------------------------
Test 1: Unauthenticated Client (Connects without presenting any client certificate)
Test 2: Rogue / Impersonating Device (Presents certificate signed by an untrusted Root CA)
Test 3: Expired Device Certificate (Presents certificate past its validity period)
Test 4: Data Tampering / Man-in-the-Middle (Payload altered after digital signing)
"""

import os
import ssl
import sys
import json
import socket
from datetime import datetime

import crypto_utils
import iot_device

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CERTS_DIR = os.path.join(BASE_DIR, "certs")
CA_CERT = os.path.join(CERTS_DIR, "ca.crt")

def attack_no_certificate(host="127.0.0.1", port=8443):
    """Attempt connection without providing any client certificate."""
    print("\n" + "=" * 65)
    print(" [ATTACK 1] Unauthenticated Connection Attempt (No Client Certificate)")
    print("=" * 65)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_verify_locations(cafile=CA_CERT)
    context.check_hostname = False
    # Notice: context.load_cert_chain is NOT called!

    try:
        raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_sock.connect((host, port))
        ssl_sock = context.wrap_socket(raw_sock, server_hostname=host)
        # Flush handshake exchange to receive server alert if client cert was missing
        ssl_sock.sendall(b"TEST_PING")
        ssl_sock.recv(1024)
        print("[-] VULNERABILITY DETECTED: Server accepted connection without client certificate!")
        ssl_sock.close()
        return False
    except ssl.SSLError as e:
        print(f"[+] DEFENSE ACTIVE: Handshake rejected by server as expected!")
        print(f"    SSL Error: {e.reason if hasattr(e, 'reason') else e}")
        return True
    except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, OSError) as e:
        print(f"[+] DEFENSE ACTIVE: Server terminated connection because client certificate was omitted: {e}")
        return True
    except Exception as e:
        print(f"[+] DEFENSE ACTIVE: Connection aborted: {e}")
        return True

def attack_untrusted_ca(host="127.0.0.1", port=8443):
    """Attempt connection presenting a certificate signed by an unauthorized Rogue CA."""
    print("\n" + "=" * 65)
    print(" [ATTACK 2] Rogue Device Attack (Certificate from Untrusted CA)")
    print("=" * 65)
    cert_file = os.path.join(CERTS_DIR, "rogue_device.crt")
    key_file = os.path.join(CERTS_DIR, "rogue_device.key")

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_verify_locations(cafile=CA_CERT)
    context.check_hostname = False
    context.load_cert_chain(certfile=cert_file, keyfile=key_file)

    try:
        raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_sock.connect((host, port))
        ssl_sock = context.wrap_socket(raw_sock, server_hostname=host)
        # Flush handshake exchange (TLS 1.3 alert detection)
        ssl_sock.sendall(b"TEST_PING")
        ssl_sock.recv(1024)
        print("[-] VULNERABILITY DETECTED: Rogue device was improperly authenticated!")
        ssl_sock.close()
        return False
    except ssl.SSLError as e:
        print(f"[+] DEFENSE ACTIVE: Gateway server rejected untrusted Rogue CA certificate!")
        print(f"    SSL Error: {e.reason if hasattr(e, 'reason') else e}")
        return True
    except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, OSError) as e:
        print(f"[+] DEFENSE ACTIVE: Server terminated connection due to invalid certificate: {e}")
        return True
    except Exception as e:
        print(f"[+] DEFENSE ACTIVE: Connection dropped: {e}")
        return True

def attack_expired_certificate(host="127.0.0.1", port=8443):
    """Attempt connection with an expired X.509 certificate."""
    print("\n" + "=" * 65)
    print(" [ATTACK 3] Stale / Deprecated Device Attack (Expired Certificate)")
    print("=" * 65)
    cert_file = os.path.join(CERTS_DIR, "expired_device.crt")
    key_file = os.path.join(CERTS_DIR, "expired_device.key")

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_verify_locations(cafile=CA_CERT)
    context.check_hostname = False
    context.load_cert_chain(certfile=cert_file, keyfile=key_file)

    try:
        raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_sock.connect((host, port))
        ssl_sock = context.wrap_socket(raw_sock, server_hostname=host)
        # Flush handshake exchange (TLS 1.3 alert detection)
        ssl_sock.sendall(b"TEST_PING")
        ssl_sock.recv(1024)
        print("[-] VULNERABILITY DETECTED: Expired certificate was accepted!")
        ssl_sock.close()
        return False
    except ssl.SSLError as e:
        print(f"[+] DEFENSE ACTIVE: Gateway server blocked expired device certificate!")
        print(f"    SSL Error: {e.reason if hasattr(e, 'reason') else e}")
        return True
    except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, OSError) as e:
        print(f"[+] DEFENSE ACTIVE: Server terminated connection due to expired certificate: {e}")
        return True
    except Exception as e:
        print(f"[+] DEFENSE ACTIVE: Connection blocked: {e}")
        return True

def attack_tampered_payload(host="127.0.0.1", port=8443):
    """Attempt data tampering (Exp 8 - Digital Signature violation)."""
    print("\n" + "=" * 65)
    print(" [ATTACK 4] Data Tampering / Integrity Violation (Modified Payload)")
    print("=" * 65)
    # Uses valid cert to establish mTLS, but tampers with data before sending
    success = iot_device.run_iot_device(device_name="device01", host=host, port=port, tamper_data=True)
    return success

if __name__ == "__main__":
    print("Select Attack Test:")
    print("1: No Client Certificate")
    print("2: Rogue / Untrusted CA Certificate")
    print("3: Expired Certificate")
    print("4: Tampered Payload (Digital Signature Check)")
    choice = input("Enter option (1-4) or press Enter to run all: ").strip()

    if choice == "1":
        attack_no_certificate()
    elif choice == "2":
        attack_untrusted_ca()
    elif choice == "3":
        attack_expired_certificate()
    elif choice == "4":
        attack_tampered_payload()
    else:
        attack_no_certificate()
        attack_untrusted_ca()
        attack_expired_certificate()
        attack_tampered_payload()
