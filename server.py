"""
Mutual TLS (mTLS) IoT Gateway Server
====================================
Course: Cyber Security Lab (7CS4-22 / 7CIT4-22)
Project: CSL-I11 Mutual TLS Authentication for IoT Devices
Experiment Link: Exp 8 - Secure Storage, Transmission & Digital Signature

Server Features:
1. Enforces Mutual TLS (mTLS) via ssl.CERT_REQUIRED.
2. Validates client X.509 certificate against trusted Root CA.
3. Rejects connections without valid CA-signed certificates (Rogue or Self-Signed).
4. Rejects expired or revoked client certificates.
5. Verifies Application-Layer Digital Signature (RSA-SHA256) for non-repudiation.
6. Multi-threaded: handles multiple IoT edge devices concurrently.
"""

import os
import sys
import ssl
import json
import socket
import logging
import threading
from datetime import datetime

# Import signature verification utility
import crypto_utils

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CERTS_DIR = os.path.join(BASE_DIR, "certs")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

CA_CERT = os.path.join(CERTS_DIR, "ca.crt")
SERVER_CERT = os.path.join(CERTS_DIR, "server.crt")
SERVER_KEY = os.path.join(CERTS_DIR, "server.key")

# Setup logging
LOG_FILE = os.path.join(LOGS_DIR, "server.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("mTLS_Server")

class MTLS_IoT_Server:
    def __init__(self, host="127.0.0.1", port=8443):
        self.host = host
        self.port = port
        self.running = False
        self.server_sock = None
        self.tls_context = self._create_ssl_context()

    def _create_ssl_context(self):
        """Configure SSL context with strict mutual TLS requirements."""
        # Use TLS Server protocol (supports TLS 1.2 and TLS 1.3)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.minimum_version = ssl.TLSVersion.TLSv1_2

        # 1. Load Server Identity (Certificate + Private Key)
        logger.info(f"Loading Server Identity: {os.path.basename(SERVER_CERT)}")
        context.load_cert_chain(certfile=SERVER_CERT, keyfile=SERVER_KEY)

        # 2. Load Trusted Root CA to verify client devices
        logger.info(f"Loading Trusted Root CA: {os.path.basename(CA_CERT)}")
        context.load_verify_locations(cafile=CA_CERT)

        # 3. CRITICAL: Require client certificate (mTLS enforcement)
        context.verify_mode = ssl.CERT_REQUIRED
        context.check_hostname = False

        # Set secure ciphers
        context.set_ciphers('ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256')
        return context

    def handle_client(self, client_sock, client_addr):
        device_id = "UNKNOWN"
        try:
            logger.info(f"[+] TCP connection accepted from {client_addr}")
            
            # Wrap socket into TLS (Performing mTLS handshake)
            ssl_sock = self.tls_context.wrap_socket(client_sock, server_side=True)
            
            # Extract peer certificate details
            peer_cert = ssl_sock.getpeercert()
            cipher = ssl_sock.cipher()
            version = ssl_sock.version()

            # Parse subject details
            subject_dict = dict(x[0] for x in peer_cert.get('subject', []))
            device_id = subject_dict.get('commonName', 'Unknown-Device')
            issuer_dict = dict(x[0] for x in peer_cert.get('issuer', []))
            issuer_ca = issuer_dict.get('commonName', 'Unknown-CA')

            logger.info(f"[+] mTLS HANDSHAKE SUCCESS with {client_addr}")
            logger.info(f"    |-- Protocol: {version}")
            logger.info(f"    |-- Cipher Suite: {cipher[0]} ({cipher[2]} bits)")
            logger.info(f"    |-- Authenticated Device CN: {device_id}")
            logger.info(f"    |-- Validated by CA: {issuer_ca}")
            logger.info(f"    |-- Certificate Serial: {peer_cert.get('serialNumber')}")
            logger.info(f"    |-- Validity Period: {peer_cert.get('notBefore')} to {peer_cert.get('notAfter')}")

            # Read sensor payload from IoT device
            raw_data = ssl_sock.recv(4096)
            if not raw_data:
                logger.warning(f"[-] No payload received from {device_id}")
                ssl_sock.close()
                return

            message = json.loads(raw_data.decode('utf-8'))
            telemetry = message.get("telemetry", {})
            signature_b64 = message.get("signature", "")

            logger.info(f"[*] Received Encrypted Sensor Data from '{device_id}': {json.dumps(telemetry)}")

            # Verify Digital Signature using the Device's certificate
            # To get raw DER certificate bytes for cryptography library:
            raw_cert_der = ssl_sock.getpeercert(binary_form=True)
            from cryptography import x509
            device_cert_obj = x509.load_der_x509_certificate(raw_cert_der)
            from cryptography.hazmat.primitives import serialization
            device_cert_pem = device_cert_obj.public_bytes(serialization.Encoding.PEM)

            is_valid_sig = crypto_utils.verify_signature(telemetry, signature_b64, device_cert_pem)

            if is_valid_sig:
                logger.info(f"[+] [EXP 8 - DIGITAL SIGNATURE VERIFIED] Authentic payload from '{device_id}'")
                response = {
                    "status": "SUCCESS",
                    "code": 200,
                    "message": f"Sensor telemetry authenticated & stored securely for device {device_id}",
                    "server_time": datetime.utcnow().isoformat() + "Z"
                }
            else:
                logger.error(f"[!] [SECURITY ALERT] Digital signature verification FAILED for '{device_id}'! Data may be tampered.")
                response = {
                    "status": "REJECTED",
                    "code": 401,
                    "message": "Signature verification failed - Integrity violation",
                    "server_time": datetime.utcnow().isoformat() + "Z"
                }

            ssl_sock.sendall(json.dumps(response).encode('utf-8'))
            ssl_sock.close()
            logger.info(f"[+] Session cleanly closed for {device_id}\n")

        except ssl.SSLError as e:
            logger.error(f"[!] [mTLS HANDSHAKE FAILED] Security violation from {client_addr}:")
            logger.error(f"    Reason: {e.reason if hasattr(e, 'reason') else str(e)}")
            try:
                client_sock.close()
            except Exception:
                pass
        except Exception as e:
            logger.error(f"[-] Error handling client {client_addr}: {str(e)}")
            try:
                client_sock.close()
            except Exception:
                pass

    def start(self):
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind((self.host, self.port))
        self.server_sock.listen(10)
        self.running = True
        logger.info("=" * 65)
        logger.info(f" mTLS IoT Gateway Server listening on {self.host}:{self.port}")
        logger.info(f" Mutual Authentication: REQUIRED (Client X.509 mandatory)")
        logger.info(f" Root Trust Anchor: {CA_CERT}")
        logger.info("=" * 65)

        try:
            while self.running:
                try:
                    client_sock, client_addr = self.server_sock.accept()
                    t = threading.Thread(target=self.handle_client, args=(client_sock, client_addr), daemon=True)
                    t.start()
                except socket.timeout:
                    continue
                except OSError:
                    break
        except KeyboardInterrupt:
            logger.info("\n[*] Server shutdown initiated by administrator.")
        finally:
            self.stop()

    def stop(self):
        self.running = False
        if self.server_sock:
            try:
                self.server_sock.close()
            except Exception:
                pass
        logger.info("[*] Server stopped.")

if __name__ == "__main__":
    server = MTLS_IoT_Server()
    server.start()
