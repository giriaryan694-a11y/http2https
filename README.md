# http2https 🚀

**Made by Aryan Giri**

`http2https` is a Python-based CLI tool that helps you access an HTTP-only local service through HTTPS.

It is useful when a browser, client, or tool expects a secure `https://` address, but your actual service is still running on plain HTTP.

---

## What it does

Your service runs locally on HTTP, for example:

```text
HTTP server:  localhost:8000
```

Then `http2https` runs an HTTPS proxy, for example:

```text
HTTPS proxy:  localhost:8080
```

So instead of opening:

```text
http://IP:8000
```

you open:

```text
https://IP:8080
```

The tool accepts the secure connection, decrypts it locally, forwards the request to your HTTP server, and sends the response back to the client.

---

## Why this is useful

Some tools and browsers expect HTTPS by default, even when the backend service itself only speaks HTTP. This tool helps in situations like:

* local development servers
* internal dashboards
* AI tools running on HTTP
* cybersec tools and lab panels
* browser testing on modern HTTPS-only environments

---

## Features

* automatic TLS certificate generation
* Subject Alternative Names support
* CA-style certificate flags for browser compatibility
* custom certificate title
* reuse or regenerate existing certificates
* reverse proxy from HTTPS to HTTP
* simple CLI experience
* designed for local use

---

## Installation

### Clone the repository

```bash
git clone https://github.com/giriaryan694-a11y/http2https
cd http2https
```

### Standard Python installation

```bash
pip install cryptography pyfiglet termcolor colorama requests
```

### Termux installation

If you are using Termux, do **not** install `cryptography` with `pip` first. Use the Termux package instead to avoid build errors.

```bash
pkg update && pkg upgrade
pkg install python python-cryptography
pip install pyfiglet termcolor colorama requests
```

---

## Usage

1. Start your local HTTP server.

Example:

```bash
python -m http.server 8000
```

2. Run the tool.

```bash
python main.py
```

3. Enter the requested details.

Typical values:

* **Certificate Title**: `MyDevCA`
* **Domains / IPs**: `localhost, 127.0.0.1, 10.192.37.173`
* **Internal Port**: `8000`
* **HTTPS Port**: `8080`

4. Open the HTTPS proxy in your browser.

Example:

```text
https://127.0.0.1:8080
```

---

## Trusting the certificate

To avoid browser certificate warnings, install the generated certificate as a trusted root certificate on your system.

### Windows

1. Open the generated certificate file.
2. Click **Install Certificate**.
3. Choose **Current User**.
4. Select **Place all certificates in the following store**.
5. Choose **Trusted Root Certification Authorities**.
6. Finish the wizard.
7. Restart your browser.

### Linux

Install the certificate into your system trust store using your distro’s certificate management method.

### Android

Import the certificate through the device security settings if your device supports user certificate installation.

---

## Notes

* This tool is intended for local or authorized development use.
* Keep the certificate and proxy endpoint private.
* If you change domains or IPs, regenerate the certificate.
* The proxy only bridges HTTPS to an HTTP backend; it does not turn the backend itself into an HTTPS server.

---

## Example flow

```text
Browser / Client
        ↓ HTTPS
http2https proxy on 8080
        ↓ HTTP
Local service on 8000
```

---

## Author

**Aryan Giri**

---

## License

This project is licensed under the **Apache License 2.0**.
