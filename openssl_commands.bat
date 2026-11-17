@echo off
REM =========================================================================
REM  OpenSSL CLI Commands for Mutual TLS (mTLS) IoT Architecture
REM  Course: Cyber Security Lab (7CS4-22 / 7CIT4-22) - Project CSL-I11
REM =========================================================================

echo [1/5] Generating Root CA Key and Self-Signed Certificate...
openssl genrsa -out ca.key 2048
openssl req -x509 -new -nodes -key ca.key -sha256 -days 3650 -out ca.crt -subj "/C=IN/ST=Rajasthan/L=Jaipur/O=SKIT CyberSec Lab/OU=Root CA/CN=IoT-Root-CA"

echo [2/5] Generating Gateway Server Key and CSR...
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr -subj "/C=IN/ST=Rajasthan/L=Jaipur/O=SKIT CyberSec Lab/OU=Gateway/CN=localhost"

echo [3/5] Signing Server Certificate with SAN (Subject Alternative Name)...
echo subjectAltName = @alt_names > server_ext.cnf
echo [alt_names] >> server_ext.cnf
echo DNS.1 = localhost >> server_ext.cnf
echo IP.1 = 127.0.0.1 >> server_ext.cnf
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 365 -sha256 -extfile server_ext.cnf

echo [4/5] Generating IoT Device 01 Key and Certificate...
openssl genrsa -out device01.key 2048
openssl req -new -key device01.key -out device01.csr -subj "/C=IN/ST=Rajasthan/L=Jaipur/O=SKIT CyberSec Lab/OU=Edge Devices/CN=device01"
openssl x509 -req -in device01.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out device01.crt -days 365 -sha256

echo [5/5] Generating Rogue/Attacker Certificate with Fake CA...
openssl genrsa -out rogue_ca.key 2048
openssl req -x509 -new -nodes -key rogue_ca.key -sha256 -days 365 -out rogue_ca.crt -subj "/C=RU/O=Hacker Syndicate/CN=Fake-Root-CA"
openssl genrsa -out rogue_device.key 2048
openssl req -new -key rogue_device.key -out rogue_device.csr -subj "/C=RU/O=Hacker Syndicate/CN=rogue_device"
openssl x509 -req -in rogue_device.csr -CA rogue_ca.crt -CAkey rogue_ca.key -CAcreateserial -out rogue_device.crt -days 365 -sha256

echo [+] OpenSSL Certificate Generation Complete!
