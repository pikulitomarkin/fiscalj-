#!/usr/bin/env python3
"""
Script para verificar informações do certificado digital
"""
from pathlib import Path
from cryptography import x509
from cryptography.hazmat.backends import default_backend
import re

cert_path = Path("certificados/cert.pem")

if not cert_path.exists():
    print(f"❌ Certificado não encontrado: {cert_path}")
    exit(1)

print("🔍 Verificando certificado digital...\n")

with open(cert_path, 'rb') as f:
    cert_data = f.read()
    cert = x509.load_pem_x509_certificate(cert_data, default_backend())

# Extrair informações
subject = cert.subject
issuer = cert.issuer

print("📋 INFORMAÇÕES DO CERTIFICADO:")
print("="*60)

# Subject (Titular)
print("\n👤 TITULAR (Subject):")
for attr in subject:
    print(f"   {attr.oid._name}: {attr.value}")

# Extrair CNPJ do subject
subject_str = subject.rfc4514_string()
print(f"\n📄 Subject completo: {subject_str}")

# Procurar CNPJ no subject
cnpj_match = re.search(r'(\d{14})', subject_str)
if cnpj_match:
    cnpj = cnpj_match.group(1)
    print(f"\n🆔 CNPJ encontrado: {cnpj}")
    print(f"   Formatado: {cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:14]}")
else:
    print("\n⚠️ CNPJ não encontrado no certificado")

# Emissor
print("\n🏛️ EMISSOR (Issuer):")
for attr in issuer:
    print(f"   {attr.oid._name}: {attr.value}")

# Validade
print(f"\n📅 VALIDADE:")
print(f"   Válido de: {cert.not_valid_before_utc}")
print(f"   Válido até: {cert.not_valid_after_utc}")

# Verificar se está válido
from datetime import datetime, timezone
now = datetime.now(timezone.utc)
if cert.not_valid_before_utc <= now <= cert.not_valid_after_utc:
    print(f"   ✅ Certificado VÁLIDO")
else:
    print(f"   ❌ Certificado EXPIRADO ou ainda não válido")

# Serial Number
print(f"\n🔢 Número de Série: {cert.serial_number}")

# Key Usage
try:
    key_usage = cert.extensions.get_extension_for_oid(x509.oid.ExtensionOID.KEY_USAGE)
    print(f"\n🔑 Uso da Chave:")
    print(f"   Digital Signature: {key_usage.value.digital_signature}")
    print(f"   Key Encipherment: {key_usage.value.key_encipherment}")
except:
    print("\n🔑 Uso da Chave: Não especificado")

print("\n" + "="*60)
print("✅ Verificação concluída!")
