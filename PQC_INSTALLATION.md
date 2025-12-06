# Post-Quantum Certificate Converter - Installation Guide

## Overview

The PQC Converter (`pdc_converter.py`) is a Streamlit application that converts standard SSL certificates to **Post-Quantum Cryptography (PQC)** certificates using NIST-standardized algorithms.

## Requirements

- Python 3.8 or higher
- pip (Python package installer)

## Installation

### 1. Install Dependencies

All required packages are listed in `requirements.txt`. Install them using:

```bash
pip install -r requirements.txt
```

The main dependencies are:
- **streamlit** - Web application framework
- **cryptography** - For parsing standard SSL certificates
- **pqcrypto** - NIST-standardized post-quantum cryptography library

### 2. Verify Installation

Test that the libraries are properly installed:

```bash
python3 -c "import pqcrypto.sign.ml_dsa_65; print('PQC library installed successfully')"
```

## Running the Application

Start the Streamlit application:

```bash
streamlit run pdc_converter.py
```

Or use the provided run script:

```bash
bash run_app.sh
```

The application will open in your default web browser at `http://localhost:8501`.

## Supported PQC Algorithms

The converter supports the following NIST-standardized post-quantum algorithms:

### ML-DSA (Module-Lattice-Based Digital Signature Algorithm)
- **ML-DSA-65 (Dilithium3)** - Security Level 3 (~AES-192)
- **ML-DSA-87 (Dilithium5)** - Security Level 5 (~AES-256)

### SLH-DSA (Stateless Hash-Based Digital Signature Algorithm)
- **SLH-DSA-SHA2-128f (SPHINCS+)** - Security Level 1 (~AES-128)

## Usage

1. **Upload Certificate**: Upload your existing SSL certificate (.pem or .crt file)
2. **Upload Private Key**: Upload the corresponding private key (.key or .pem file)
3. **Select Algorithm**: Choose a post-quantum algorithm from the dropdown
4. **Generate**: Click the "Generate PQC Certificate" button
5. **Download**: Download both the PQC certificate and private key

## Creating Test Certificates

For testing purposes, you can create a self-signed certificate using OpenSSL:

```bash
openssl req -x509 -newkey rsa:2048 -nodes \
  -keyout test_key.pem -out test_cert.pem -days 365 \
  -subj "/CN=example.com/O=Test Organization"
```

## Features

- ✅ Parses existing SSL certificates to extract Subject and SANs
- ✅ Generates PQC key pairs using NIST-standardized algorithms
- ✅ Creates self-signed PQC certificates
- ✅ Displays step-by-step progress during conversion
- ✅ Shows certificate details (Subject, SANs, validity period)
- ✅ Provides downloadable PQC certificate and private key files
- ✅ Comprehensive error handling and user feedback

## Security Considerations

- **Private Key Security**: Always keep your PQC private keys secure
- **Never commit** private keys to version control
- **Store securely**: Use proper key management systems in production
- **Quantum-Resistant**: These certificates use algorithms designed to be secure against quantum computer attacks

## Troubleshooting

### ImportError: No module named 'pqcrypto'

Install the required dependencies:
```bash
pip install -r requirements.txt
```

### Certificate Parsing Errors

Ensure your certificate file is in PEM format and not encrypted. The file should start with:
```
-----BEGIN CERTIFICATE-----
```

### Missing Dependencies

If you encounter any missing dependency errors, try upgrading pip and reinstalling:
```bash
pip install --upgrade pip
pip install -r requirements.txt --upgrade
```

## Technical Details

### PQCrypto Library

The application uses the `pqcrypto` Python library, which provides pure Python implementations of NIST-standardized post-quantum cryptography algorithms. This library is:

- ✅ Pure Python (no complex system dependencies)
- ✅ Cross-platform compatible
- ✅ Based on PQClean reference implementations
- ✅ Implements NIST-standardized algorithms

### Certificate Format

The generated PQC certificates are text-based files containing:
- Algorithm information
- Security level
- Subject details from the original certificate
- Subject Alternative Names (SANs)
- Validity period
- Public key (Base64 encoded)
- Digital signature (Base64 encoded)

## References

- [NIST Post-Quantum Cryptography](https://csrc.nist.gov/projects/post-quantum-cryptography)
- [PQCrypto Library](https://github.com/PQClean/PQClean)
- [Cryptography Library](https://pyca.github.io/cryptography/)

## License

This tool is provided as-is for educational and testing purposes.
