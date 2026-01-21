#!/usr/bin/env python3
"""
Script para converter certificado .pfx/.p12 para cert.pem e key.pem
"""
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from pathlib import Path
import getpass

def converter_certificado():
    """Converte certificado PFX/P12 para PEM."""
    print("🔐 Conversor de Certificado Digital")
    print("="*60)
    
    # Solicitar caminho do arquivo
    pfx_path = input("\n📁 Caminho do certificado (.pfx ou .p12): ").strip()
    
    if not Path(pfx_path).exists():
        print(f"❌ Arquivo não encontrado: {pfx_path}")
        return False
    
    # Solicitar senha
    senha = getpass.getpass("🔑 Senha do certificado: ")
    
    try:
        print("\n⏳ Processando certificado...")
        
        # Ler arquivo PFX/P12
        with open(pfx_path, 'rb') as f:
            pfx_data = f.read()
        
        # Importar certificado
        from cryptography.hazmat.primitives.serialization import pkcs12
        
        private_key, certificate, additional_certs = pkcs12.load_key_and_certificates(
            pfx_data,
            senha.encode() if senha else None,
            default_backend()
        )
        
        if not private_key or not certificate:
            print("❌ Não foi possível extrair chave privada ou certificado")
            return False
        
        # Criar pasta certificados se não existir
        cert_dir = Path("certificados")
        cert_dir.mkdir(exist_ok=True)
        
        # Salvar chave privada (key.pem)
        key_path = cert_dir / "key.pem"
        with open(key_path, 'wb') as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))
        print(f"✅ Chave privada salva: {key_path}")
        
        # Salvar certificado (cert.pem)
        cert_path = cert_dir / "cert.pem"
        with open(cert_path, 'wb') as f:
            f.write(certificate.public_bytes(serialization.Encoding.PEM))
        print(f"✅ Certificado salvo: {cert_path}")
        
        # Informações do certificado
        print(f"\n📋 Informações do Certificado:")
        print(f"   Titular: {certificate.subject.rfc4514_string()}")
        print(f"   Emissor: {certificate.issuer.rfc4514_string()}")
        print(f"   Validade: {certificate.not_valid_before} até {certificate.not_valid_after}")
        
        # Gerar Base64 para Railway
        print(f"\n🚀 Gerando Base64 para Railway...")
        import base64
        
        cert_b64 = base64.b64encode(cert_path.read_bytes()).decode('ascii')
        key_b64 = base64.b64encode(key_path.read_bytes()).decode('ascii')
        
        # Salvar em arquivos
        Path("cert_b64_railway.txt").write_text(cert_b64)
        Path("key_b64_railway.txt").write_text(key_b64)
        
        print(f"✅ Base64 salvo em:")
        print(f"   - cert_b64_railway.txt ({len(cert_b64)} chars)")
        print(f"   - key_b64_railway.txt ({len(key_b64)} chars)")
        
        print(f"\n📋 Configure no Railway:")
        print(f"   CERTIFICATE_CERT_PEM = conteúdo de cert_b64_railway.txt")
        print(f"   CERTIFICATE_KEY_PEM = conteúdo de key_b64_railway.txt")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao processar certificado: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n⚠️  IMPORTANTE:")
    print("   1. Você precisa de um certificado digital válido (.pfx ou .p12)")
    print("   2. Este script irá gerar cert.pem e key.pem")
    print("   3. Também gerará os Base64 para configurar no Railway")
    print()
    
    converter_certificado()
    
    print("\n" + "="*60)
    print("✅ Processo concluído!")
    print("="*60)
