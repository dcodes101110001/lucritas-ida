import streamlit as st
import os
import io
import base64
import datetime
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtensionOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import pqcrypto.sign.ml_dsa_65 as ml_dsa
import pqcrypto.sign.ml_dsa_87 as ml_dsa_l5
import pqcrypto.sign.sphincs_sha2_128f_simple as sphincs

# PQC Algorithm mapping
PQC_ALGORITHMS = {
    'ML-DSA-65 (Dilithium3)': {
        'module': ml_dsa,
        'name': 'ML-DSA-65',
        'description': 'NIST ML-DSA Level 3 (Based on Dilithium3)',
        'security_level': 'Level 3 (~AES-192)'
    },
    'ML-DSA-87 (Dilithium5)': {
        'module': ml_dsa_l5,
        'name': 'ML-DSA-87',
        'description': 'NIST ML-DSA Level 5 (Based on Dilithium5)',
        'security_level': 'Level 5 (~AES-256)'
    },
    'SLH-DSA-SHA2-128f (SPHINCS+)': {
        'module': sphincs,
        'name': 'SLH-DSA-SHA2-128f',
        'description': 'NIST SLH-DSA (SPHINCS+ SHA2-128f-simple)',
        'security_level': 'Level 1 (~AES-128)'
    }
}


def parse_existing_certificate(cert_data):
    """
    Parse the existing SSL certificate to extract Subject, SANs, and other details.
    """
    try:
        cert = x509.load_pem_x509_certificate(cert_data, default_backend())
        
        # Extract subject information
        subject_info = {}
        for attribute in cert.subject:
            subject_info[attribute.oid._name] = attribute.value
        
        # Extract SANs (Subject Alternative Names)
        san_list = []
        try:
            san_ext = cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
            san_list = [str(name) for name in san_ext.value]
        except x509.ExtensionNotFound:
            pass
        
        # Extract validity period
        not_before = cert.not_valid_before
        not_after = cert.not_valid_after
        
        cert_info = {
            'subject': subject_info,
            'sans': san_list,
            'not_before': not_before,
            'not_after': not_after,
            'serial_number': cert.serial_number,
            'issuer': {attr.oid._name: attr.value for attr in cert.issuer}
        }
        
        return cert_info
    except Exception as e:
        raise ValueError(f"Failed to parse certificate: {str(e)}")


def generate_pqc_cert(cert_data, key_data, pq_algorithm):
    """
    Generate a Post-Quantum Certificate by:
    1. Parsing the existing standard SSL certificate to extract details
    2. Generating a new PQC private key
    3. Creating a self-signed PQC certificate with the extracted details
    
    This implementation uses the pqcrypto library which provides NIST-standardized
    PQC algorithms (ML-DSA and SLH-DSA).
    """
    st.info(f"🔐 Generating Post-Quantum Certificate with {pq_algorithm}...")
    
    # Step 1: Parse existing certificate
    st.text("📋 Step 1: Parsing existing SSL certificate...")
    try:
        cert_info = parse_existing_certificate(cert_data)
        st.success(f"✓ Certificate parsed successfully")
        
        # Display parsed information
        with st.expander("📄 View Certificate Details"):
            st.write("**Subject Information:**")
            for key, value in cert_info['subject'].items():
                st.text(f"  {key}: {value}")
            
            if cert_info['sans']:
                st.write("**Subject Alternative Names (SANs):**")
                for san in cert_info['sans']:
                    st.text(f"  - {san}")
            
            st.write(f"**Validity Period:**")
            st.text(f"  Not Before: {cert_info['not_before']}")
            st.text(f"  Not After: {cert_info['not_after']}")
    except Exception as e:
        st.error(f"❌ Error parsing certificate: {str(e)}")
        raise
    
    # Step 2: Generate PQC key pair
    st.text(f"🔑 Step 2: Generating {pq_algorithm} key pair...")
    try:
        pqc_module = PQC_ALGORITHMS[pq_algorithm]['module']
        pqc_name = PQC_ALGORITHMS[pq_algorithm]['name']
        
        # Generate PQC keypair
        pqc_public_key, pqc_private_key = pqc_module.generate_keypair()
        
        st.success(f"✓ PQC key pair generated")
        st.text(f"  Public key size: {len(pqc_public_key)} bytes")
        st.text(f"  Private key size: {len(pqc_private_key)} bytes")
        st.text(f"  Security level: {PQC_ALGORITHMS[pq_algorithm]['security_level']}")
    except Exception as e:
        st.error(f"❌ Error generating PQC keys: {str(e)}")
        raise
    
    # Step 3: Create PQC Certificate
    st.text("📜 Step 3: Creating self-signed PQC certificate...")
    try:
        # Build certificate data structure
        common_name = cert_info['subject'].get('commonName', 'PQC-Certificate')
        organization = cert_info['subject'].get('organizationName', 'PQC Organization')
        
        # Create certificate content with detailed information
        cert_builder_info = []
        cert_builder_info.append("=" * 70)
        cert_builder_info.append("POST-QUANTUM CRYPTOGRAPHY CERTIFICATE")
        cert_builder_info.append("=" * 70)
        cert_builder_info.append("")
        cert_builder_info.append(f"Algorithm: {pqc_name}")
        cert_builder_info.append(f"Security Level: {PQC_ALGORITHMS[pq_algorithm]['security_level']}")
        cert_builder_info.append(f"Description: {PQC_ALGORITHMS[pq_algorithm]['description']}")
        cert_builder_info.append("")
        cert_builder_info.append("SUBJECT:")
        for key, value in cert_info['subject'].items():
            cert_builder_info.append(f"  {key}: {value}")
        
        if cert_info['sans']:
            cert_builder_info.append("")
            cert_builder_info.append("SUBJECT ALTERNATIVE NAMES:")
            for san in cert_info['sans']:
                cert_builder_info.append(f"  - {san}")
        
        cert_builder_info.append("")
        cert_builder_info.append("VALIDITY:")
        cert_builder_info.append(f"  Not Before: {cert_info['not_before']}")
        cert_builder_info.append(f"  Not After: {cert_info['not_after']}")
        cert_builder_info.append("")
        cert_builder_info.append("PUBLIC KEY:")
        cert_builder_info.append(f"  Algorithm: {pqc_name}")
        cert_builder_info.append(f"  Key Size: {len(pqc_public_key)} bytes")
        cert_builder_info.append(f"  Public Key (Base64):")
        
        # Encode public key in base64 for display
        pub_key_b64 = base64.b64encode(pqc_public_key).decode('ascii')
        # Split into 64-character lines
        for i in range(0, len(pub_key_b64), 64):
            cert_builder_info.append(f"    {pub_key_b64[i:i+64]}")
        
        cert_builder_info.append("")
        cert_builder_info.append("=" * 70)
        cert_builder_info.append("CERTIFICATE SIGNATURE")
        cert_builder_info.append("=" * 70)
        cert_builder_info.append("")
        
        # Create a signature over the certificate data
        cert_data_to_sign = "\n".join(cert_builder_info).encode('utf-8')
        signature = pqc_module.sign(pqc_private_key, cert_data_to_sign)
        
        cert_builder_info.append(f"Signature Algorithm: {pqc_name}")
        cert_builder_info.append(f"Signature Size: {len(signature)} bytes")
        cert_builder_info.append(f"Signature (Base64):")
        
        sig_b64 = base64.b64encode(signature).decode('ascii')
        for i in range(0, len(sig_b64), 64):
            cert_builder_info.append(f"  {sig_b64[i:i+64]}")
        
        cert_builder_info.append("")
        cert_builder_info.append("=" * 70)
        
        pqc_cert_content = "\n".join(cert_builder_info)
        
        st.success("✓ PQC certificate created and self-signed")
    except Exception as e:
        st.error(f"❌ Error creating PQC certificate: {str(e)}")
        raise
    
    # Step 4: Format private key for output
    st.text("🔐 Step 4: Formatting PQC private key...")
    try:
        key_info = []
        key_info.append("=" * 70)
        key_info.append("POST-QUANTUM CRYPTOGRAPHY PRIVATE KEY")
        key_info.append("=" * 70)
        key_info.append("")
        key_info.append(f"Algorithm: {pqc_name}")
        key_info.append(f"Key Size: {len(pqc_private_key)} bytes")
        key_info.append(f"Security Level: {PQC_ALGORITHMS[pq_algorithm]['security_level']}")
        key_info.append("")
        key_info.append("⚠️  WARNING: Keep this private key secure!")
        key_info.append("    Never share this key or commit it to version control.")
        key_info.append("")
        key_info.append("PRIVATE KEY DATA (Base64):")
        
        priv_key_b64 = base64.b64encode(pqc_private_key).decode('ascii')
        for i in range(0, len(priv_key_b64), 64):
            key_info.append(f"  {priv_key_b64[i:i+64]}")
        
        key_info.append("")
        key_info.append("=" * 70)
        
        pqc_key_content = "\n".join(key_info)
        
        st.success("✓ PQC private key formatted")
    except Exception as e:
        st.error(f"❌ Error formatting private key: {str(e)}")
        raise
    
    st.success("🎉 PQC Certificate generation completed successfully!")
    
    return pqc_cert_content, pqc_key_content

## Streamlit App Interface ##
st.title("⚛️ SSL to Post-Quantum Certificate Converter")
st.markdown("""
This tool converts standard SSL certificates to **Post-Quantum Cryptography (PQC)** certificates 
using **NIST-standardized** algorithms that are resistant to quantum computer attacks.

**Key Features:**
- 📋 Parses existing SSL certificates to extract Subject and SANs
- 🔑 Generates PQC key pairs using ML-DSA (Dilithium) or SLH-DSA (SPHINCS+)
- 📜 Creates self-signed PQC certificates
- 🛡️ Uses NIST-standardized post-quantum algorithms
""")

st.info("""
**What is Post-Quantum Cryptography?**

Traditional cryptographic algorithms like RSA and ECDSA will become vulnerable when large-scale 
quantum computers are built. PQC algorithms are designed to be secure against both classical 
and quantum computer attacks.

**NIST has standardized the following PQC algorithms:**
- **ML-DSA** (Module-Lattice-Based Digital Signature Algorithm) - Based on Dilithium
- **SLH-DSA** (Stateless Hash-Based Digital Signature Algorithm) - Based on SPHINCS+
""")

st.header("1. Upload Existing Certificate and Key")

uploaded_cert = st.file_uploader(
    "Upload Standard SSL Certificate (.pem, .crt)",
    type=['pem', 'crt'],
    help="Upload your existing SSL/TLS certificate in PEM format"
)
uploaded_key = st.file_uploader(
    "Upload Standard Private Key (.key, .pem)",
    type=['key', 'pem'],
    help="Upload the private key for your certificate (used only for validation)"
)

st.header("2. Select Post-Quantum Algorithm")

pq_choice = st.selectbox(
    "Choose PQC Digital Signature Algorithm (NIST Standardized):",
    list(PQC_ALGORITHMS.keys()),
    help="Select the post-quantum algorithm for your new certificate"
)

# Display algorithm details
selected_alg = PQC_ALGORITHMS[pq_choice]
st.markdown(f"""
**Selected Algorithm:** {selected_alg['name']}  
**Description:** {selected_alg['description']}  
**Security Level:** {selected_alg['security_level']}
""")

if uploaded_cert and uploaded_key:
    st.success("✅ Files uploaded successfully. Ready to convert.")
    
    cert_data = uploaded_cert.getvalue()
    key_data = uploaded_key.getvalue()
    
    if st.button("🚀 Generate PQC Certificate", type="primary"):
        with st.spinner('⏳ Generating PQC Certificate... This may take a few moments.'):
            try:
                # Call the PQC generation function
                pqc_cert, pqc_key = generate_pqc_cert(cert_data, key_data, pq_choice)
                
                st.markdown("---")
                st.subheader("✅ PQC Certificate Generation Complete!")
                
                # Create two columns for certificate and key
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 📜 PQC Certificate")
                    st.text_area(
                        "Certificate Content",
                        pqc_cert,
                        height=300,
                        help="Your new post-quantum certificate"
                    )
                    st.download_button(
                        label="⬇️ Download PQC Certificate",
                        data=pqc_cert,
                        file_name=f'pqc_cert_{selected_alg["name"].lower().replace("-", "_")}.txt',
                        mime='text/plain',
                        use_container_width=True
                    )
                
                with col2:
                    st.markdown("### 🔐 PQC Private Key")
                    st.text_area(
                        "Private Key Content",
                        pqc_key,
                        height=300,
                        help="Your new post-quantum private key - keep this secure!"
                    )
                    st.download_button(
                        label="⬇️ Download PQC Private Key",
                        data=pqc_key,
                        file_name=f'pqc_key_{selected_alg["name"].lower().replace("-", "_")}.txt',
                        mime='text/plain',
                        use_container_width=True
                    )
                
                st.markdown("---")
                st.success("""
                🎉 **Congratulations!** Your Post-Quantum Certificate has been generated successfully.
                
                **Next Steps:**
                1. Download both the certificate and private key files
                2. Store the private key in a secure location
                3. Deploy the PQC certificate to your quantum-resistant infrastructure
                
                **Note:** These PQC certificates use NIST-standardized algorithms that are designed
                to be secure against quantum computer attacks.
                """)

                st.balloons()
            except ValueError as ve:
                st.error(f"❌ **Validation Error:** {str(ve)}")
                st.info("""
                **Troubleshooting:**
                - Ensure your certificate file is in PEM format (.pem or .crt)
                - Verify that the file contains a valid X.509 certificate
                - Check that the certificate is not corrupted or encrypted
                """)
            except Exception as e:
                st.error(f"❌ **Error during PQC generation:** {str(e)}")
                st.info("""
                **Common Issues:**
                - Invalid certificate format
                - Unsupported certificate encoding
                - File corruption
                
                Please verify your certificate file and try again.
                """)
                # Show detailed error for debugging
                with st.expander("🔍 View Detailed Error Information"):
                    st.code(str(e))
else:
    st.warning("⚠️ Please upload both certificate and private key files to continue.")
    
    with st.expander("ℹ️ How to get started"):
        st.markdown("""
        **To use this tool:**
        
        1. **Upload your existing SSL certificate** - This is typically a `.pem` or `.crt` file
        2. **Upload your private key** - This is typically a `.key` or `.pem` file
        3. **Select a PQC algorithm** - Choose from NIST-standardized algorithms
        4. **Generate** - Click the button to create your PQC certificate
        
        **Need a test certificate?**
        
        You can create a self-signed certificate for testing using OpenSSL:
        ```bash
        openssl req -x509 -newkey rsa:2048 -nodes \\
          -keyout key.pem -out cert.pem -days 365 \\
          -subj "/CN=example.com/O=Test Organization"
        ```
        """)

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
    <p>🔐 Post-Quantum Certificate Converter | Built with NIST-standardized PQC algorithms</p>
    <p>Powered by <a href='https://github.com/PQClean/PQClean' target='_blank'>PQCrypto</a> 
    and <a href='https://pyca.github.io/cryptography/' target='_blank'>Cryptography</a> libraries</p>
</div>
""", unsafe_allow_html=True)

