#!/usr/bin/env python3
"""
Teste simplificado de geração de XML (sem assinatura)
"""
import sys
from pathlib import Path

# Adiciona diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.xml_generator import NFSeXMLGenerator
from src.models.schemas import (
    NFSeRequest, PrestadorServico, TomadorServico, 
    Servico, TipoAmbiente
)

print("🧪 TESTE DE GERAÇÃO DE XML DPS\n")
print("="*60)

# Criar dados de teste com o CNPJ correto
prestador = PrestadorServico(
    cnpj="58645846000169",  # VSB SERVICOS MEDICOS LTDA
    inscricao_municipal="8259069",
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
    nome="João da Silva",
    nome_razao_social="João da Silva",
    logradouro="Rua Teste",
    numero="456",
    bairro="Bairro Teste",
    municipio="Porto Alegre",
    uf="RS",
    cep="90000000"
)

servico = Servico(
    descricao="Consulta médica",
    valor_servico=100.00,
    aliquota_iss=2.5,
    item_lista_servico="0101",
    codigo_tributacao_municipio="010101",
    discriminacao="Consulta médica de rotina"
)

nfse_request = NFSeRequest(
    prestador=prestador,
    tomador=tomador,
    servico=servico
)

# Criar gerador SEM certificado (apenas para testar estrutura)
print("\n1️⃣ Criando gerador XML...")
gerador = NFSeXMLGenerator(ambiente=TipoAmbiente.PRODUCAO)
print("   ✅ Gerador criado")

# Gerar XML
print("\n2️⃣ Gerando XML DPS...")
try:
    xml = gerador.gerar_xml_nfse(nfse_request)
    print(f"   ✅ XML gerado: {len(xml)} bytes")
    
    # Salvar para análise
    Path("xml_teste.xml").write_text(xml, encoding='utf-8')
    print(f"   💾 Salvo em: xml_teste.xml")
    
    # Análise básica
    print("\n3️⃣ Analisando estrutura do XML...")
    
    # Verificar elementos principais
    checks = [
        ('<?xml version', 'Declaração XML'),
        ('<DPS', 'Elemento raiz DPS'),
        ('xmlns="http://www.sped.fazenda.gov.br/nfse"', 'Namespace'),
        ('versao="1.01"', 'Versão'),
        ('<infDPS', 'Elemento infDPS'),
        ('Id="DPS', 'Atributo Id'),
        ('<tpAmb>', 'Tipo de Ambiente'),
        ('<dhEmi>', 'Data/Hora Emissão'),
        ('<prest>', 'Prestador'),
        ('<CNPJ>58645846000169</CNPJ>', 'CNPJ Prestador (VSB)'),
        ('<xNome>VSB SERVICOS MEDICOS LTDA</xNome>', 'Razão Social VSB'),
        ('<tom>', 'Tomador'),
        ('<serv>', 'Serviço')
    ]
    
    all_ok = True
    for check_str, description in checks:
        if check_str in xml:
            print(f"   ✅ {description}")
        else:
            print(f"   ❌ {description} - NÃO ENCONTRADO")
            all_ok = False
    
    # Extrair ID do DPS
    import re
    id_match = re.search(r'Id="(DPS[^"]+)"', xml)
    if id_match:
        id_dps = id_match.group(1)
        print(f"\n📋 ID do DPS: {id_dps}")
        
        # Verificar se CNPJ está no ID
        if '58645846000169' in id_dps:
            print(f"   ✅ CNPJ correto no ID do DPS")
        else:
            print(f"   ❌ CNPJ incorreto no ID do DPS")
            all_ok = False
    
    # Mostrar primeiras linhas do XML
    print("\n📄 Primeiras linhas do XML:")
    print("-"*60)
    for i, line in enumerate(xml.split('\n')[:15], 1):
        print(f"{i:2d}: {line}")
    print("-"*60)
    
    if all_ok:
        print("\n✅ ESTRUTURA DO XML ESTÁ CORRETA!")
        print("\n⚠️ PRÓXIMO PASSO:")
        print("   Configure os certificados para testar assinatura:")
        print("   - certificados/cert.pem")
        print("   - certificados/key.pem")
    else:
        print("\n❌ PROBLEMAS ENCONTRADOS NA ESTRUTURA DO XML")
    
except Exception as e:
    print(f"   ❌ ERRO: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("✅ TESTE CONCLUÍDO")
