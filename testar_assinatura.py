#!/usr/bin/env python3
"""
Script para testar assinatura XML e validar
"""
from pathlib import Path
from lxml import etree
from src.utils.xml_generator import NFSeXMLGenerator
from src.models.schemas import NFSeRequest, PrestadorServico, TomadorServico, Servico, TipoAmbiente
from datetime import datetime

print("🧪 TESTE DE ASSINATURA XML\n")
print("="*60)

# Criar dados de teste
prestador = PrestadorServico(
    cnpj="58645846000169",
    inscricao_municipal="93442",
    razao_social="VSB SERVICOS MEDICOS LTDA",
    nome_fantasia="VSB",
    logradouro="Rua Exemplo",
    numero="123",
    bairro="Centro",
    municipio="Porto Alegre",
    uf="RS",
    cep="90000000"
)

tomador = TomadorServico(
    cpf_cnpj="12345678901",
    nome_razao_social="Tomador Teste",
    logradouro="Rua Teste",
    numero="456",
    bairro="Bairro Teste",
    municipio="Porto Alegre",
    uf="RS",
    cep="90000000"
)

servico = Servico(
    discriminacao="Consulta médica",
    valor_servicos=100.00,
    valor_liquido=100.00,
    item_lista_servico="0101",
    codigo_tributacao_municipio="010101"
)

nfse_request = NFSeRequest(
    prestador=prestador,
    tomador=tomador,
    servico=servico
)

# Criar gerador
gerador = NFSeXMLGenerator(
    ambiente=TipoAmbiente.PRODUCAO,
    cert_path="certificados/cert.pem",
    key_path="certificados/key.pem"
)

print("\n1️⃣ Gerando XML sem assinatura...")
xml_sem_assinatura = gerador.gerar_xml_nfse(nfse_request)
print(f"   ✅ Gerado: {len(xml_sem_assinatura)} bytes")

# Salvar para análise
Path("xml_sem_assinatura.xml").write_text(xml_sem_assinatura, encoding='utf-8')
print(f"   💾 Salvo em: xml_sem_assinatura.xml")

print("\n2️⃣ Assinando XML...")
try:
    xml_assinado = gerador.assinar_xml(xml_sem_assinatura)
    print(f"   ✅ Assinado: {len(xml_assinado)} bytes")
    
    # Salvar para análise
    Path("xml_assinado.xml").write_text(xml_assinado, encoding='utf-8')
    print(f"   💾 Salvo em: xml_assinado.xml")
    
    # Verificar estrutura
    print("\n3️⃣ Verificando estrutura do XML assinado...")
    root = etree.fromstring(xml_assinado.encode('utf-8'))
    
    # Procurar elemento Signature
    ns = {'ds': 'http://www.w3.org/2000/09/xmldsig#', 'nfse': 'http://www.sped.fazenda.gov.br/nfse'}
    signature = root.find('.//ds:Signature', ns)
    
    if signature is not None:
        print("   ✅ Elemento <Signature> encontrado")
        
        # Verificar SignedInfo
        signed_info = signature.find('.//ds:SignedInfo', ns)
        if signed_info is not None:
            print("   ✅ Elemento <SignedInfo> encontrado")
            
            # Verificar Reference
            reference = signed_info.find('.//ds:Reference', ns)
            if reference is not None:
                uri = reference.get('URI')
                print(f"   ✅ Elemento <Reference> encontrado com URI: {uri}")
            else:
                print("   ❌ Elemento <Reference> NÃO encontrado")
        else:
            print("   ❌ Elemento <SignedInfo> NÃO encontrado")
        
        # Verificar KeyInfo
        key_info = signature.find('.//ds:KeyInfo', ns)
        if key_info is not None:
            print("   ✅ Elemento <KeyInfo> encontrado")
            
            # Verificar X509Certificate
            x509_cert = key_info.find('.//ds:X509Certificate', ns)
            if x509_cert is not None:
                cert_text = x509_cert.text
                print(f"   ✅ Certificado X509 incluído ({len(cert_text) if cert_text else 0} chars)")
                
                # Extrair CNPJ do certificado
                if cert_text:
                    import base64
                    from cryptography import x509
                    from cryptography.hazmat.backends import default_backend
                    
                    cert_bytes = base64.b64decode(cert_text)
                    cert = x509.load_der_x509_certificate(cert_bytes, default_backend())
                    subject = cert.subject.rfc4514_string()
                    
                    import re
                    cnpj_match = re.search(r'(\d{14})', subject)
                    if cnpj_match:
                        cnpj_cert = cnpj_match.group(1)
                        cnpj_dps = prestador.cnpj
                        
                        print(f"   📄 CNPJ no certificado: {cnpj_cert}")
                        print(f"   📄 CNPJ no DPS: {cnpj_dps}")
                        
                        if cnpj_cert == cnpj_dps:
                            print("   ✅ CNPJ DO CERTIFICADO CORRESPONDE AO DPS!")
                        else:
                            print("   ❌ CNPJ DO CERTIFICADO NÃO CORRESPONDE AO DPS!")
            else:
                print("   ❌ Certificado X509 NÃO encontrado")
        else:
            print("   ❌ Elemento <KeyInfo> NÃO encontrado")
    else:
        print("   ❌ Elemento <Signature> NÃO encontrado - XML não está assinado!")
    
    print("\n" + "="*60)
    print("✅ TESTE CONCLUÍDO!")
    
except Exception as e:
    print(f"   ❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
