"""
Script para converter certificado .pfx para .pem
VSB Serviços Médicos LTDA
"""
import sys
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import pkcs12

def converter_certificado():
    """Converte certificado .pfx para .pem"""
    
    print("\n" + "="*60)
    print("  Conversão de Certificado Digital - VSB")
    print("="*60 + "\n")
    
    # Caminhos
    pfx_path = r"c:\Users\marco\Downloads\VSBSERVICOSMEDICOSLTDA_58645846000169.pfx"
    cert_path = r"c:\Users\marco\Downloads\vsbcert.pem"
    key_path = r"c:\Users\marco\Downloads\vsbkey.pem"
    
    # Senha do certificado
    password = b"KLP4klp4"
    
    # Verificar se o certificado existe
    if not Path(pfx_path).exists():
        print(f"❌ Certificado não encontrado em: {pfx_path}")
        return False
    
    print(f"📄 Certificado encontrado: {pfx_path}\n")
    
    try:
        # Ler o arquivo .pfx
        print("🔄 Lendo certificado .pfx...")
        with open(pfx_path, 'rb') as f:
            pfx_data = f.read()
        
        # Carregar PKCS12
        print("🔄 Extraindo dados do certificado...")
        private_key, certificate, additional_certs = pkcs12.load_key_and_certificates(
            pfx_data, 
            password,
            backend=default_backend()
        )
        
        # Extrair certificado (parte pública)
        print("🔄 Salvando certificado público...")
        cert_pem = certificate.public_bytes(serialization.Encoding.PEM)
        
        with open(cert_path, 'wb') as f:
            f.write(cert_pem)
        
        print(f"✅ Certificado extraído: {cert_path}")
        
        # Extrair chave privada
        print("🔄 Salvando chave privada...")
        key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        with open(key_path, 'wb') as f:
            f.write(key_pem)
        
        print(f"✅ Chave privada extraída: {key_path}")
        
        print("\n" + "="*60)
        print("  ✅ Conversão concluída com sucesso!")
        print("="*60 + "\n")
        
        print("Arquivos gerados:")
        print(f"  📄 Certificado: {cert_path}")
        print(f"  🔑 Chave privada: {key_path}\n")
        
        print("⚠️  IMPORTANTE:")
        print("  - Mantenha estes arquivos em local seguro")
        print("  - Nunca compartilhe a chave privada")
        print("  - A senha já está configurada no .env\n")
        
        print("Próximos passos:")
        print("  1. Execute: pip install -r requirements.txt")
        print("  2. Execute: streamlit run app_nfse_enhanced.py")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao converter certificado: {e}")
        print("\nVerifique se:")
        print("  - A senha do certificado está correta")
        print("  - O arquivo .pfx não está corrompido")
        print("  - Você tem as bibliotecas necessárias instaladas:")
        print("    pip install cryptography pyOpenSSL")
        return False

if __name__ == "__main__":
    sucesso = converter_certificado()
    sys.exit(0 if sucesso else 1)
