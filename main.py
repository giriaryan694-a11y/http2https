import os
import ssl
import http.server
import ipaddress
import datetime
import requests
import pyfiglet
import colorama
from termcolor import colored
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes

# Initialize colorama for Windows compatibility
colorama.init()

# Global variable to store the target HTTP port for the proxy handler
TARGET_PORT = 80
CERT_DIR = "browser_cert"

def print_banner():
    """Prints the stylish CLI banner."""
    os.system('cls' if os.name == 'nt' else 'clear')
    banner = pyfiglet.figlet_format("http2https", font="slant")
    print(colored(banner, "cyan", attrs=["bold"]))
    print(colored("                               Made By Aryan Giri", "green", attrs=["bold"]))
    print(colored("="*60, "magenta"))
    print()

def generate_cert(domains, cert_file, key_file, cert_title):
    """Generates a modern self-signed CA certificate with a custom title and SANs."""
    os.makedirs(os.path.dirname(cert_file), exist_ok=True)

    if os.path.exists(cert_file): os.remove(cert_file)
    if os.path.exists(key_file): os.remove(key_file)

    print(colored("[*] Generating 2048-bit RSA private key...", "yellow"))
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    # NEW: Apply the custom user title to the Organization and Common Name
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, cert_title),
        x509.NameAttribute(NameOID.COMMON_NAME, cert_title),
    ])

    sans = []
    for d in domains:
        try:
            ip = ipaddress.ip_address(d)
            sans.append(x509.IPAddress(ip))
        except ValueError:
            sans.append(x509.DNSName(d))

    print(colored(f"[*] Generating x509 Certificate for: {', '.join(domains)}...", "yellow"))
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.now(datetime.timezone.utc)
    ).not_valid_after(
        datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName(sans),
        critical=False,
    ).add_extension(
        x509.BasicConstraints(ca=True, path_length=None),
        critical=True,
    ).add_extension(
        x509.KeyUsage(
            digital_signature=True,
            content_commitment=False,
            key_encipherment=True,
            data_encipherment=False,
            key_agreement=False,
            key_cert_sign=True,
            crl_sign=False,
            encipher_only=False,
            decipher_only=False,
        ),
        critical=True,
    ).add_extension(
        x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]),
        critical=False,
    ).sign(key, hashes.SHA256())

    with open(key_file, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))

    with open(cert_file, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    print(colored(f"[+] Certificate '{cert_title}' generated successfully! Saved in ./{CERT_DIR}/", "green"))


class ProxyHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    """Handles incoming HTTPS requests and forwards them to the local HTTP server."""
    def do_proxy(self):
        url = f"http://127.0.0.1:{TARGET_PORT}{self.path}"
        req_headers = {key: val for key, val in self.headers.items() if key.lower() != 'host'}
        req_headers['Host'] = f"127.0.0.1:{TARGET_PORT}"
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else None

        try:
            response = requests.request(
                method=self.command, url=url, headers=req_headers,
                data=body, allow_redirects=False, stream=True
            )
            self.send_response(response.status_code)
            for key, val in response.headers.items():
                if key.lower() not in ['transfer-encoding', 'content-encoding']: 
                    self.send_header(key, val)
            self.end_headers()
            self.wfile.write(response.raw.read())
        except requests.exceptions.RequestException as e:
            self.send_error(502, f"Bad Gateway: Unable to reach internal server at port {TARGET_PORT}. Error: {e}")

    def do_GET(self): self.do_proxy()
    def do_POST(self): self.do_proxy()
    def do_PUT(self): self.do_proxy()
    def do_DELETE(self): self.do_proxy()
    def do_HEAD(self): self.do_proxy()
    def do_OPTIONS(self): self.do_proxy()
    def do_PATCH(self): self.do_proxy()

def main():
    global TARGET_PORT
    print_banner()

    cert_file = os.path.join(CERT_DIR, "cert.crt")
    key_file = os.path.join(CERT_DIR, "key.pem")
    regenerate_certs = True

    if os.path.exists(cert_file) and os.path.exists(key_file):
        print(colored(f"[!] Found existing certificates in ./{CERT_DIR}/", "yellow", attrs=["bold"]))
        choice = input(colored("[?] Do you want to delete them and generate new ones? (Y/N): ", "cyan")).strip().lower()
        if choice == 'n': regenerate_certs = False
    
    print("-" * 60)

    if regenerate_certs:
        # NEW: Ask for the Certificate Title
        cert_title = input(colored("[?] Enter a Title/Name for the Certificate (e.g., Aryan Local Dev CA): ", "cyan")).strip()
        if not cert_title:
            cert_title = "http2https Local CA"

        domains_input = input(colored("[?] Enter domains/IPs to secure (comma separated, e.g., localhost, 127.0.0.1): ", "cyan"))
        domains = ["localhost", "127.0.0.1"] if not domains_input.strip() else [d.strip() for d in domains_input.split(',')]
            
    try:
        if regenerate_certs or 'TARGET_PORT' not in globals():
             TARGET_PORT = int(input(colored("[?] Enter the port your internal HTTP server is running on (e.g., 8080): ", "cyan")))
             listen_port = int(input(colored("[?] Enter the port to run this HTTPS proxy on (e.g., 443): ", "cyan")))
    except ValueError:
        print(colored("[-] Invalid port number! Please enter numbers only.", "red"))
        return

    if regenerate_certs:
        print("-" * 60)
        # NEW: Pass the title to the generator
        generate_cert(domains, cert_file, key_file, cert_title)
        print("-" * 60)

    server_address = ('0.0.0.0', listen_port)
    httpd = http.server.HTTPServer(server_address, ProxyHTTPRequestHandler)

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    try:
        context.load_cert_chain(certfile=cert_file, keyfile=key_file)
    except Exception as e:
        print(colored(f"[-] Error loading certificates: {e}", "red"))
        return
        
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    print()
    print(colored(f"[🚀] http2https server is now running on https://localhost:{listen_port}", "green", attrs=["bold"]))
    print(colored(f"[🔄] Forwarding all traffic to http://127.0.0.1:{TARGET_PORT}", "green"))
    print(colored("[!] Press Ctrl+C to stop.", "yellow"))
    print()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n" + colored("[*] Shutting down http2https...", "red"))
        httpd.server_close()

if __name__ == '__main__':
    main()
